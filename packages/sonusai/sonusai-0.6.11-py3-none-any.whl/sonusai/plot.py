"""sonusai plot

usage: plot [-hv] [-m MODEL] [-l CSV] [-i MIXID] [-o OUTPUT] INPUT

options:
   -h, --help
   -v, --verbose                Be verbose.
   -m MODEL, --model MODEL      Trained model ONNX file.
   -i MIXID, --mixid MIXID      Mixture to plot if input is HDF5.
   -l CSV, --labels CSV         Optional CSV file of class labels (from SonusAI gentcst).
   -o OUTPUT, --output OUTPUT   Optional output HDF5 file for prediction.

Plot SonusAI audio, feature, truth, and prediction data. INPUT must be one of three file types:

    * WAV
      Using the given model, generate feature data and run prediction. A model file must be
      provided. The MIXID is ignored.

    * JSON
      Using the given mixture database, generate feature and truth data. Run prediction if
      a model is given. The MIXID is required.

    * HDF5
      Using the given mixture database, generate feature and truth data. Run prediction if
      a model is given. The MIXID is required.

Prediction data will be written to OUTPUT if a model file is given and OUTPUT is specified.

There will be one plot per active truth index. In addition, the top 5 prediction classes are determined and
plotted if needed (i.e., if they were not already included in the truth plots). For plots generated using a
mixture database, then the target will also be displayed. If mixup is active, then each target involved will
be added to the corresponding truth plot.

Inputs:
    MODEL   A SonusAI trained ONNX model file. If a model file is given, prediction data will be
            generated.
    INPUT   A WAV file, or
            a JSON file containing a SonusAI mixture database, or
            an HDF5 file containing:
                attribute:  mixdb (required)

Outputs:
    {INPUT}-plot.pdf or {INPUT}-mix{MIXID}-plot.pdf
    plot.log
    OUTPUT (if MODEL and OUTPUT are both specified)

"""
from typing import List
from typing import Union

import matplotlib.pyplot as plt
import numpy as np

from sonusai import logger


def spec_plot(mixture: np.ndarray,
              spectrogram: np.ndarray,
              predict: Union[np.ndarray, None] = None,
              labels: Union[List[str], None] = None,
              title: str = '') -> plt.figure:
    from sonusai.mixture import SAMPLE_RATE
    from sonusai.utils import int16_to_float

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, constrained_layout=True, figsize=(11, 8.5))

    # Plot the waveform
    x_axis = np.arange(len(mixture), dtype=np.float32) / SAMPLE_RATE
    ax1.plot(x_axis, int16_to_float(mixture), label='Mixture')
    ax1.set_xlim(x_axis[0], x_axis[-1])
    ax1.set_ylim([-1.025, 1.025])

    # Plot the spectrogram
    ax2.imshow(np.transpose(spectrogram), aspect='auto', interpolation='nearest', origin='lower')

    if predict is not None:
        # Plot and label the model output scores for the top-scoring classes.
        mean_predict = np.mean(predict, axis=0)
        num_classes = predict.shape[-1]
        top_n = min(10, num_classes)
        top_class_indices = np.argsort(mean_predict)[::-1][:top_n]
        ax3.imshow(np.transpose(predict[:, top_class_indices]), aspect='auto', interpolation='nearest', cmap='gray_r')
        y_ticks = range(0, top_n)
        ax3.set_yticks(y_ticks, [labels[top_class_indices[x]] for x in y_ticks])
        ax3.set_ylim(-0.5 + np.array([top_n, 0]))

        # Plot the probabilities
        ax4.plot(predict[:, top_class_indices])
        ax4.legend(np.array(labels)[top_class_indices], loc='best')

    fig.suptitle(title)

    return fig


