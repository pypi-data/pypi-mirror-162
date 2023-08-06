from typing import List

from sonusai.mixture.constants import DEFAULT_FRAME_SIZE


def calculate_input_shape(feature: str,
                          flatten: bool = False,
                          timesteps: int = 0,
                          add1ch: bool = False,
                          frame_size=DEFAULT_FRAME_SIZE) -> List[int]:
    """
    Calculate input shape given feature and user-specified reshape parameters.

    Inputs:
        feature:     String defining the Aaware feature used in SonusAI, typically  mixdb.feature.
        flatten:     If true, flatten the 2D spectrogram from SxB to S*B.
        timesteps:   Pre-pend timesteps dimension if non-zero, size = timesteps.
        add1ch:      Append channel dimension of size 1, (channel last).
        frame_size:  The default SonusAI frame size should always be used for now.
    """
    from pyaaware import FeatureGenerator

    # num_classes is irrelevant, set to 2
    fg = FeatureGenerator(frame_size=frame_size,
                          feature_mode=feature,
                          num_classes=2)

    if flatten:
        in_shape = [fg.stride * fg.num_bands]
    else:
        in_shape = [fg.stride, fg.num_bands]

    if timesteps > 0:
        in_shape.insert(0, timesteps)

    if add1ch:
        in_shape.append(1)

    return in_shape
