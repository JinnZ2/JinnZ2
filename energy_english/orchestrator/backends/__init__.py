# energy_english/orchestrator/backends/__init__.py
"""
Backend registry for the L3 orchestrator.

Importing this package does NOT eagerly import every backend — backends
that depend on optional packages (boto3, modal) are loaded lazily so a
model-only or local-only setup doesn't fail on import.
"""

from energy_english.orchestrator.backends.docker import DockerRuntime
from energy_english.orchestrator.backends.http import HTTPRuntime
from energy_english.orchestrator.backends.local import LocalRuntime


__all__ = [
    "DockerRuntime",
    "HTTPRuntime",
    "LocalRuntime",
    "load_aws_lambda_runtime",
    "load_modal_runtime",
]


def load_aws_lambda_runtime():
    """Lazy import. Raises BackendUnavailable if boto3 is missing."""
    from energy_english.orchestrator.backends.aws_lambda import AWSLambdaRuntime
    return AWSLambdaRuntime


def load_modal_runtime():
    """Lazy import. Raises BackendUnavailable if modal is missing."""
    from energy_english.orchestrator.backends.modal_runtime import ModalRuntime
    return ModalRuntime
