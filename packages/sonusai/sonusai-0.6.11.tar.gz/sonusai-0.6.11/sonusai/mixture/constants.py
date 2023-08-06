import os
import re

import sonusai

VALID_AUGMENTATIONS = ['normalize', 'gain', 'pitch', 'tempo', 'eq1', 'eq2', 'eq3', 'lpf', 'count', 'mixup']
RAND_PATTERN = re.compile(r'rand\(([-+]?(\d+(\.\d*)?|\.\d+)),\s*([-+]?(\d+(\.\d*)?|\.\d+))\)')
SAMPLE_RATE = 16000
BIT_DEPTH = 16
CHANNEL_COUNT = 1
SAMPLE_BYTES = int(BIT_DEPTH / 8)
FLOAT_BYTES = 4
DEFAULT_FRAME_SIZE = 64

DEFAULT_NOISE = os.path.join(sonusai.BASEDIR, 'data', 'whitenoise.wav')
DEFAULT_CONFIG = os.path.join(sonusai.BASEDIR, 'data', 'genmixdb.yml')
