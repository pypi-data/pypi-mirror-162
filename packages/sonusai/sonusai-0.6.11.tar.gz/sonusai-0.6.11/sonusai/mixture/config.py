from typing import Dict
from typing import List
from typing import Union

from sonusai.mixture.mixdb import NoiseFiles
from sonusai.mixture.mixdb import TargetFiles


def raw_load_config(name: str) -> dict:
    """Load YAML file with SonusAI variable substitution."""
    import yaml

    with open(file=name, mode='r') as f:
        config = yaml.safe_load(f)

    return config_variable_substitution(config)


def config_variable_substitution(config: dict) -> dict:
    """Find custom SonusAI variables in given dictionary and substitute their values in place."""
    import json

    from sonusai.mixture.constants import DEFAULT_FRAME_SIZE

    result = json.dumps(config)
    result = result.replace('"${frame_size}"', str(DEFAULT_FRAME_SIZE))
    config = json.loads(result)
    return config


def get_default_config() -> dict:
    """Load default SonusAI config."""
    import json

    import sonusai
    from sonusai import SonusAIError

    try:
        return raw_load_config(sonusai.mixture.DEFAULT_CONFIG)
    except Exception as e:
        raise SonusAIError(f'Error loading default config: {e}')


def load_config(name: str) -> dict:
    """Load SonusAI default config and update with given YAML file (performing SonusAI variable substitution)."""
    return update_config_from_file(name=name, config=get_default_config())


def update_config_from_file(name: str, config: dict) -> dict:
    """Update the given config with the config in the given YAML file."""
    from copy import deepcopy

    from sonusai import SonusAIError

    new_config = deepcopy(config)

    try:
        given_config = raw_load_config(name)
    except Exception as e:
        raise SonusAIError(f'Error loading config from {name}: {e}')

    # Use default config as base and overwrite with given config keys as found
    for key in new_config:
        if key in given_config:
            if key not in ['truth_settings']:
                new_config[key] = given_config[key]

    # Handle 'truth_settings' special case
    if 'truth_settings' in given_config:
        new_config['truth_settings'] = deepcopy(given_config['truth_settings'])

    if not isinstance(new_config['truth_settings'], list):
        new_config['truth_settings'] = [new_config['truth_settings']]

    default = deepcopy(config['truth_settings'])
    if not isinstance(default, list):
        default = [default]

    new_config['truth_settings'] = update_truth_settings(new_config['truth_settings'], default)

    # Check for required keys
    required_keys = [
        'class_balancing',
        'class_balancing_augmentation',
        'class_labels',
        'class_weights_threshold',
        'exhaustive_noise',
        'feature',
        'frame_size',
        'noise_augmentations',
        'noises',
        'num_classes',
        'seed',
        'snrs',
        'target_augmentations',
        'targets',
        'truth_mode',
        'truth_reduction_function',
        'truth_settings',
    ]
    for key in required_keys:
        if key not in new_config:
            raise SonusAIError(f"Missing required '{key}' in {name}")

    return new_config


def update_truth_settings(given: Union[List[Dict], Dict], default: List[Dict] = None) -> List[Dict]:
    """Update missing fields in given 'truth_settings' with default values."""
    from copy import deepcopy

    from sonusai import SonusAIError

    truth_settings = deepcopy(given)
    if not isinstance(truth_settings, list):
        truth_settings = [truth_settings]

    if default is not None and len(truth_settings) != len(default):
        raise SonusAIError(f'Length of given does not match default')

    required_keys = [
        'function',
        'config',
        'index',
    ]
    for n in range(len(truth_settings)):
        for key in required_keys:
            if key not in truth_settings[n]:
                if default is not None and key in default[n]:
                    truth_settings[n][key] = default[n][key]
                else:
                    raise SonusAIError(f"Missing required '{key}' in truth_settings")

    for truth_setting in truth_settings:
        if not isinstance(truth_setting['index'], list):
            truth_setting['index'] = [truth_setting['index']]

    return truth_settings


