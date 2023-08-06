"""Synthesized Licence and feature flagging subpackage.

This subpackage contains the licence and feature flagging functionality for Synthesized.
It is used to load the licence key, verify the licence, and check that given features are
enabled.

Utilty functions related to the licence are defined in the `licence` submodule. There are two
public global variables defined here.

    - `licence.EXPIRY_DATE`: The expiry date of the licence.
    - `licence.FEATURES`: The features enabled by the licence.

These variables are never used directly when evaluating the licence. Instead, these
variables are always redetermined from `_KEY` – an RSA encrypted string. This way user can't
change available features or expiry date,

Most importantly, the `verify` function can be used throughout the codebase to check that the
licence is valid for a given feature.

Modules:
    analytics.py: Util functions for sentry and segment (our tracking libraries).
    exceptions.py: Possible licence exceptions.
    features.py: Optional features are defined here.
    licence.py: Licence loading and verifying functions.
"""
import base64
import json
import sys

from synthesized._licence.exceptions import (
    ColabLicenceError,
    FeatureUnavailableError,
    LicenceError,
    LicenceExpiredError,
    LicenceSignatureError,
    LicenceWarning,
)
from synthesized._licence.features import OptionalFeature

from synthesized._licence.prompt import prompt_for_licence  # isort: skip

from synthesized._licence import licence  # isort: skip

from .analytics import (  # isort:skip
    check_colab_environemnt,
    maybe_register_analytics,
    maybe_register_sentry,
    track,
    track_values,
)


verify = licence.verify

if not licence.is_key_set():
    prompt_for_licence()

try:
    verify()
    assert licence._KEY is not None
    data = base64.b64decode(licence._KEY).decode("utf-8")
    email: str = json.loads(data[88:])["email"]

    try:
        verify(OptionalFeature.LOCAL_PACKAGE)
    except FeatureUnavailableError:
        check_colab_environemnt()

    try:
        verify(OptionalFeature.NO_ANALYTICS)
    except FeatureUnavailableError:
        maybe_register_sentry(email)
        maybe_register_analytics(licence._KEY, email)

except LicenceError as e:
    sys.exit(e)

__all__ = [
    "OptionalFeature",
    "verify",
    "LicenceError",
    "LicenceExpiredError",
    "ColabLicenceError",
    "LicenceWarning",
    "FeatureUnavailableError",
    "LicenceSignatureError",
]
