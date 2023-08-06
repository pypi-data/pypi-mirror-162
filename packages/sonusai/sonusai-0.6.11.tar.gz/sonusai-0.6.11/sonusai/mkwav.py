"""sonusai mkwav

usage: mkwav [-htn] [-i MIXID] MIXDB

options:
   -h, --help
   -i MIXID, --mixid MIXID      Mixture ID to generate. [default: 0].
   -t, --target                 Write target file.
   -n, --noise                  Write noise file.

The mkwav command creates WAV files from a SonusAI database.

Inputs:
    MIXDB       A SonusAI mixture database JSON file or an HDF5 file containing a SonusAI mixture database.
                The HDF5 file contains:
                    attribute:  mixdb

"""

import numpy as np

from sonusai import logger
from sonusai.mixture import MixtureDatabase


def mkwav(mixdb: MixtureDatabase, mixid: int) -> (np.ndarray, np.ndarray):
    from sonusai.genmix import genmix

    mixture, _, target, noise, _, _ = genmix(mixdb=mixdb, mixid=[mixid])
    return mixture, target, noise


def _write_wav(name: str, data: np.ndarray) -> None:
    import wave

    from sonusai.mixture import CHANNEL_COUNT
    from sonusai.mixture import SAMPLE_BYTES
    from sonusai.mixture import SAMPLE_RATE

    with wave.open(name, mode='w') as f:
        f.setnchannels(CHANNEL_COUNT)
        f.setsampwidth(SAMPLE_BYTES)
        f.setframerate(SAMPLE_RATE)
        f.writeframesraw(data)
        logger.info(f'Wrote {name}')


def main():
    from os.path import basename
    from os.path import splitext

    from docopt import docopt

    import sonusai
    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import update_console_handler
    from sonusai.mixture import load_mixdb
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sonusai.__version__, options_first=True)

    mixdb_name = args['MIXDB']
    mixid = int(args['--mixid'])

    log_name = 'mkwav.log'
    create_file_handler(log_name)
    update_console_handler(False)
    initial_log_messages('mkwav')

    mixdb = load_mixdb(mixdb_name)

    mixture, target, noise = mkwav(mixdb=mixdb, mixid=mixid)

    base_name = basename(splitext(mixdb_name)[0])
    _write_wav(name=f'{base_name}_mixture_{mixid}.wav', data=mixture)
    if args['--target']:
        _write_wav(name=f'{base_name}_target_{mixid}.wav', data=target)
    if args['--noise']:
        _write_wav(name=f'{base_name}_noise_{mixid}.wav', data=noise)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        raise SystemExit(0)
