try:
    from .version import __version__
except ModuleNotFoundError:
    from importlib_metadata import version as _version

    __version__ = _version("synthesized")
import os
import warnings

if os.environ.get("SYNTHESIZED_TP_WARNINGS", "false").lower() != "true":
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    import tensorflow as tf

    tf.get_logger().setLevel("ERROR")
    tf.autograph.set_verbosity(0)
    for module in ["numpy", "pandas", "sklearn", "tensorflow"]:
        warnings.filterwarnings("ignore", module=module, append=True)

import synthesized._licence as _licence

from .common.synthesizer import Synthesizer
from .complex.conditional import ConditionalSampler
from .complex.data_imputer import DataImputer
from .complex.highdim import HighDimSynthesizer
from .complex.multi_table import TwoTableSynthesizer
from .complex.two_table import TwoTableDeepSynthesizer
from .metadata.data_frame_meta import DataFrameMeta
from .metadata.factory import MetaExtractor

__all__ = [
    "__version__",
    "HighDimSynthesizer",
    "ConditionalSampler",
    "DataImputer",
    "Synthesizer",
    "DataFrameMeta",
    "MetaExtractor",
    "TwoTableSynthesizer",
    "TwoTableDeepSynthesizer",
    "_licence",
]
