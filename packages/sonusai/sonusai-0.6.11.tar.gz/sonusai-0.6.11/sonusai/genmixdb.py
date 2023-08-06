"""sonusai genmixdb

usage: genmixdb [-hv] CONFIG...

options:
   -h, --help
   -v, --verbose    Be verbose.

Create mixture database data for training and evaluation.

genmixdb creates a database of training and evaluation feature and truth data generation information. It allows
the choice of audio neural-network feature types that are supported by the Aaware real-time front-end and truth
data that is synchronized frame-by-frame with the feature data.

Here are some examples:

#### Adding target data
Suppose you have an audio file which is an example, or target, of what you want to
recognize or detect. Of course, for training a NN you also need truth data for that
file (also called labels). If you don't already have it, genmixdb can create truth using
energy-based sound detection on each frame of the feature data. You can also select
different feature types. Here's an example:

genmixdb target_gfr32ts2.yml

where target_gfr32ts2.yml contains:
---
feature: gfr32ts2

targets:
  - name: data/target.wav

target_augmentations:
  - normalize: -3.5
...

The mixture database is written to a JSON file that inherits the base name of the config file.

#### Target data mix with noise and augmentation

genmixdb mix_gfr32ts2.yml

where mix_gfr32ts2.yml contains:
---
feature: gfr32ts2

output: data/my_mix.h5

targets:
  - name: data/target.wav

target_augmentations:
  - normalize: -3.5
    pitch: [-3, 0, 3]
    tempo: [0.8, 1, 1.2]

noises:
  - name: data/noise.wav

noise_augmentations:
  - normalize: -3.5

snrs:
  - 20
...

In this example a time-domain mixture is created and feature data is calculated as
specified by 'feature: gfr32ts2'. Various feature types are available which vary in
spectral and temporal resolution (4 ms or higher), and other feature algorithm
parameters. The total feature size, dimension, and #frames for mixture is reported
in the log file (the log file name is derived from the output file base name; in this
case it would be mix_gfr32ts2.log).

Truth (labels) can be automatically created per feature output frame based on sound
energy detection. By default, these are appended to the feature data in a single HDF5
output file. By default, truth/label generation is turned on with default algorithm
and threshold levels (see truth section) and a single class, i.e., detecting a single
type of sound. The truth format is a single float per class representing the
probability of activity/presence, and multi-class truth/labels are possible by
specifying the number of classes and either a scalar index or a vector of indices in
which to put the truth result. For example, 'num_class: 3' and  'truth_index: 2' adds
a 1x3 vector to the feature data with truth put in index 2 (others would be 0) for
data/target.wav being an audio clip from sound type of class 2.

The mixture is created with potential data augmentation functions in the following way:
1. apply noise augmentation rule
2. apply target augmentation rule
3. adjust noise gain for specific SNR
4. add augmented noise to augmented target

The mixture length is the target length by default, and the noise signal is repeated
if it is shorter, or trimmed if longer.

#### Target and noise using path lists

Target and noise audio is specified as a list containing text files, audio files, and
file globs. Text files are processed with items on each line where each item can be a
text file, an audio file, or a file glob. Each item will be searched for audio files
which can be WAV, MP3, FLAC, AIFF, or OGG format with any sample rate, bit depth, or
channel count. All audio files will be converted to 16 kHz, 16-bit, single channel
format before processing. For example,

genmixdb dog-bark.yml

where dog-bark.yml contains:
---
targets:
  - name: slib/dog-outside/*.wav
  - name: slib/dog-inside/*.wav

will find all .wav files in the specified directories and process them as targets.

"""
from typing import List

import numpy as np

from sonusai import logger
from sonusai.mixture import AugmentedTargets
from sonusai.mixture import Mixture
from sonusai.mixture import MixtureDatabase

# NOTE: multiprocessing dictionary is required for run-time performance; using 'partial' is much slower.
MP_DICT = dict()


