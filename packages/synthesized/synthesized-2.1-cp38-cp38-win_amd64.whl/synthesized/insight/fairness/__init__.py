from synthesized._licence import OptionalFeature, verify

verify(OptionalFeature.FAIRNESS)

from .bias_mitigator import BiasMitigator
from .fairness_scorer import FairnessScorer

__all__ = ["FairnessScorer", "BiasMitigator"]