def class_plot(mixture: np.ndarray,
               target: Union[np.ndarray, None] = None,
               truth_f: Union[np.ndarray, None] = None,
               predict: Union[np.ndarray, None] = None,
               label: str = '') -> plt.figure:
    """
    Plot mixture waveform with optional prediction and/or truth together in a single plot.
    The target waveform can optionally be provided, and prediction and truth can have multiple classes.

    Inputs:
      mixture       required, numpy array (samples, 1)
      target        optional, list of numpy arrays (samples, 1)
      truth_f       optional, numpy array (frames, 1)
      predict       optional, numpy array (frames, 1)
      label         optional, label name to use when plotting

    """
    from sonusai import SonusAIError
    from sonusai.mixture import SAMPLE_RATE
    from sonusai.utils import int16_to_float

    if mixture.ndim != 1:
        raise SonusAIError('Too many dimensions in mixture')

    if target is not None and target.ndim != 1:
        raise SonusAIError('Too many dimensions in target')

    # Set default to 1 frame when there is no truth or predict data
    frames = 1
    if truth_f is not None and predict is not None:
        if truth_f.ndim != 1:
            raise SonusAIError('Too many dimensions in truth_f')
        t_frames = len(truth_f)

        if predict.ndim != 1:
            raise SonusAIError('Too many dimensions in predict')
        p_frames = len(predict)

        frames = min(t_frames, p_frames)
    elif truth_f is not None:
        if truth_f.ndim != 1:
            raise SonusAIError('Too many dimensions in truth_f')
        frames = len(truth_f)
    elif predict is not None:
        if predict.ndim != 1:
            raise SonusAIError('Too many dimensions in predict')
        frames = len(predict)

    samples = (len(mixture) // frames) * frames

    # x-axis in sec
    x_axis = np.arange(samples, dtype=np.float32) / SAMPLE_RATE

    fig, ax1 = plt.subplots(1, 1, constrained_layout=True, figsize=(11, 8.5))

    # Plot the time-domain waveforms then truth/prediction on second axis
    ax1.plot(x_axis, int16_to_float(mixture[0:samples]), color='mistyrose', label='Mixture')
    color = 'red'
    ax1.set_xlim(x_axis[0], x_axis[-1])
    ax1.set_ylim([-1.025, 1.025])
    ax1.set_ylabel(f'Amplitude', color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    # Plot target time-domain waveform
    if target is not None:
        ax1.plot(x_axis, int16_to_float(target[0:samples]), color='blue', label='Target')

    # instantiate 2nd y-axis that shares the same x-axis
    if truth_f is not None or predict is not None:
        y_label = 'Truth/Predict'
        if truth_f is None:
            y_label = 'Predict'
        if predict is None:
            y_label = 'Truth'

        ax2 = ax1.twinx()

        color = 'black'
        ax2.set_xlim(x_axis[0], x_axis[-1])
        ax2.set_ylim([-0.025, 1.025])
        ax2.set_ylabel(y_label, color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        if truth_f is not None:
            ax2.plot(x_axis, expand_frames_to_samples(truth_f, samples), color='green', label='Truth')

        if predict is not None:
            ax2.plot(x_axis, expand_frames_to_samples(predict, samples), color='brown', label='Predict')

    # set only on last/bottom plot
    ax1.set_xlabel('time (s)')

    fig.suptitle(label)

    return fig


def expand_frames_to_samples(x: np.ndarray, samples: int) -> np.ndarray:
    samples_per_frame = samples // len(x)
    return np.reshape(np.tile(np.expand_dims(x, 1), [1, samples_per_frame]), samples)


def main():
    from os.path import basename
    from os.path import exists
    from os.path import splitext

    import h5py
    from docopt import docopt
    from matplotlib.backends.backend_pdf import PdfPages
    from pyaaware import Predict

    import sonusai
    from sonusai import SonusAIError
    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import update_console_handler
    from sonusai.mixture import DEFAULT_FRAME_SIZE
    from sonusai.mixture import get_feature_from_audio
    from sonusai.mixture import get_feature_stats
    from sonusai.mixture import get_mixture_data
    from sonusai.mixture import get_truth_indices_for_mixid
    from sonusai.mixture import load_mixdb
    from sonusai.mixture import read_audio
    from sonusai.utils import get_label_names
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sonusai.__version__, options_first=True)

    verbose = args['--verbose']
    model_name = args['--model']
    output_name = args['--output']
    labels_name = args['--labels']
    mixid = args['--mixid']
    input_name = args['INPUT']

    if mixid is not None:
        mixid = int(mixid)

    log_name = 'plot.log'
    create_file_handler(log_name)
    update_console_handler(verbose)
    initial_log_messages('plot')

    if not exists(input_name):
        raise SonusAIError(f'{input_name} does not exist')

    logger.info('')
    logger.info(f'Input:  {input_name}')
    if model_name is not None:
        logger.info(f'Model:  {model_name}')
    if output_name is not None:
        logger.info(f'Output: {output_name}')
    logger.info('')

    ext = splitext(input_name)[1]

    model = None
    mixdb = None
    target = None
    truth_f = None
    t_indices = None

    if model_name is not None:
        model = Predict(model_name)

    if ext == '.wav':
        if model_name is None:
            raise SonusAIError('Must specify MODEL when input is WAV')

        mixture = read_audio(input_name)
        feature = get_feature_from_audio(audio=mixture, model=model)
        fs = get_feature_stats(feature_mode=model.feature,
                               frame_size=DEFAULT_FRAME_SIZE,
                               num_classes=model.output_shape[-1],
                               truth_mutex=model.mutex)
        feature_step_samples = fs.feature_step_samples
        feature_samples = fs.feature_samples

        logger.debug(f'Audio samples      {len(mixture)}')
        logger.debug(f'Feature shape      {feature.shape}')

    elif ext in ['.json', '.h5']:
        if mixid is None:
            raise SonusAIError('Must specify MIXID when input is JSON or H5')

        mixdb = load_mixdb(input_name)

        logger.info(f'Generating data for mixture {mixid}')
        md = get_mixture_data(mixdb=mixdb, mixid=mixid)
        mixture = md.mixture
        target = md.target
        feature = md.feature
        truth_f = md.truth_f
        feature_step_samples = mixdb.feature_step_samples
        feature_samples = mixdb.feature_samples
        t_indices = [x - 1 for x in get_truth_indices_for_mixid(mixdb=mixdb, mixid=mixid)]

        logger.debug(f'Audio samples      {len(mixture)}')
        logger.debug(f'Targets:')
        mixture_record = mixdb.mixtures[mixid]
        for n in range(len(mixture_record.target_file_index)):
            name = mixdb.targets[mixture_record.target_file_index[n]].name
            duration = mixdb.targets[mixture_record.target_file_index[n]].duration
            augmentation = mixdb.target_augmentations[mixture_record.target_augmentation_index[n]]
            logger.debug(f'  Name             {name}')
            logger.debug(f'  Duration         {duration}')
            logger.debug(f'  Augmentation     {augmentation}')

        logger.debug(f'Feature shape      {feature.shape}')
        logger.debug(f'Truth shape        {truth_f.shape}')

    else:
        raise SonusAIError(f'Unknown file type for {input_name}')

    logger.debug('')
    logger.info(f'Running prediction on mixture {mixid}')
    logger.debug(f'Model feature name {model.feature}')
    logger.debug(f'Model input shape  {model.input_shape}')
    logger.debug(f'Model output shape {model.output_shape}')
    predict = model.execute(feature)

    labels = get_label_names(num_labels=predict.shape[1], file=labels_name)

    # Report the highest-scoring classes and their scores.
    p_max = np.max(predict, axis=0)
    p_indices = np.argsort(p_max)[::-1][:5]
    p_max_len = max([len(labels[i]) for i in p_indices])

    logger.info('Top 5 active prediction classes by max:')
    for i in p_indices:
        logger.info(f'  {labels[i]:{p_max_len}s} {p_max[i]:.3f}')
    logger.info('')

    indices = list(p_indices)
    if t_indices is not None:
        indices += t_indices
    indices = sorted(list(set(indices)))

    base_name = basename(splitext(input_name)[0])
    if mixdb is not None:
        title = f'{input_name} Mixture {mixid}'
        pdf_name = f'{base_name}-mix{mixid}-plot.pdf'
    else:
        title = f'{input_name}'
        pdf_name = f'{base_name}-plot.pdf'

    # Original size (frames, stride, num_bands)
    # Decimate by (feature_step_samples // feature_samples) in the stride dimension
    # Reshape to get frames*decimated_stride, num_bands
    if feature.ndim != 3:
        raise SonusAIError(f'feature does not have 3 dimensions: frames, stride, num_bands')
    decimation = feature_step_samples // feature_samples
    spectrogram = feature[:, ::decimation, :]
    spectrogram = np.reshape(spectrogram, (spectrogram.shape[0] * spectrogram.shape[1], spectrogram.shape[2]))

    with PdfPages(pdf_name) as pdf:
        pdf.savefig(spec_plot(mixture=mixture,
                              spectrogram=spectrogram,
                              predict=predict,
                              labels=labels,
                              title=title))
        for index in indices:
            pdf.savefig(class_plot(mixture=mixture,
                                   target=target[index],
                                   truth_f=truth_f[:, index],
                                   predict=predict[:, index],
                                   label=labels[index]))
        logger.info(f'Wrote {pdf_name}')

    if output_name:
        with h5py.File(name=output_name, mode='w') as f:
            f.create_dataset(name='predict', data=predict)
            logger.info(f'Wrote {output_name}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        raise SystemExit(0)