def genmixdb(file: str = None,
             config: dict = None,
             logging: bool = True,
             show_progress: bool = False) -> MixtureDatabase:
    from random import seed
    from typing import List

    import yaml
    from tqdm import tqdm

    import sonusai
    from sonusai import SonusAIError
    from sonusai.mixture import Augmentation
    from sonusai.mixture import Mixture
    from sonusai.mixture import MixtureDatabase
    from sonusai.mixture import Mixtures
    from sonusai.mixture import TruthSettings
    from sonusai.mixture import balance_targets
    from sonusai.mixture import build_noise_audios
    from sonusai.mixture import get_augmentation_indices_for_mixup
    from sonusai.mixture import get_augmentations
    from sonusai.mixture import get_augmented_target_indices_for_mixup
    from sonusai.mixture import get_augmented_targets
    from sonusai.mixture import get_class_weights_threshold
    from sonusai.mixture import get_feature_stats
    from sonusai.mixture import get_mixups
    from sonusai.mixture import get_noise_files
    from sonusai.mixture import get_target_files
    from sonusai.mixture import get_total_class_count
    from sonusai.mixture import load_config
    from sonusai.mixture import log_duration_and_sizes
    from sonusai.mixture import read_raw_target_audio
    from sonusai.mixture import update_truth_settings
    from sonusai.utils import dataclass_from_dict
    from sonusai.utils import p_tqdm_map

    if (file is None and config is None) or (file is not None and config is not None):
        raise SonusAIError(f'Must specify either file name or config')

    if file is not None:
        config = load_config(file)

    seed(config['seed'])

    if logging:
        logger.debug(f'Seed: {config["seed"]}')
        logger.debug('Configuration:')
        logger.debug(yaml.dump(config))

    if logging:
        logger.info('Collecting targets')
    target_files = get_target_files(config)
    if len(target_files) == 0:
        raise SonusAIError('Canceled due to no targets')

    if logging:
        logger.debug('List of targets:')
        logger.debug(yaml.dump([sub.name for sub in target_files], default_flow_style=False))

    if logging:
        logger.info('Collecting noises')
    noise_files = get_noise_files(config)
    if logging:
        logger.debug('List of noises:')
        logger.debug(yaml.dump([sub.name for sub in noise_files], default_flow_style=False))

    if logging:
        logger.info('Collecting target augmentations')
    target_augmentations = get_augmentations(rules=config['target_augmentations'])
    mixups = get_mixups(target_augmentations)
    if logging:
        for mixup in mixups:
            logger.debug(f'Expanded list of target augmentations for mixup of {mixup}:')
            indices = get_augmentation_indices_for_mixup(target_augmentations, mixup)
            for idx in indices:
                logger.debug(f'- {target_augmentations[idx]}')
            logger.debug('')

    if logging:
        logger.info('Collecting noise augmentations')
    noise_augmentations = get_augmentations(config['noise_augmentations'])
    if logging:
        logger.debug('Expanded list of noise augmentations:')
        for augmentation in noise_augmentations:
            logger.debug(f'- {augmentation}')
        logger.debug('')

    if logging:
        logger.debug(f'SNRs: {config["snrs"]}\n')
        logger.debug(f'Exhaustive noise: {config["exhaustive_noise"]}\n')

    if config['truth_mode'] not in ['normal', 'mutex']:
        raise SonusAIError(f'invalid truth_mode: {config["truth_mode"]}')
    truth_mutex = config['truth_mode'] == 'mutex'

    if truth_mutex and any(mixup > 1 for mixup in mixups):
        raise SonusAIError(f'Mutex truth mode is not compatible with mixup')

    fs = get_feature_stats(feature_mode=config['feature'],
                           frame_size=config['frame_size'],
                           num_classes=config['num_classes'],
                           truth_mutex=truth_mutex)

    augmented_targets = get_augmented_targets(target_files, target_augmentations)

    mixdb = MixtureDatabase(
        class_balancing=config['class_balancing'],
        class_balancing_augmentation=dataclass_from_dict(Augmentation, config['class_balancing_augmentation']),
        class_labels=config['class_labels'],
        class_weights_threshold=get_class_weights_threshold(config),
        exhaustive_noise=config['exhaustive_noise'],
        feature=config['feature'],
        feature_samples=fs.feature_samples,
        feature_step_samples=fs.feature_step_samples,
        first_cba_index=len(target_augmentations),
        frame_size=config['frame_size'],
        noise_augmentations=noise_augmentations,
        noises=noise_files,
        num_classes=config['num_classes'],
        seed=config['seed'],
        snrs=config['snrs'],
        target_augmentations=target_augmentations,
        targets=target_files,
        truth_mutex=truth_mutex,
        truth_reduction_function=config['truth_reduction_function'],
        truth_settings=dataclass_from_dict(TruthSettings, update_truth_settings(config['truth_settings'])),
    )

    MP_DICT['mixdb'] = mixdb

    raw_target_audio = read_raw_target_audio(mixdb=mixdb, show_progress=show_progress)
    noise_audios = build_noise_audios(mixdb=mixdb, show_progress=show_progress)

    MP_DICT['raw_target_audio'] = raw_target_audio
    MP_DICT['noise_audios'] = noise_audios

    augmented_targets = balance_targets(mixdb, augmented_targets)

    target_sets = 0
    total_duration = 0
    for mixup in mixups:
        augmented_target_indices_for_mixup = get_augmented_target_indices_for_mixup(
            mixdb=mixdb,
            augmented_targets=augmented_targets,
            mixup=mixup)
        target_sets += len(augmented_target_indices_for_mixup)
        for indices in augmented_target_indices_for_mixup:
            for augmented_target in [augmented_targets[idx] for idx in indices]:
                length = int(target_files[augmented_target.target_file_index].duration * sonusai.mixture.SAMPLE_RATE)
                augmentation = target_augmentations[augmented_target.target_augmentation_index]
                if augmentation.tempo is not None:
                    length /= augmentation.tempo
                if length % fs.feature_step_samples:
                    length += fs.feature_step_samples - int(length % fs.feature_step_samples)
                total_duration += float(length) / sonusai.mixture.SAMPLE_RATE

    target_sets *= len(mixdb.snrs)
    total_duration *= len(mixdb.snrs)
    noise_sets = len(noise_files) * len(noise_augmentations) if mixdb.exhaustive_noise else 1
    total_mixtures = noise_sets * target_sets
    if logging:
        logger.info('')
        logger.info(f'Found {total_mixtures:,} mixtures to process')

    if logging:
        log_duration_and_sizes(total_duration=total_duration,
                               num_classes=mixdb.num_classes,
                               feature_step_samples=fs.feature_step_samples,
                               num_bands=fs.num_bands,
                               stride=fs.stride,
                               desc='Estimated')
        logger.info(f'Feature shape:        {fs.stride} x {fs.num_bands} ({fs.stride * fs.num_bands} total params)')
        logger.info(f'Feature samples:      {fs.feature_samples} samples ({fs.feature_ms} ms)')
        logger.info(f'Feature step samples: {fs.feature_step_samples} samples ({fs.feature_step_ms} ms)')

    if mixdb.exhaustive_noise:
        # Get indices and offsets
        # mixtures is a nested list: noise, target
        mixtures: List[Mixtures] = list()

        for noise_file_index in range(len(noise_files)):
            for noise_augmentation_index, noise_augmentation in enumerate(noise_augmentations):
                mixtures.append(list())
                noise_offset = 0
                noise_length = len(noise_audios[noise_file_index][noise_augmentation_index])
                for mixup in mixups:
                    augmented_target_indices_for_mixup = get_augmented_target_indices_for_mixup(
                        mixdb=mixdb,
                        augmented_targets=augmented_targets,
                        mixup=mixup)
                    for augmented_target_indices_for_mixup in augmented_target_indices_for_mixup:
                        (target_file_index,
                         target_augmentation_index,
                         target_length) = _get_target_info(
                            mixdb=mixdb,
                            augmented_target_indices_for_mixup=augmented_target_indices_for_mixup,
                            augmented_targets=augmented_targets,
                            raw_target_audio=raw_target_audio)

                        for snr in mixdb.snrs:
                            mixtures[-1].append(Mixture(
                                target_file_index=target_file_index,
                                target_augmentation_index=target_augmentation_index,
                                noise_file_index=noise_file_index,
                                noise_offset=noise_offset,
                                noise_augmentation_index=noise_augmentation_index,
                                snr=snr,
                            ))

                            noise_offset = int((noise_offset + target_length) % noise_length)

        # Fill in the details
        progress = tqdm(total=total_mixtures, desc='genmixdb', disable=not show_progress)
        for n_id in range(len(mixtures)):
            m = mixtures[n_id][0]
            MP_DICT['augmented_noise_audio'] = noise_audios[m.noise_file_index][m.noise_augmentation_index]
            mixtures[n_id] = p_tqdm_map(_process_mixture, mixtures[n_id], progress=progress)
        progress.close()

        # Flatten mixtures
        mixdb.mixtures = [item for sublist in mixtures for item in sublist]

    else:
        # Get indices and offsets
        mixtures: Mixtures = list()

        noise_offset = 0
        noise_file_index = 0
        noise_augmentation_index = 0
        for mixup in mixups:
            augmented_target_indices_for_mixup = get_augmented_target_indices_for_mixup(
                mixdb=mixdb,
                augmented_targets=augmented_targets,
                mixup=mixup)
            for augmented_target_indices_for_mixup in augmented_target_indices_for_mixup:
                (target_file_index,
                 target_augmentation_index,
                 target_length) = _get_target_info(
                    mixdb=mixdb,
                    augmented_target_indices_for_mixup=augmented_target_indices_for_mixup,
                    augmented_targets=augmented_targets,
                    raw_target_audio=raw_target_audio)

                if noise_offset + target_length >= len(noise_audios[noise_file_index][noise_augmentation_index]):
                    if noise_offset == 0:
                        raise SonusAIError('Length of target audio exceeds length of noise audio')

                    noise_offset = 0
                    noise_augmentation_index += 1
                    if noise_augmentation_index == len(noise_audios[noise_file_index]):
                        noise_augmentation_index = 0
                        noise_file_index += 1
                        if noise_file_index == len(noise_audios):
                            noise_file_index = 0

                for snr in mixdb.snrs:
                    mixtures.append(Mixture(target_file_index=target_file_index,
                                            target_augmentation_index=target_augmentation_index,
                                            noise_file_index=noise_file_index,
                                            noise_augmentation_index=noise_augmentation_index,
                                            noise_offset=noise_offset,
                                            snr=snr))

                noise_offset += target_length

        # Fill in the details
        progress = tqdm(total=total_mixtures, desc='genmixdb', disable=not show_progress)
        mixtures = p_tqdm_map(_process_mixture_nen, mixtures, progress=progress)
        progress.close()

        mixdb.mixtures = mixtures

    mixdb.class_count = get_total_class_count(mixdb)

    total_samples = sum([sub.samples for sub in mixdb.mixtures])
    total_duration = total_samples / sonusai.mixture.SAMPLE_RATE
    if logging:
        log_duration_and_sizes(total_duration=total_duration,
                               num_classes=mixdb.num_classes,
                               feature_step_samples=fs.feature_step_samples,
                               num_bands=fs.num_bands,
                               stride=fs.stride,
                               desc='Actual')

    return mixdb


