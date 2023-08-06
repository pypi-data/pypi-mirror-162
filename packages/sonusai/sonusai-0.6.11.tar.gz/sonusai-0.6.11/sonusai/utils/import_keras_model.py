from typing import Any


def import_keras_model(name: str) -> Any:
    import os
    import sys
    from importlib import import_module

    from sonusai import SonusAIError

    try:
        path = os.path.dirname(name)
        if len(path) < 1:
            path = './'

        # Add model file location to system path
        sys.path.append(os.path.abspath(path))

        try:
            # expect at least a Keras-tuner build_model(hp) function
            root = os.path.splitext(os.path.basename(name))[0]
            model = import_module(root)
        except Exception as e:
            raise SonusAIError(f'Error: could not import model from {name}: {e}.')
    except Exception as e:
        raise SonusAIError(f'Error: could not find {name}: {e}.')

    return model