def get_hierarchical_config_files(root: str, leaf: str) -> list:
    """Get a hierarchical list of config files in the given leaf of the given root."""
    from sonusai import SonusAIError
    import os
    from pathlib import Path

    config_file = 'config.yml'

    root_path = Path(os.path.abspath(root))
    if not root_path.is_dir():
        raise SonusAIError(f'Given root, {root_path}, is not a directory.')

    leaf_path = Path(os.path.abspath(leaf))
    if not leaf_path.is_dir():
        raise SonusAIError(f'Given leaf, {leaf_path}, is not a directory.')

    common = os.path.commonpath((root_path, leaf_path))
    if os.path.normpath(common) != os.path.normpath(root_path):
        raise SonusAIError(f'Given leaf, {leaf_path}, is not in the hierarchy of the given root, {root_path}')

    top_config_file = Path(os.path.join(root_path, config_file))
    if not top_config_file.is_file():
        raise SonusAIError(f'Could not find {top_config_file}')

    current = leaf_path
    config_files = list()
    while current != root_path:
        local_config_file = Path(os.path.join(current, config_file))
        if local_config_file.is_file():
            config_files.append(local_config_file)
        current = current.parent

    config_files.append(top_config_file)
    return list(reversed(config_files))


def update_config_from_hierarchy(root: str, leaf: str, config: dict) -> dict:
    """Update the given config using the hierarchical config files in the given leaf of the given root."""
    from copy import deepcopy

    new_config = deepcopy(config)
    config_files = get_hierarchical_config_files(root=root, leaf=leaf)
    for config_file in config_files:
        new_config = update_config_from_file(name=config_file, config=new_config)

    return new_config


def get_max_class(num_classes: int, truth_mutex: bool) -> int:
    """Get the maximum class index."""
    max_class = num_classes
    if truth_mutex:
        max_class -= 1
    return max_class


def get_target_files(config: dict) -> TargetFiles:
    from sonusai import SonusAIError
    from sonusai.utils.dataclass_from_dict import dataclass_from_dict

    truth_settings = config.get('truth_settings', list())
    target_files = list()
    for target_file in config['targets']:
        append_target_files(target_files, target_file, truth_settings)

    max_class = get_max_class(config['num_classes'], config['truth_mode'] == 'mutex')

    for target_file in target_files:
        target_file['truth_settings'] = update_truth_settings(target_file['truth_settings'], config['truth_settings'])

        for truth_setting in target_file['truth_settings']:
            if any(idx > max_class for idx in truth_setting['index']):
                raise SonusAIError('invalid truth index')

    return dataclass_from_dict(TargetFiles, target_files)