def _get_target_info(mixdb: MixtureDatabase,
                     augmented_target_indices_for_mixup: List[int],
                     augmented_targets: AugmentedTargets,
                     raw_target_audio: List[np.ndarray]) -> (List[int], List[int], int):
    from sonusai.mixture import estimate_audio_length

    target_file_index = list()
    target_augmentation_index = list()
    target_length = 0
    for idx in augmented_target_indices_for_mixup:
        tfi = augmented_targets[idx].target_file_index
        tai = augmented_targets[idx].target_augmentation_index

        target_file_index.append(tfi)
        target_augmentation_index.append(tai)

        target_audio = raw_target_audio[tfi]
        target_augmentation = mixdb.target_augmentations[tai]
        target_length = max(estimate_audio_length(audio_in=target_audio,
                                                  augmentation=target_augmentation,
                                                  length_common_denominator=mixdb.feature_step_samples),
                            target_length)
    return target_file_index, target_augmentation_index, target_length


def get_output_from_config(config: dict, config_name: str) -> str:
    from os.path import splitext

    from sonusai import SonusAIError

    try:
        config_base = splitext(config_name)[0]
        name = str(splitext(config['output'])[0])
        name = name.replace('${config}', config_base)
        return name
    except Exception as e:
        raise SonusAIError(f'Error getting genmixdb base name: {e}')


