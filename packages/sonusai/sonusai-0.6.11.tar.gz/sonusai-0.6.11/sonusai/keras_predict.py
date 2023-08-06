"""sonusai keras_predict

usage: keras_predict [-hvfc] (-m MODEL) (-w KMODEL) [-b BATCH] [-t TSTEPS] DATA

options:
   -h, --help
   -v, --verbose                Be verbose.
   -f, --flatten                Flatten input feature data.
   -c, --add1ch                 Add channel dimension to feature (i.e., cnn input).
   -m MODEL, --model MODEL      Model Python file with build and/or hypermodel functions.
   -w KMODEL, --weights KMODEL  Keras model HDF5 file with weights.
   -b BATCH, --batch BATCH      Batch size. [default: 1].
   -t TSTEPS, --tsteps TSTEPS   Timesteps. [default: 0].

Run Keras prediction on a model defined by a Python definition file and using
DATA HDF5 feature+truth data generated from the SonusAI genft function.

Results are written into subdirectory predict-<DATA>-<TIMESTAMP>

"""
from sonusai import logger


def main():
    from docopt import docopt

    import sonusai
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sonusai.__version__, options_first=True)

    import os
    from datetime import datetime

    import h5py
    import keras2onnx
    import keras_tuner as kt
    import numpy as np
    import tensorflow as tf
    from tensorflow.keras import backend as kb

    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import update_console_handler
    from sonusai.metrics import class_summary
    from sonusai.metrics import snr_summary
    from sonusai.mixture import load_mixdb
    from sonusai.utils import calculate_input_shape
    from sonusai.utils import create_onnx_from_keras
    from sonusai.utils import import_keras_model
    from sonusai.utils import reshape_inputs

    verbose = args['--verbose']
    flatten = args['--flatten']
    add1ch = args['--add1ch']
    model_name = args['--model']
    kmodel_name = args['--weights']
    batch_size = int(args['--batch'])
    timesteps = int(args['--tsteps'])
    data_name = args['DATA']

    model_tail = os.path.basename(model_name)
    data_tail = os.path.basename(data_name)
    data_root = os.path.splitext(data_tail)[0]

    # Results subdirectory
    ts = datetime.now()

    # First try just date
    ts_str = 'predict-' + data_root + '-' + ts.strftime('%Y%m%d')
    try:
        os.mkdir(ts_str)
    except OSError as _:
        # add hour-min-sec if necessary
        ts_str = 'predict-' + data_root + '-' + ts.strftime('%Y%m%d-%H%M%S')
        os.mkdir(ts_str)

    # Setup logging file
    name_ts = ts_str + '/' + 'predict'  # base filename path with subdir timestamp
    create_file_handler(name_ts + '.log')
    update_console_handler(verbose)
    initial_log_messages('predict-' + data_root)

    # Check dims and model build before we read large dataset and make subdir and start logging
    logger.info(f'TF ver: {tf.__version__}')
    logger.info(f'Keras ver: {tf.keras.__version__}')
    logger.info(f'Keras2onnx ver: {keras2onnx.__version__}')

    mixdb = load_mixdb(data_name)
    mixid = list(range(len(mixdb.mixtures)))
    logger.info(f'Found {len(mixid)} mixtures with {mixdb.num_classes} classes from {data_name}')

    # Import model definition file
    model = import_keras_model(model_name)
    logger.info(f'Successfully imported {model_tail}, testing default model build')

    # Calculate input shape
    logger.info('Building default model')
    in_shape = calculate_input_shape(mixdb.feature, flatten, timesteps, add1ch)

    try:
        hypermodel = model.MyHyperModel(input_shape=in_shape, num_classes=mixdb.num_classes, batch_size=batch_size)
        model_default = hypermodel.build_model(kt.HyperParameters())
    except Exception as e:
        logger.exception(f'Error: build_model() in {model_tail} failed: {e}.')
        raise SystemExit(1)

    logger.info(f'Successfully built using {model_tail}, summary:')
    kb.clear_session()
    logger.info('')
    model_default.summary(print_fn=logger.info)
    logger.info(f'User shape params: batch_size {batch_size}, timesteps {timesteps}, '
                f'flatten={flatten}, add1ch={add1ch}')
    logger.info(f'Model build above with default hyper-parameters, in_shape: {in_shape}, '
                f'num_classes {mixdb.num_classes}')
    logger.info(f'Compiled with optimizer: {model_default.optimizer.get_config()}')
    logger.info('')

    logger.info(f'Loading weights from {kmodel_name}')
    model_default.load_weights(kmodel_name)
    logger.info(f'Loading feature+truth data from {data_name} with {len(mixid)} mixtures '
                f'with {mixdb.num_classes} classes')
    with h5py.File(data_name, 'r') as f:
        feature = np.array(f['feature'])
        truth_f = np.array(f['truth_f'])

    logger.info('Reshaping data')
    feature, truth, in_shape, outlen, _, _ = reshape_inputs(feature, truth_f, batch_size, timesteps, flatten, add1ch)

    # Save to ONNX format
    try:
        create_onnx_from_keras(keras_model=model_default,
                               is_flattened=flatten,
                               has_timestep=(timesteps != 0),
                               has_channel=add1ch,
                               is_mutex=mixdb.truth_mutex,
                               feature=mixdb.feature,
                               filename=name_ts + '.onnx')
    except Exception as e:
        logger.info(f'Failed to create ONNX model, no file saved: {e}.')

    # Compute prediction and metrics on data
    logger.info('Running Keras prediction')
    predict = model_default.predict(feature, batch_size=batch_size, verbose=1)
    with h5py.File(name_ts + '-metrics.h5', 'w') as f:
        f.create_dataset('predict', data=predict)
        f.create_dataset('truth_f', data=truth)

        logger.info(f'Metrics per class over {len(mixid)} mixtures:')
        # Use default prediction threshold
        classdf = class_summary(mixdb=mixdb,
                                mixid=mixid,
                                truth_f=truth,
                                predict=predict)
        logger.info(classdf.round(3).to_string())
        logger.info('')
        f.create_dataset('classdf', data=classdf)

        snr_macrodf, snr_microdf, _, _ = snr_summary(mixdb=mixdb,
                                                     mixid=mixid,
                                                     truth_f=truth,
                                                     predict=predict)
        logger.info(f'Metrics micro-avg per SNR over all {len(mixid)} mixtures:')
        logger.info(snr_microdf.round(3).to_string())
        logger.info('\n')
        f.create_dataset('snr_macrodf', data=snr_macrodf)
        f.create_dataset('snr_microdf', data=snr_microdf)

    # Create and save model with timesteps, batch = 1
    logger.info('')
    if timesteps > 0:
        # only set to 1 if nonzero (exists)
        timesteps = 1
    in_shape = calculate_input_shape(feature=mixdb.feature,
                                     flatten=flatten,
                                     timesteps=timesteps,
                                     add1ch=add1ch)
    hypermodel = model.MyHyperModel(input_shape=in_shape,
                                    num_classes=mixdb.num_classes,
                                    batch_size=1)
    modelp = hypermodel.build_model(kt.HyperParameters())
    # load weights from previously saved HDF5
    modelp.load_weights(kmodel_name)

    # save a prediction version of model to name_ts-predict-onnx
    create_onnx_from_keras(keras_model=modelp,
                           is_flattened=flatten,
                           has_timestep=(timesteps != 0),
                           has_channel=add1ch,
                           is_mutex=mixdb.truth_mutex,
                           feature=mixdb.feature,
                           filename=name_ts + '-b1.onnx')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        exit()
