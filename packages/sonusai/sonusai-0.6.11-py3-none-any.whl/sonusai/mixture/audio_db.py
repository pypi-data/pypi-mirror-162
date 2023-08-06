from dataclasses import dataclass
from typing import List
from typing import Union

import numpy as np

from sonusai.mixture.mixdb import Mixture
from sonusai.mixture.mixdb import MixtureDatabase

# NOTE: multiprocessing dictionary is required for run-time performance; using 'partial' is much slower.
MP_DICT = dict()


def build_noise_audios(mixdb: MixtureDatabase, show_progress: bool = False) -> List[List[np.ndarray]]:
    """Build a database of noise audio data."""
    from tqdm import tqdm

    from sonusai.mixture.augmentation import apply_augmentation

    noise_audios = list()
    for file_index in tqdm(range(len(mixdb.noises)), desc='Read noise audio', disable=not show_progress):
        audio_in = read_audio(name=mixdb.noises[file_index].name)
        noise_audios.append(list())
        for augmentation_index, augmentation in enumerate(mixdb.noise_augmentations):
            noise_audios[-1].append(apply_augmentation(audio_in=audio_in, augmentation=augmentation))

    return noise_audios


def build_target_audios(mixdb: MixtureDatabase, show_progress: bool = False) -> List[np.ndarray]:
    """Build a list of target audio data."""
    from tqdm import tqdm

    from sonusai.mixture.mixdb import MixtureDatabase
    from sonusai.utils.parallel_tqdm import p_tqdm_map

    MP_DICT['mixdb']: MixtureDatabase = mixdb

    indices = list(range(len(mixdb.targets)))
    progress = tqdm(total=len(indices), desc='Read target audio', disable=not show_progress)
    target_audios = p_tqdm_map(_read_target_audio, indices, progress=progress)
    return target_audios


def _read_target_audio(file_index: int) -> np.ndarray:
    """Parallel target audio reader kernel."""
    mixdb: MixtureDatabase = MP_DICT['mixdb']
    return read_audio(name=mixdb.targets[file_index].name)


def check_audio_files_exist(mixdb: MixtureDatabase) -> None:
    """Walk through all the noise and target audio files in a mixture database ensuring that they exist."""
    from os.path import exists

    from sonusai import SonusAIError
    from sonusai.mixture.config import tokenized_expandvars

    for file_index in range(len(mixdb.noises)):
        file_name, _ = tokenized_expandvars(mixdb.noises[file_index].name)
        if not exists(file_name):
            raise SonusAIError(f'Could not find {file_name}')

    for file_index in range(len(mixdb.targets)):
        file_name, _ = tokenized_expandvars(mixdb.targets[file_index].name)
        if not exists(file_name):
            raise SonusAIError(f'Could not find {file_name}')


def read_raw_target_audio(mixdb: MixtureDatabase,
                          show_progress: bool = False) -> List[np.ndarray]:
    """Read in all audio data beforehand to avoid reading it multiple times in a loop."""

    from tqdm import tqdm

    from sonusai.utils.parallel_tqdm import p_tqdm_map

    names = [target.name for target in mixdb.targets]
    progress = tqdm(total=len(names), desc='Read target audio', disable=not show_progress)
    raw_target_audio = p_tqdm_map(read_audio, names, progress=progress)
    progress.close()

    return raw_target_audio


def get_target_noise_audio(mixdb: MixtureDatabase,
                           mixture: Mixture,
                           target_audios: List[np.ndarray],
                           noise_audios: List[List[np.ndarray]]) -> (List[np.ndarray], np.ndarray):
    """Apply augmentations and return augmented target and noise data."""

    from sonusai import SonusAIError
    from sonusai.mixture.augmentation import apply_augmentation

    target_file_index = mixture.target_file_index
    target_augmentation_index = mixture.target_augmentation_index
    if len(target_file_index) != len(target_augmentation_index):
        raise SonusAIError('target_file_index and target_augmentation_index are not the same length')

    if mixture.samples % mixdb.frame_size != 0:
        raise SonusAIError(f'Number of samples in mixture is not a multiple of {mixdb.frame_size}')

    target_audio = list()
    for idx in range(len(mixture.target_file_index)):
        target_augmentation = mixdb.target_augmentations[target_augmentation_index[idx]]

        audio_out = apply_augmentation(audio_in=target_audios[target_file_index[idx]],
                                       augmentation=target_augmentation,
                                       length_common_denominator=mixdb.feature_step_samples)

        audio_out = np.array(np.single(audio_out) * mixture.target_snr_gain, dtype=np.int16)
        audio_out = _pad_to_samples(audio_in=audio_out, samples=mixture.samples)
        target_audio.append(audio_out)

    noise_audio, _ = get_next_noise(offset_in=mixture.noise_offset,
                                    length=mixture.samples,
                                    audio_in=noise_audios[mixture.noise_file_index][mixture.noise_augmentation_index])

    noise_audio = np.array(np.single(noise_audio) * mixture.noise_snr_gain, dtype=np.int16)

    return target_audio, noise_audio


def _pad_to_samples(audio_in: np.ndarray, samples: int) -> np.ndarray:
    return np.pad(audio_in, (0, samples - len(audio_in)), mode='constant', constant_values=0)