def append_target_files(target_files: List[dict],
                        target_file: Union[dict, str],
                        truth_settings: List[dict],
                        tokens: Union[dict, None] = None) -> None:
    from glob import glob
    from os import listdir
    from os.path import dirname
    from os.path import isabs
    from os.path import isdir
    from os.path import join
    from os.path import splitext

    import sox

    from sonusai import SonusAIError

    if tokens is None:
        tokens = dict()

    if isinstance(target_file, dict):
        if 'name' in target_file:
            in_name = target_file['name']
        else:
            raise SonusAIError('Target list contained record without name')

        if 'truth_settings' in target_file:
            truth_settings = target_file['truth_settings']
    else:
        in_name = target_file

    in_name, new_tokens = tokenized_expandvars(in_name)
    tokens.update(new_tokens)
    names = glob(in_name)
    if not names:
        raise SonusAIError(f'Could not find {in_name}. Make sure path exists')
    for name in names:
        ext = splitext(name)[1].lower()
        dir_name = dirname(name)
        if isdir(name):
            for file in listdir(name):
                child = file
                if not isabs(child):
                    child = join(dir_name, child)
                append_target_files(target_files, child, truth_settings, tokens)
        else:
            try:
                if ext == '.txt':
                    with open(file=name, mode='r') as txt_file:
                        for line in txt_file:
                            # strip comments
                            child = line.partition('#')[0]
                            child = child.rstrip()
                            if child:
                                child, new_tokens = tokenized_expandvars(child)
                                tokens.update(new_tokens)
                                if not isabs(child):
                                    child = join(dir_name, child)
                                append_target_files(target_files, child, truth_settings, tokens)
                elif ext == '.yml':
                    try:
                        yml_config = raw_load_config(name)

                        if 'targets' in yml_config:
                            for record in yml_config['targets']:
                                append_target_files(target_files, record, truth_settings, tokens)
                    except Exception as e:
                        raise SonusAIError(f'Error processing {name}: {e}')
                else:
                    sox.file_info.validate_input_file(name)
                    duration = sox.file_info.duration(name)
                    for key, value in tokens.items():
                        name = name.replace(value, f'${key}')
                    entry = {
                        'name':     name,
                        'duration': duration,
                    }
                    if len(truth_settings) > 0:
                        entry['truth_settings'] = truth_settings
                        for truth_setting in entry['truth_settings']:
                            if 'function' in truth_setting and truth_setting['function'] == 'file':
                                truth_setting['config']['file'] = splitext(name)[0] + '.h5'
                    target_files.append(entry)
            except SonusAIError:
                raise
            except Exception as e:
                raise SonusAIError(f'Error processing {name}: {e}')


def get_noise_files(config: dict) -> NoiseFiles:
    from sonusai.mixture.mixdb import NoiseFiles
    from sonusai.utils.dataclass_from_dict import dataclass_from_dict

    noise_files = list()
    for noise_file in config['noises']:
        append_noise_files(noise_files, noise_file)

    return dataclass_from_dict(NoiseFiles, noise_files)


def append_noise_files(noise_files: List[dict],
                       noise_file: Union[dict, str],
                       tokens: Union[dict, None] = None) -> None:
    from glob import glob
    from os import listdir
    from os.path import dirname
    from os.path import isabs
    from os.path import isdir
    from os.path import join
    from os.path import splitext

    import sox

    from sonusai import SonusAIError

    if tokens is None:
        tokens = dict()

    if isinstance(noise_file, dict):
        if 'name' in noise_file:
            in_name = noise_file['name']
        else:
            raise SonusAIError('Noise list contained record without name')
    else:
        in_name = noise_file

    in_name, new_tokens = tokenized_expandvars(in_name)
    tokens.update(new_tokens)
    names = glob(in_name)
    if not names:
        raise SonusAIError(f'Could not find {in_name}. Make sure path exists')
    for name in names:
        ext = splitext(name)[1].lower()
        dir_name = dirname(name)
        if isdir(name):
            for file in listdir(name):
                child = file
                if not isabs(child):
                    child = join(dir_name, child)
                append_noise_files(noise_files, child, tokens)
        else:
            try:
                if ext == '.txt':
                    with open(file=name, mode='r') as txt_file:
                        for line in txt_file:
                            # strip comments
                            child = line.partition('#')[0]
                            child = child.rstrip()
                            if child:
                                child, new_tokens = tokenized_expandvars(child)
                                tokens.update(new_tokens)
                                if not isabs(child):
                                    child = join(dir_name, child)
                                append_noise_files(noise_files, child, tokens)
                elif ext == '.yml':
                    try:
                        yml_config = raw_load_config(name)

                        if 'noises' in yml_config:
                            for record in yml_config['noises']:
                                append_noise_files(noise_files, record, tokens)
                    except Exception as e:
                        raise SonusAIError(f'Error processing {name}: {e}')
                else:
                    sox.file_info.validate_input_file(name)
                    duration = sox.file_info.duration(name)
                    for key, value in tokens.items():
                        name = name.replace(value, f'${key}')
                    entry = {
                        'name':     name,
                        'duration': duration,
                    }
                    noise_files.append(entry)
            except SonusAIError:
                raise
            except Exception as e:
                raise SonusAIError(f'Error processing {name}: {e}')


