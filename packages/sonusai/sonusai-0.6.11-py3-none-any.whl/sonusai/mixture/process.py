from typing import List

import numpy as np

from sonusai.mixture.mixdb import Mixture
from sonusai.mixture.mixdb import MixtureDatabase


def _process_target_audio(mixdb: MixtureDatabase,
                          mixture: Mixture,
                          raw_target_audio: List[np.ndarray]) -> np.ndarray:
    """Apply augmentation and update target metadata."""
    from sonusai import SonusAIError
    from sonusai.mixture.augmentation import apply_augmentation
    from sonusai.mixture.class_count import get_class_count

    target_file_index = mixture.target_file_index
    target_augmentation_index = mixture.target_augmentation_index
    if len(target_file_index) != len(target_augmentation_index):
        raise SonusAIError('target_file_index and target_augmentation_index are not the same length')

    mixture.samples = 0
    target_audio = list()
    mixture.target_gain = list()
    for idx in range(len(target_file_index)):
        target_augmentation = mixdb.target_augmentations[target_augmentation_index[idx]]

        target_audio.append(apply_augmentation(audio_in=raw_target_audio[target_file_index[idx]],
                                               augmentation=target_augmentation,
                                               length_common_denominator=mixdb.feature_step_samples))

        # target_gain is used to back out the gain augmentation in order to return the target audio
        # to its normalized level when calculating truth.
        if target_augmentation.gain is not None:
            target_gain = 10 ** (target_augmentation.gain / 20)
        else:
            target_gain = 1
        mixture.target_gain.append(target_gain)

    mixture.samples = max([len(item) for item in target_audio])

    for idx in range(len(target_audio)):
        pad = mixture.samples - len(target_audio[idx])
        target_audio[idx] = np.pad(target_audio[idx], (0, pad), mode='constant', constant_values=0)

    mixture.class_count = get_class_count(mixdb=mixdb,
                                          mixture=mixture,
                                          target_audio=target_audio)

    return sum(target_audio)


def process_target(mixture: Mixture,
                   mixdb: MixtureDatabase,
                   raw_target_audio: List[np.ndarray]) -> Mixture:
    """Apply augmentation and update target metadata."""
    _process_target_audio(mixdb, mixture, raw_target_audio)
    return mixture


def process_mixture(mixture: Mixture,
                    mixdb: MixtureDatabase,
                    raw_target_audio: List[np.ndarray],
                    augmented_noise_audio: np.ndarray) -> Mixture:
    from sonusai.mixture.audio_db import get_next_noise

    augmented_target_audio = _process_target_audio(mixdb=mixdb,
                                                   mixture=mixture,
                                                   raw_target_audio=raw_target_audio)

    noise_segment, _ = get_next_noise(offset_in=mixture.noise_offset,
                                      length=mixture.samples,
                                      audio_in=augmented_noise_audio)

    return _update_mixture_gains(mixdb=mixdb,
                                 mixture=mixture,
                                 augmented_target_audio=augmented_target_audio,
                                 noise_segment=noise_segment)


def process_mixture_nen(mixture: Mixture,
                        mixdb: MixtureDatabase,
                        raw_target_audio: List[np.ndarray],
                        noise_audios: List[List[np.ndarray]]) -> Mixture:
    from sonusai.mixture.audio_db import get_next_noise

    augmented_target_audio = _process_target_audio(mixdb=mixdb,
                                                   mixture=mixture,
                                                   raw_target_audio=raw_target_audio)

    noise_segment, _ = get_next_noise(offset_in=mixture.noise_offset,
                                      length=mixture.samples,
                                      audio_in=noise_audios[mixture.noise_file_index][mixture.noise_augmentation_index])

    return _update_mixture_gains(mixdb=mixdb,
                                 mixture=mixture,
                                 augmented_target_audio=augmented_target_audio,
                                 noise_segment=noise_segment)


def _update_mixture_gains(mixdb: MixtureDatabase,
                          mixture: Mixture,
                          augmented_target_audio: np.ndarray,
                          noise_segment: np.ndarray) -> Mixture:
    from sonusai.utils.dbfs import dbfs_to_sample

    if mixture.snr < -96:
        # Special case for zeroing out target data
        mixture.target_snr_gain = 0
        mixture.noise_snr_gain = 1
        mixture.class_count = [0] * mixdb.num_classes
        # Setting target_gain to zero will cause the truth to be all zeros.
        mixture.target_gain = [0] * len(mixture.target_gain)
    elif mixture.snr > 96:
        # Special case for zeroing out noise data
        mixture.target_snr_gain = 1
        mixture.noise_snr_gain = 0
    else:
        target_energy = np.mean(np.square(np.single(augmented_target_audio)))
        noise_energy = np.mean(np.square(np.single(noise_segment)))
        noise_gain = np.sqrt(target_energy / noise_energy) / 10 ** (mixture.snr / 20)

        # Check for noise_gain > 1 to avoid clipping
        if noise_gain > 1:
            mixture.target_snr_gain = 1 / noise_gain
            mixture.noise_snr_gain = 1
        else:
            mixture.target_snr_gain = 1
            mixture.noise_snr_gain = noise_gain
    # Check for clipping in mixture
    gain_adjusted_target_audio = np.single(augmented_target_audio) * mixture.target_snr_gain
    gain_adjusted_noise_audio = np.single(noise_segment) * mixture.noise_snr_gain
    mixture_audio = gain_adjusted_target_audio + gain_adjusted_noise_audio
    if any(abs(mixture_audio) >= 32768):
        # Clipping occurred; lower gains to bring audio within int16 bounds
        gain_adjustment = dbfs_to_sample(-0.25) / max(abs(mixture_audio))
        mixture.target_snr_gain *= gain_adjustment
        mixture.noise_snr_gain *= gain_adjustment

    return mixture
