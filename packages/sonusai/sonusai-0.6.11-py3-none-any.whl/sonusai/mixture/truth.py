from typing import List

import numpy as np

from sonusai.mixture.mixdb import Mixture
from sonusai.mixture.mixdb import MixtureDatabase


def _strictly_decreasing(list_to_check: list) -> bool:
    return all(x > y for x, y in zip(list_to_check, list_to_check[1:]))


def generate_truth(mixdb: MixtureDatabase,
                   mixture: Mixture,
                   target_audio: List[np.ndarray],
                   compute: bool = True) -> np.ndarray:
    from sonusai import SonusAIError

    if not compute:
        return np.empty(0, dtype=np.single)

    if len(target_audio) != len(mixture.target_file_index):
        raise SonusAIError('Number of target audio entries does not match number of target file indices')

    truth = np.zeros((mixture.samples, mixdb.num_classes), dtype=np.single)
    for idx in range(len(target_audio)):
        for truth_setting in mixdb.targets[mixture.target_file_index[idx]].truth_settings:
            target_gain = mixture.target_gain[idx]
            if mixture.target_snr_gain is not None:
                target_gain *= mixture.target_snr_gain

            config = {
                'index':       truth_setting.index,
                'function':    truth_setting.function,
                'config':      truth_setting.config,
                'frame_size':  mixdb.frame_size,
                'num_classes': mixdb.num_classes,
                'mutex':       mixdb.truth_mutex,
                'target_gain': target_gain,
            }
            truth += truth_function(audio=target_audio[idx], config=config)

    return truth


def truth_function(audio: np.ndarray, config: dict) -> np.ndarray:
    import h5py
    from pyaaware import ForwardTransform
    from pyaaware import SED

    from sonusai import SonusAIError
    from sonusai.utils.int16_to_float import int16_to_float

    truth = np.zeros((len(audio), config['num_classes']), dtype=np.single)

    if config['function'] == 'sed':
        if len(audio) % config['frame_size'] != 0:
            raise SonusAIError(f'Number of samples in audio is not a multiple of {config["frame_size"]}')

        if 'config' not in config:
            raise SonusAIError('Truth function SED missing config')

        parameters = ['thresholds']
        for parameter in parameters:
            if parameter not in config['config']:
                raise SonusAIError(f'Truth function SED config missing required parameter: {parameter}')

        thresholds = config['config']['thresholds']
        if not _strictly_decreasing(thresholds):
            raise SonusAIError(f'Truth function SED thresholds are not strictly decreasing: {thresholds}')

        if config['target_gain'] == 0:
            return truth

        fft = ForwardTransform(N=config['frame_size'] * 4, R=config['frame_size'])
        sed = SED(thresholds=thresholds,
                  index=config['index'],
                  frame_size=config['frame_size'],
                  num_classes=config['num_classes'],
                  mutex=config['mutex'])

        audio = np.int16(np.single(audio) / config['target_gain'])
        for offset in range(0, len(audio), config['frame_size']):
            indices = slice(offset, offset + config['frame_size'])
            new_truth = sed.execute(fft.energy_t(int16_to_float(audio[indices])))
            truth[indices] = np.reshape(new_truth, (1, len(new_truth)))

        return truth

    elif config['function'] == 'file':
        if 'config' not in config:
            raise SonusAIError('Truth function file missing config')

        parameters = ['file']
        for parameter in parameters:
            if parameter not in config['config']:
                raise SonusAIError(f'Truth function file config missing required parameter: {parameter}')

        with h5py.File(name=config['config']['file'], mode='r') as f:
            truth_in = np.array(f['/truth_t'])

        if truth_in.ndim != 2:
            raise SonusAIError('Truth file data is not 2 dimensions')

        if truth_in.shape[0] != len(audio):
            raise SonusAIError('Truth file does not contain the right amount of samples')

        if config['target_gain'] == 0:
            return truth

        if isinstance(config['index'], list):
            if len(config['index']) != truth_in.shape[1]:
                raise SonusAIError('Truth file does not contain the right amount of classes')

            truth[:, config['index']] = truth_in
        else:
            if config['index'] + truth_in.shape[1] > config['num_classes']:
                raise SonusAIError('Truth file contains too many classes')

            truth[:, config['index']:config['index'] + truth_in.shape[1]] = truth_in

        return truth

    elif config['function'] == 'energy_t':
        if config['target_gain'] == 0:
            return truth

        fft = ForwardTransform(N=config['frame_size'] * 4, R=config['frame_size'])
        for offset in range(0, len(audio), config['frame_size']):
            target_energy = fft.energy_t(int16_to_float(audio[offset:offset + config['frame_size']]))
            truth[offset:offset + config['frame_size'], config['index']] = np.single(target_energy)

        return truth

    elif config['function'] == 'energy_f':
        if config['target_gain'] == 0:
            return truth

        fft = ForwardTransform(N=config['frame_size'] * 4, R=config['frame_size'])

        if isinstance(config['index'], list):
            if len(config['index']) != fft.bins:
                raise SonusAIError('Truth index does not contain the right amount of classes')
        else:
            if config['index'] + fft.bins > config['num_classes']:
                raise SonusAIError('Truth index exceeds the number of classes')

        for offset in range(0, len(audio), config['frame_size']):
            target_energy = fft.energy_f(int16_to_float(audio[offset:offset + config['frame_size']]))

            indices = slice(offset, offset + config['frame_size'])
            if isinstance(config['index'], list):
                truth[indices, config['index']] = np.single(target_energy)
            else:
                truth[indices, config['index']:config['index'] + fft.bins] = np.single(target_energy)

        return truth

    elif config['function'] == 'phoneme':
        # Read in .txt transcript and run a Python function to generate text grid data
        # (indicating which phonemes are active)
        # Then generate truth based on this data and put in the correct classes based on config['index']
        raise SonusAIError('Truth function phoneme is not supported yet')

    raise SonusAIError(f'Unsupported truth function: {config["function"]}')


def get_truth_indices_for_mixid(mixdb: MixtureDatabase, mixid: int) -> List[int]:
    """Get a list of truth indices for a given mixid."""

    from sonusai.mixture.targets import get_truth_indices_for_target

    indices = list()
    for target_file_index in mixdb.mixtures[mixid].target_file_index:
        indices.append(*get_truth_indices_for_target(mixdb.targets[target_file_index]))

    return sorted(list(set(indices)))


def truth_reduction(x: np.ndarray, func: str) -> np.ndarray:
    from sonusai import SonusAIError

    if func == 'max':
        return np.max(x, axis=0)

    if func == 'mean':
        return np.mean(x, axis=0)

    raise SonusAIError(f'Invalid truth reduction function: {func}')