def tokenized_expandvars(path: str) -> (str, dict):
    """Expand shell variables of the forms $var, ${var} and %var%.
    Unknown variables are left unchanged."""

    # Expand paths containing shell variable substitutions.
    # The following rules apply:
    #       - no expansion within single quotes
    #       - '$$' is translated into '$'
    #       - '%%' is translated into '%' if '%%' are not seen in %var1%%var2%
    #       - ${varname} is accepted.
    #       - $varname is accepted.
    #       - %varname% is accepted.
    #       - varnames can be made out of letters, digits and the characters '_-'
    #         (though is not verified in the ${varname} and %varname% cases)
    # XXX With COMMAND.COM you can use any characters in a variable name,
    # XXX except '^|<>='.
    import os
    import string

    from sonusai.mixture.constants import DEFAULT_NOISE

    os.environ['default_noise'] = DEFAULT_NOISE

    path = os.fspath(path)
    token_map = {}
    if isinstance(path, bytes):
        if b'$' not in path and b'%' not in path:
            return path, token_map
        varchars = bytes(string.ascii_letters + string.digits + '_-', 'ascii')
        quote = b'\''
        percent = b'%'
        brace = b'{'
        rbrace = b'}'
        dollar = b'$'
        environ = getattr(os, 'environb', None)
    else:
        if '$' not in path and '%' not in path:
            return path, token_map
        varchars = string.ascii_letters + string.digits + '_-'
        quote = '\''
        percent = '%'
        brace = '{'
        rbrace = '}'
        dollar = '$'
        environ = os.environ
    res = path[:0]
    index = 0
    pathlen = len(path)
    while index < pathlen:
        c = path[index:index + 1]
        if c == quote:  # no expansion within single quotes
            path = path[index + 1:]
            pathlen = len(path)
            try:
                index = path.index(c)
                res += c + path[:index + 1]
            except ValueError:
                res += c + path
                index = pathlen - 1
        elif c == percent:  # variable or '%'
            if path[index + 1:index + 2] == percent:
                res += c
                index += 1
            else:
                path = path[index + 1:]
                pathlen = len(path)
                try:
                    index = path.index(percent)
                except ValueError:
                    res += percent + path
                    index = pathlen - 1
                else:
                    var = path[:index]
                    try:
                        if environ is None:
                            value = os.fsencode(os.environ[os.fsdecode(var)])
                        else:
                            value = environ[var]
                        token_map[var] = value
                    except KeyError:
                        value = percent + var + percent
                    res += value
        elif c == dollar:  # variable or '$$'
            if path[index + 1:index + 2] == dollar:
                res += c
                index += 1
            elif path[index + 1:index + 2] == brace:
                path = path[index + 2:]
                pathlen = len(path)
                try:
                    index = path.index(rbrace)
                except ValueError:
                    res += dollar + brace + path
                    index = pathlen - 1
                else:
                    var = path[:index]
                    try:
                        if environ is None:
                            value = os.fsencode(os.environ[os.fsdecode(var)])
                        else:
                            value = environ[var]
                        token_map[var] = value
                    except KeyError:
                        value = dollar + brace + var + rbrace
                    res += value
            else:
                var = path[:0]
                index += 1
                c = path[index:index + 1]
                while c and c in varchars:
                    var += c
                    index += 1
                    c = path[index:index + 1]
                try:
                    if environ is None:
                        value = os.fsencode(os.environ[os.fsdecode(var)])
                    else:
                        value = environ[var]
                    token_map[var] = value
                except KeyError:
                    value = dollar + var
                res += value
                if c:
                    index -= 1
        else:
            res += c
        index += 1
    return res, token_map
