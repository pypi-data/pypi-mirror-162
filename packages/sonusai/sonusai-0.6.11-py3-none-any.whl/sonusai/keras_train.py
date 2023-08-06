"""sonusai keras_train

usage: keras_train [-hvfc] (-m MODEL) [-e EPOCHS] [-b BATCH] [-t TSTEPS] [-l VAL] DATA

options:
   -h, --help
   -v, --verbose                Be verbose.
   -f, --flatten                Flatten input feature data.
   -c, --add1ch                 Add channel dimension to feature (i.e., cnn input).
   -m MODEL, --model MODEL      Model Python file with build and/or hypermodel functions.
   -e EPOCHS --epochs EPOCHS    Number of epochs to use in training. [default: 8].
   -b BATCH, --batch BATCH      Batch size. [default: 32].
   -t TSTEPS, --tsteps TSTEPS   Timesteps.  [default: 0].
   -l VAL, --val VAL            Validation split (0 - 1) or validation HDF5 file. [default: 0.2].

Use Keras to train a model defined by a Python definition file and DATA HDF5 feature+truth file
generated from the SonusAI genft function.

Validation is loaded from VAL if HDF5 file or created from DATA using a split of VAL.

Results are written into subdirectory <MODEL>-<TIMESTAMP>

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
    from tensorflow.keras.callbacks import EarlyStopping

    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import update_console_handler
    from sonusai.data_generator import DataGenerator
    from sonusai.genft import genft
    from sonusai.metrics import class_summary
    from sonusai.metrics import snr_summary
    from sonusai.mixture import get_ft_from_file
    from sonusai.mixture import get_total_class_count
    from sonusai.mixture import load_mixdb
    from sonusai.mixture import new_mixdb_from_mixid
    from sonusai.utils import calculate_input_shape
    from sonusai.utils import create_onnx_from_keras
    from sonusai.utils import import_keras_model
    from sonusai.utils import reshape_inputs
    from sonusai.utils import stratified_shuffle_split_mixid

    verbose = args['--verbose']
    flatten = args['--flatten']
    add1ch = args['--add1ch']
    model_name = args['--model']
    epochs = int(args['--epochs'])
    batch_size = int(args['--batch'])
    timesteps = int(args['--tsteps'])
    val_name = args['--val']
    data_name = args['DATA']

    model_tail = os.path.basename(model_name)
    model_root = os.path.splitext(model_tail)[0]

    # Results subdirectory
    ts = datetime.now()

    # First try just date
    ts_str = model_root + '-' + ts.strftime('%Y%m%d')
    try:
        os.mkdir(ts_str)
    except OSError as _:
        # add hour-min-sec if necessary
        ts_str = model_root + '-' + ts.strftime('%Y%m%d-%H%M%S')
        os.mkdir(ts_str)

    # Setup logging file
    name_ts = ts_str + '/' + model_root  # base filename path with subdir timestamp
    create_file_handler(name_ts + '.log')
    update_console_handler(verbose)
    initial_log_messages(model_root)

    # Check dims and model build before we read large dataset and make subdir and start logging
    logger.info(f'TF ver: {tf.__version__}')
    logger.info(f'Keras ver: {tf.keras.__version__}')
    logger.info(f'Keras2onnx ver: {keras2onnx.__version__}')

    mixdb = load_mixdb(data_name)
    num_mixtures = len(mixdb.mixtures)
    logger.info(f'Found {num_mixtures} mixtures with {mixdb.num_classes} classes from {data_name}')

    # Import model definition file
    model = import_keras_model(model_name)
    logger.info(f'Successfully imported {model_tail}, testing default model build')

    # Calculate input shape
    logger.info('Building default model')
    in_shape = calculate_input_shape(feature=mixdb.feature,
                                     flatten=flatten,
                                     timesteps=timesteps,
                                     add1ch=add1ch)

    try:
        hypermodel = model.MyHyperModel(input_shape=in_shape,
                                        num_classes=mixdb.num_classes,
                                        batch_size=batch_size)
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

    # Prepare validation data
    v_mixdb = None
    v_feature = None
    v_truth = None
    vsplit = None
    try:
        vsplit = float(val_name)
        if vsplit < 0 or vsplit > 1:
            logger.exception('--val must be between 0 and 1')
            raise SystemExit(1)
    except ValueError:
        try:
            val_head, val_tail = os.path.split(val_name)
            val_ext = os.path.splitext(val_tail)[1]
            v_mixdb = load_mixdb(val_name)
            if val_ext == '.h5':
                v_feature, v_truth = get_ft_from_file(val_name)
            else:
                # JSON - generate feature-truth data
                v_feature, v_truth, _, _ = genft(mixdb=v_mixdb, mixid=':', show_progress=verbose)

        except Exception as e:
            logger.warning(f'Error {e}. Using vsplit=0.2 instead of --val={val_name}')
            vsplit = 0.2

    if v_mixdb is not None:
        # If validation data provided, then use it instead of split
        logger.info(f'Read {len(v_mixdb.mixtures)} validation mixtures from {val_name}')
        logger.info(f'Stratify/shuffle all {num_mixtures} training mixtures')
        # Training data does not need to be split; use all mixtures from mixdb
        t_mixid, _, _, _ = stratified_shuffle_split_mixid(mixdb, vsplit=0)
    else:
        # vsplit from --val arg or default = 0.2
        logger.info(f'Calculating validation data using split of {vsplit}')
        t_mixid, v_mixid, t_num_mixid, v_num_mixid = stratified_shuffle_split_mixid(mixdb, vsplit=vsplit)
        logger.info(f'Split {len(v_mixid)} validation mixtures')
        v_feature, v_truth = get_ft_from_file(filename=data_name, mixid=v_mixid)
        v_mixdb = new_mixdb_from_mixid(mixdb, v_mixid)

    v_mixid = list(range(len(v_mixdb.mixtures)))
    logger.info(f'Original validation data shape: {v_feature.shape}')
    v_feature, v_truth, _, _, _, _ = reshape_inputs(feature=v_feature,
                                                    truth=v_truth,
                                                    batch_size=batch_size,
                                                    timesteps=timesteps,
                                                    flatten=flatten,
                                                    add1ch=add1ch)
    logger.info(f'Final validation data shape: {v_feature.shape}')

    # Prepare class weighting
    class_featcnt = np.ceil(np.array(get_total_class_count(mixdb, t_mixid)) / mixdb.feature_step_samples)
    if mixdb.truth_mutex:
        oweight = 16.0
        logger.info(f'Detected single-label mode (truth_mutex), setting other weight to {oweight}')
        class_featcnt[-1] = class_featcnt[-1] / oweight

    total_features = sum(class_featcnt)
    cweights = np.zeros(mixdb.num_classes)
    for n in range(mixdb.num_classes):
        # Avoid non-existent problem in sklearn by setting to 0
        cweights[n] = total_features / (mixdb.num_classes * class_featcnt[n]) if class_featcnt[n] else 0

    logger.info(f'Final class weights: {cweights}')

    t_feature = None
    t_truth = None
    t_datagen = None

    memory_enough = True
    if memory_enough:
        # Read train+truth into memory and reshape
        logger.info(f'Reading {len(t_mixid)} training mixtures into memory')
        t_feature, t_truth = get_ft_from_file(filename=data_name, mixid=t_mixid)
        logger.info(f'Reshaping training data')
        t_feature, t_truth, _, _, _, _ = reshape_inputs(feature=t_feature,
                                                        truth=t_truth,
                                                        batch_size=batch_size,
                                                        timesteps=timesteps,
                                                        flatten=flatten,
                                                        add1ch=add1ch)
        class_truth_cnt = sum(t_truth)
        fframes = t_truth.shape[0]
        ctweights = np.zeros(mixdb.num_classes)
        for n in range(mixdb.num_classes):
            ctweights[n] = fframes / (class_truth_cnt[n]) if class_truth_cnt[n] else 1
    else:
        # Use SonusAI DataGenerator to create training+truth on the fly
        logger.info(f'Split {len(t_mixid)} training mixtures')
        t_datagen = DataGenerator(filename=data_name,
                                  mixid=t_mixid,
                                  batch_size=batch_size,
                                  timesteps=timesteps,
                                  flatten=flatten,
                                  add1ch=add1ch)

    es_p = 8
    es = EarlyStopping(monitor='val_loss',
                       mode='min',
                       verbose=1,
                       patience=es_p)
    ckpt_callback = tf.keras.callbacks.ModelCheckpoint(filepath=name_ts + '-ckpt',
                                                       save_weights_only=True,
                                                       monitor='val_map',
                                                       mode='max',
                                                       save_best_only=True)

    logger.info('')
    logger.info(f'Training with no class weighting and early stopping patience = {es_p}')
    logger.info('')

    if memory_enough:
        history = model_default.fit(t_feature, t_truth,
                                    batch_size=batch_size,
                                    epochs=epochs,
                                    validation_data=(v_feature, v_truth),
                                    shuffle=False,
                                    callbacks=[es, ckpt_callback])
    else:
        history = model_default.fit(t_datagen,
                                    batch_size=batch_size,
                                    epochs=epochs,
                                    validation_data=(v_feature, v_truth),
                                    shuffle=False,
                                    callbacks=[es, ckpt_callback])

    # Save history into numpy file
    history_name = name_ts + '-history'
    np.save(history_name, history.history)
    # Reload with: history=np.load(history_name, allow_pickle='TRUE').item()
    logger.info(f'Saved training history to numpy file {history_name}.npy')
    model_default.save(name_ts + '.h5')
    logger.info(f'Saved trained model to {name_ts}.h5')

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
        logger.warning(f'Failed to create ONNX model, no file saved: {e}.')

    # Compute prediction metrics on validation data
    # t_mixid, v_mixid, or entire dataset mixdb
    logger.info('Running Keras prediction on validation data')
    v_predict = model_default.predict(v_feature, batch_size=batch_size, verbose=1)
    with h5py.File(name_ts + '-metrics.h5', 'w') as f:
        f.create_dataset('predict', data=v_predict)
        f.create_dataset('truth_f', data=v_truth)

        logger.info(f'Metrics per class over {len(v_mixid)} mixtures:')
        # Use default prediction threshold
        classdf = class_summary(mixdb=v_mixdb,
                                mixid=v_mixid,
                                truth_f=v_truth,
                                predict=v_predict)
        logger.info(classdf.round(3).to_string())
        logger.info('')
        f.create_dataset('classdf', data=classdf)

        snr_macrodf, snr_microdf, _, _ = snr_summary(mixdb=v_mixdb,
                                                     mixid=v_mixid,
                                                     truth_f=v_truth,
                                                     predict=v_predict)
        logger.info(f'Metrics micro-avg per SNR over all {len(v_mixid)} mixtures:')
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
    modelp.load_weights(name_ts + '.h5')
    # save a prediction version of model to name_ts-pred-onnx
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