def _process_mixture(mixture: Mixture) -> Mixture:
    from sonusai.mixture import process_mixture

    return process_mixture(mixture=mixture,
                           mixdb=MP_DICT['mixdb'],
                           raw_target_audio=MP_DICT['raw_target_audio'],
                           augmented_noise_audio=MP_DICT['augmented_noise_audio'])


def _process_mixture_nen(mixture: Mixture) -> Mixture:
    from sonusai.mixture import process_mixture_nen

    return process_mixture_nen(mixture=mixture,
                               mixdb=MP_DICT['mixdb'],
                               raw_target_audio=MP_DICT['raw_target_audio'],
                               noise_audios=MP_DICT['noise_audios'])


def main():
    import time

    from docopt import docopt

    import sonusai
    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import update_console_handler
    from sonusai.mixture import load_config
    from sonusai.utils import seconds_to_hms
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sonusai.__version__, options_first=True)

    verbose = args['--verbose']

    for config_file in args['CONFIG']:
        start_time = time.monotonic()
        logger.info(f'Creating mixture database for {config_file}')
        config = load_config(config_file)
        output = get_output_from_config(config, config_file)

        log_name = output + '.log'
        create_file_handler(log_name)
        update_console_handler(verbose)
        initial_log_messages('genmixdb')

        mixdb = genmixdb(config=config, show_progress=True)

        json_name = output + '.json'
        with open(file=json_name, mode='w') as file:
            file.write(mixdb.to_json(indent=2))
            logger.info(f'Wrote mixture database for {config_file} to {json_name}')

        end_time = time.monotonic()
        logger.info(f'Completed in {seconds_to_hms(seconds=end_time - start_time)}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        raise SystemExit(0)
