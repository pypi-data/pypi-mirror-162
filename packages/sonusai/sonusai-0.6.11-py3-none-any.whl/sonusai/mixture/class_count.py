from typing import List

import numpy as np

from sonusai.mixture.mixdb import ClassCount
from sonusai.mixture.mixdb import Mixture
from sonusai.mixture.mixdb import MixtureDatabase
from sonusai.mixture.mixdb import MixtureID
from sonusai.mixture.mixdb import Mixtures


def get_class_count(mixdb: MixtureDatabase, mixture: Mixture, target_audio: List[np.ndarray]) -> ClassCount:
    """Computes the number of samples for which each truth index is active for a given sample-based truth input."""
    from sonusai.mixture.mixdb import get_class_weights_threshold
    from sonusai.mixture.truth import generate_truth

    truth = generate_truth(mixdb=mixdb,
                           mixture=mixture,
                           target_audio=target_audio)

    class_weights_threshold = get_class_weights_threshold(mixdb)

    class_count = [0] * mixdb.num_classes
    num_classes = mixdb.num_classes
    if mixdb.truth_mutex:
        num_classes -= 1
    for cl in range(num_classes):
        class_count[cl] = int(np.sum(truth[:, cl] >= class_weights_threshold[cl]))

    return class_count


def get_total_class_count(mixdb: MixtureDatabase, mixid: MixtureID = ':') -> ClassCount:
    """Sums the class counts for all mixtures."""
    from sonusai.mixture.mixdb import get_mixtures_from_mixid

    mixtures = get_mixtures_from_mixid(mixdb, mixid)
    return compute_total_class_count(mixdb, mixtures)


def compute_total_class_count(mixdb: MixtureDatabase, mixtures: Mixtures) -> ClassCount:
    from sonusai import SonusAIError

    total_class_count = [0] * mixdb.num_classes
    for mixture in mixtures:
        for cl in range(mixdb.num_classes):
            total_class_count[cl] += mixture.class_count[cl]

    if mixdb.truth_mutex:
        # Compute the class count for the 'other' class
        if total_class_count[-1] != 0:
            raise SonusAIError('Error: truth_mutex was set, but the class count for the last count was non-zero.')
        total_class_count[-1] = sum([sub.samples for sub in mixtures]) - sum(total_class_count)

    return total_class_count

# def get_class_count_metrics_for_class(mixdb: MixtureDatabase, class_index: int) -> (int, int):
#     """TODO"""
#     pass
