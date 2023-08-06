import numpy as np


def calculate_optimal_thresholds(truth: np.ndarray,
                                 predict: np.ndarray,
                                 timesteps: int = 0,
                                 truth_thr: float = 0.5) -> (np.ndarray, np.ndarray):
    """ Calculates optimal thresholds for each class from one-hot prediction and truth data
        (numpy float arrays) where both are one-hot probabilities (or quantized decisions)
        with size frames x num_classes or frames x timesteps x num_classes.

        Returns 2 threshold arrays num_classes x 1:
          thresholds_opt_pr:     optimal thesholds for PR-curve (F1) performance
          thresholds_opt_roc:    optimal thresholds for ROC-curve (TPR/FPR) performance

        Optional truth_thr is the decision threshold(s) applied to truth one-hot input thus allowing
        truth to optionally be continuous probabilities.  Default is 0.5.
    """
    from sklearn.metrics import average_precision_score
    from sklearn.metrics import precision_recall_curve
    from sklearn.metrics import roc_auc_score
    from sklearn.metrics import roc_curve

    from sonusai import logger
    from sonusai.utils.reshape import reshape_truth_predict

    if truth.shape != predict.shape:
        logger.error('Shape of truth and predict are not equal')
        exit()

    truth, predict, num_classes = reshape_truth_predict(truth, predict, timesteps)

    # Apply decision to truth input
    truthb = np.int8(truth >= truth_thr)

    AP = np.zeros((num_classes, 1))
    AUC = np.zeros((num_classes, 1))
    thresholds_opt_pr = np.zeros((num_classes, 1))
    thresholds_opt_roc = np.zeros((num_classes, 1))
    eps = np.finfo(float).eps
    for nci in range(num_classes):
        # Average Precision also called area under the PR curve AUCPR and
        # AUC ROC curve using binary-ized truth and continuous prediction probabilities
        # sklearn returns nan if no active truth in a class but w/un-suppressible div-by-zero warning
        if sum(truthb[:, nci]) == 0:  # no active truth must be NaN
            thresholds_opt_pr[nci] = np.NaN
            thresholds_opt_roc[nci] = np.NaN
            AUC[nci] = np.NaN
            AP[nci] = np.NaN
        else:
            AP[nci] = average_precision_score(truthb[:, nci], predict[:, nci], average=None)
            AUC[nci] = roc_auc_score(truthb[:, nci], predict[:, nci], average=None)

            # Optimal threshold from PR curve, optimizes f-score
            precision, recall, thrpr = precision_recall_curve(truthb[:, nci], predict[:, nci])
            fscore = (2 * precision * recall) / (precision + recall + eps)
            ix = np.argmax(fscore)  # index of largest f1 score
            thresholds_opt_pr[nci] = thrpr[ix]

            # Optimal threshold from ROC curve, optimizes J-statistic (TPR-FPR) or gmean
            fpr, tpr, thrroc = roc_curve(truthb[:, nci], predict[:, nci])
            # J = tpr - fpr                  # J can result in thr > 1
            gmeans = np.sqrt(tpr * (1 - fpr))  # gmean seems better behaved
            ix = np.argmax(gmeans)
            thresholds_opt_roc[nci] = thrroc[ix]

    return thresholds_opt_pr, thresholds_opt_roc, AP, AUC
