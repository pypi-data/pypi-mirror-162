from typing import List

from sonusai.mixture.mixdb import Mixture
from sonusai.mixture.mixdb import MixtureDatabase
from sonusai.mixture.mixdb import Mixtures

# NOTE: multiprocessing dictionary is required for run-time performance; using 'partial' is much slower.
MP_DICT = dict()


def balance_active_truth(mixdb: MixtureDatabase,
                         raw_target_audio: list,
                         logging: bool = True,
                         show_progress: bool = False) -> Mixtures:
    """Add target augmentations until the class count values are balanced."""

    import numpy as np

    from sonusai import logger
    from sonusai.mixture import SAMPLE_RATE
    from sonusai.utils import seconds_to_hms

    MP_DICT['mixdb'] = mixdb
    MP_DICT['raw_target_audio'] = raw_target_audio

    augmented_targets = _get_augmented_targets(mixdb)
    class_balancing_samples = _get_class_balancing_samples(mixdb, augmented_targets)
    if logging:
        logger.info('')
        label_digits = max([len(_get_class_label(mixdb, item)) for item in range(len(class_balancing_samples))])
        samples_digits = np.ceil(np.log10(float(max(class_balancing_samples))))
        samples_digits = int(samples_digits + np.ceil(samples_digits / 3))
        for class_index, required_samples in enumerate(class_balancing_samples):
            logger.info(f'Class {_get_class_label(mixdb, class_index):>{label_digits}} '
                        f'needs {required_samples:>{samples_digits},} more active truth samples '
                        f' - {seconds_to_hms(required_samples / SAMPLE_RATE)}')
        logger.info('')

    for class_index, required_samples in enumerate(class_balancing_samples):
        augmented_targets = _balance_class(mixdb=mixdb,
                                           mixtures=augmented_targets,
                                           class_index=class_index,
                                           required_samples=required_samples,
                                           logging=logging,
                                           show_progress=show_progress)

    return augmented_targets


def _balance_class(mixdb: MixtureDatabase,
                   mixtures: Mixtures,
                   class_index: int,
                   required_samples: int,
                   logging: bool = True,
                   show_progress: bool = False) -> Mixtures:
    """Add target augmentations for a single class until the required samples are satisfied."""
    import multiprocessing as mp

    import numpy as np
    from tqdm import tqdm

    from sonusai import SonusAIError
    from sonusai import logger
    from sonusai.mixture import Mixture
    from sonusai.mixture import get_target_indices_for_truth_index
    from sonusai.utils import p_map

    if required_samples == 0:
        return mixtures

    class_label = _get_class_label(mixdb, class_index)

    # Get list of targets for this class
    target_indices = get_target_indices_for_truth_index(mixdb.targets, class_index)
    if not target_indices:
        raise SonusAIError(f'Could not find single-class targets for class index {class_index}')

    num_cpus = mp.cpu_count()

    remaining_samples = required_samples
    added_samples = 0
    added_targets = 0
    progress = tqdm(total=required_samples, desc=f'Balance class {class_label}', disable=not show_progress)
    while True:
        records: Mixtures = []
        while len(records) < num_cpus:
            for target_index in target_indices:
                augmentation_indices = _get_unused_balancing_augmentations(mixdb=mixdb,
                                                                           mixtures=mixtures,
                                                                           target_file_index=target_index,
                                                                           amount=num_cpus)
                for augmentation_index in augmentation_indices:
                    records.append(Mixture(target_file_index=[target_index],
                                           target_augmentation_index=[augmentation_index]))

        records = records[0:num_cpus]
        records = p_map(_process_target, records)

        for record in records:
            new_samples = np.sum(np.sum(record.class_count))
            remaining_samples -= new_samples

            # If the current record will overshoot the required samples then add it only if
            # overshooting results in a sample count closer to the required than not overshooting.
            add_record = remaining_samples >= 0 or -remaining_samples < remaining_samples + new_samples

            if add_record:
                mixtures.append(record)
                added_samples += new_samples
                added_targets += 1
                progress.update(new_samples)

            if remaining_samples <= 0:
                _remove_unused_augmentations(mixdb=mixdb, mixtures=mixtures)
                progress.update(required_samples - added_samples)
                progress.close()
                if logging:
                    logger.info(f'Added {added_targets:,} new augmented targets for class {class_label}')
                return mixtures


def _process_target(mixture: Mixture) -> Mixture:
    from sonusai.mixture import process_target

    return process_target(mixture=mixture, mixdb=MP_DICT['mixdb'], raw_target_audio=MP_DICT['raw_target_audio'])


def _get_class_balancing_samples(mixdb: MixtureDatabase, mixtures: Mixtures) -> List[int]:
    """Determine the number of additional active truth samples needed for each class in order for
    all classes to be represented evenly over all mixtures.

    If the truth mode is mutually exclusive, ignore the last class (i.e., set to zero).
    """

    import numpy as np

    from sonusai.mixture import compute_total_class_count

    class_count = compute_total_class_count(mixdb, mixtures)

    if mixdb.truth_mutex:
        class_count = class_count[:-1]

    result = list(np.max(class_count) - class_count)

    if mixdb.truth_mutex:
        result.append(0)

    return result


def _get_augmented_targets(mixdb: MixtureDatabase) -> Mixtures:
    """Get a list of augmented targets from a mixture database."""
    snr = max(mixdb.snrs)
    return [sub for sub in mixdb.mixtures if sub.snr == snr and sub.noise_file_index == 0]


def _get_class_label(mixdb: MixtureDatabase, class_index: int) -> str:
    if mixdb.class_labels:
        return mixdb.class_labels[class_index]

    return str(class_index)


def _get_unused_balancing_augmentations(mixdb: MixtureDatabase,
                                        mixtures: Mixtures,
                                        target_file_index: int,
                                        amount: int = 1) -> List[int]:
    """Get a list of unused balancing augmentations for a given target file index."""
    from dataclasses import asdict

    from sonusai.mixture import get_augmentations
    from sonusai.mixture import get_class_balancing_augmentation

    balancing_augmentations = [item for item in range(len(mixdb.target_augmentations)) if
                               item >= mixdb.first_cba_index]
    used_balancing_augmentations = [sub.target_augmentation_index for sub in mixtures if
                                    sub.target_file_index == target_file_index and
                                    sub.target_augmentation_index in balancing_augmentations]

    augmentation_indices = [item for item in balancing_augmentations if item not in used_balancing_augmentations]
    class_balancing_augmentation = get_class_balancing_augmentation(mixdb=mixdb, target_file_index=target_file_index)

    while len(augmentation_indices) < amount:
        new_augmentation = get_augmentations(asdict(class_balancing_augmentation))[0]
        mixdb.target_augmentations.append(new_augmentation)
        augmentation_indices.append(len(mixdb.target_augmentations) - 1)

    return augmentation_indices


def _remove_unused_augmentations(mixdb: MixtureDatabase, mixtures: Mixtures) -> None:
    """Remove any unused target augmentation rules from the end of the database."""
    max_used_augmentation = max([index for mixture in mixtures for index in mixture.target_augmentation_index]) + 1
    mixdb.target_augmentations = mixdb.target_augmentations[0:max_used_augmentation]