def get_audio_and_truth_t(mixdb: MixtureDatabase,
                          mixture: Mixture,
                          target_audios: List[np.ndarray],
                          noise_audios: List[List[np.ndarray]],
                          compute_truth: bool = True,
                          compute_segsnr: bool = False,
                          frame_based_segsnr: bool = False) \
        -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    from sonusai.mixture.segsnr import generate_segsnr
    from sonusai.mixture.truth import generate_truth

    target_audio, noise_audio = get_target_noise_audio(mixdb=mixdb,
                                                       mixture=mixture,
                                                       target_audios=target_audios,
                                                       noise_audios=noise_audios)

    truth_t = generate_truth(mixdb=mixdb,
                             mixture=mixture,
                             target_audio=target_audio,
                             compute=compute_truth)

    target_audio = sum(_pad_target_audio(audio_in=target_audio))

    segsnr = generate_segsnr(mixdb=mixdb,
                             mixture=mixture,
                             target_audio=target_audio,
                             noise_audio=noise_audio,
                             compute=compute_segsnr,
                             frame_based=frame_based_segsnr)

    mixture_audio = np.array(target_audio + noise_audio, dtype=np.int16)
    return mixture_audio, truth_t, target_audio, noise_audio, segsnr


def _pad_target_audio(audio_in: List[np.ndarray]) -> List[np.ndarray]:
    samples = max([len(item) for item in audio_in])
    for idx in range(len(audio_in)):
        pad = samples - len(audio_in[idx])
        audio_in[idx] = np.pad(audio_in[idx], (0, pad), mode='constant', constant_values=0)
    return audio_in


def get_next_noise(offset_in: int, length: int, audio_in: np.ndarray) -> (np.ndarray, int):
    audio_out = np.take(audio_in, range(offset_in, offset_in + length), mode='wrap')
    offset_out = (offset_in + length) % len(audio_in)
    return audio_out, offset_out


def read_audio(name: str) -> np.ndarray:
    import sox

    from sonusai import SonusAIError
    from sonusai import logger
    from sonusai.mixture.config import tokenized_expandvars
    from sonusai.mixture.constants import BIT_DEPTH
    from sonusai.mixture.constants import CHANNEL_COUNT
    from sonusai.mixture.constants import SAMPLE_RATE

    expanded_name, _ = tokenized_expandvars(name)

    try:
        # Read in and convert to desired format
        inp = sox.Transformer()
        inp.set_output_format(rate=SAMPLE_RATE, bits=BIT_DEPTH, channels=CHANNEL_COUNT)
        return inp.build_array(input_filepath=expanded_name,
                               sample_rate_in=int(sox.file_info.sample_rate(expanded_name)))

    except Exception as e:
        if name != expanded_name:
            logger.error(f'Error reading {name} (expanded: {expanded_name}): {e}')
        else:
            raise SonusAIError(f'Error reading {name}: {e}')


@dataclass(frozen=True)
class MixtureData:
    mixture: np.ndarray
    target: List[Union[np.ndarray, None]]
    noise: np.ndarray
    feature: np.ndarray
    truth_f: np.ndarray


def get_mixture_data(mixdb: MixtureDatabase, mixid: int) -> MixtureData:
    """Get mixture data assuming nothing has been loaded into memory already."""

    from sonusai.mixture.augmentation import apply_augmentation
    from sonusai.mixture.feature import get_feature_and_truth_f
    from sonusai.mixture.targets import get_truth_indices_for_target
    from sonusai.mixture.truth import generate_truth

    mixture = mixdb.mixtures[mixid]

    target_audio = list()
    target_truth_indices = list()
    for idx in range(len(mixture.target_file_index)):
        target_name = mixdb.targets[mixture.target_file_index[idx]].name
        target_augmentation = mixdb.target_augmentations[mixture.target_augmentation_index[idx]]

        audio_out = apply_augmentation(audio_in=read_audio(target_name),
                                       augmentation=target_augmentation,
                                       length_common_denominator=mixdb.feature_step_samples)

        audio_out = np.array(np.single(audio_out) * mixture.target_snr_gain, dtype=np.int16)
        audio_out = _pad_to_samples(audio_in=audio_out, samples=mixture.samples)
        target_audio.append(audio_out)
        target_truth_indices.append(get_truth_indices_for_target(mixdb.targets[mixture.target_file_index[idx]]))

    target_audio = _pad_target_audio(audio_in=target_audio)

    noise_audios = build_noise_audios(mixdb=mixdb, show_progress=False)
    noise_audio, _ = get_next_noise(offset_in=mixture.noise_offset,
                                    length=mixture.samples,
                                    audio_in=noise_audios[mixture.noise_file_index][mixture.noise_augmentation_index])

    noise_audio = np.array(np.single(noise_audio) * mixture.noise_snr_gain, dtype=np.int16)

    truth_t = generate_truth(mixdb=mixdb,
                             mixture=mixture,
                             target_audio=target_audio,
                             compute=True)

    mixture_audio = np.array(sum(target_audio) + noise_audio, dtype=np.int16)

    # Transform target_audio into a list num_classes long such that each entry is the target data per class
    class_audio = list()
    for n in range(mixdb.num_classes):
        class_audio.append(None)
        for idx in range(len(target_audio)):
            if n + 1 in target_truth_indices[idx]:
                if class_audio[n] is None:
                    class_audio[n] = target_audio[idx]
                else:
                    class_audio[n] += target_audio[idx]

    feature, truth_f = get_feature_and_truth_f(mixdb=mixdb, mixid=mixid, audio=mixture_audio, truth_t=truth_t)

    return MixtureData(mixture=mixture_audio,
                       target=class_audio,
                       noise=noise_audio,
                       feature=feature,
                       truth_f=truth_f)
