# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator API: CLI argument plumbing and deploy-artifact generation.

When the upstream ``aiconfigurator`` package is available, all public symbols
are re-exported from ``aiconfigurator.generator.api``. Otherwise the minimal
fallbacks below keep the search CLI functional; artifact generation that
requires the upstream dynamo config generator degrades to a warning.
"""

from __future__ import annotations

import logging
import shlex

logger = logging.getLogger(__name__)

try:  # Prefer upstream implementation when available.
    from aiconfigurator.generator.api import (  # type: ignore # noqa: F401
        add_generator_override_arguments,
        generate_backend_artifacts,
        generate_naive_config,
        generator_cli_helper,
        get_default_dynamo_version_mapping,
        load_generator_overrides_from_args,
        resolve_backend_version_for_dynamo,
    )

    _UPSTREAM = True
except ImportError:
    _UPSTREAM = False


# ---------------------------------------------------------------------------
# Fallback implementations (used when the upstream package is not installed)
# ---------------------------------------------------------------------------

def _noop_add_generator_override_arguments(parser) -> None:
    """Add the generator override CLI arguments (upstream-compatible subset)."""
    group = parser.add_argument_group("generator overrides")
    group.add_argument(
        "--generator-dynamo-version",
        dest="generator_dynamo_version",
        type=str,
        default=None,
        help="Dynamo version to generate configs for (backend versions are mapped from it).",
    )
    group.add_argument(
        "--generated-config-version",
        dest="generated_config_version",
        type=str,
        default=None,
        help="Backend version used for the generated deploy configs (overrides defaults).",
    )
    group.add_argument(
        "--generator-set",
        dest="generator_set",
        action="append",
        type=str,
        default=[],
        metavar="KEY=VALUE",
        help="Generator override, e.g. --generator-set K8sConfig.k8s_pvc_name=my-pvc.",
    )


def _noop_generator_cli_helper(argv: list[str]) -> bool:
    """Fallback for upstream hidden generator subcommands; never handled here."""
    return False


def _load_generator_overrides_from_args(args) -> dict:
    """Collect generator overrides from parsed CLI args into a flat dict."""
    overrides: dict = {}
    for name in ("generator_dynamo_version", "generated_config_version"):
        value = getattr(args, name, None)
        if value:
            overrides[name] = value
    for item in getattr(args, "generator_set", None) or []:
        if "=" in item:
            key, value = item.split("=", 1)
            overrides[key.strip()] = value.strip()
        else:
            logger.warning("Ignoring malformed --generator-set entry: %s", item)
    return overrides


_FALLBACK_BACKEND_VERSIONS = {
    "trtllm": "latest",
    "vllm": "latest",
    "vllm-ascend": "latest",
    "sglang": "latest",
}


def _get_default_dynamo_version_mapping() -> tuple[str | None, dict[str, str]]:
    """Fallback default mapping; labels configs with 'latest' per backend."""
    return "latest", dict(_FALLBACK_BACKEND_VERSIONS)


def _resolve_backend_version_for_dynamo(dynamo_version: str, backend_name: str | None = None):
    """Fallback resolver: version mapping tables live in the upstream package."""
    logger.warning(
        "Upstream aiconfigurator is not installed; using 'latest' as the "
        "backend version for dynamo %s. Pass --generated-config-version to pin it.",
        dynamo_version,
    )
    if backend_name is not None:
        return "latest"
    return dict(_FALLBACK_BACKEND_VERSIONS)


def _generate_backend_artifacts(
    params: dict,
    backend: str,
    backend_version: str,
    output_dir: str,
    use_dynamo_generator: bool = True,
) -> None:
    """Fallback: skip deploy-artifact generation (shell scripts / k8s manifests).

    ``generator_config.yaml`` is still written by the caller, so the resolved
    configuration is not lost.
    """
    logger.warning(
        "Upstream aiconfigurator is not installed: skipping deploy artifact "
        "generation for backend %s (%s). Only generator_config.yaml is saved. "
        "Install it with: pip install aiconfigurator "
        "--extra-index-url https://pypi.nvidia.com/",
        backend,
        backend_version,
    )


def _generate_naive_config(
    model_path: str,
    total_gpus: int,
    system: str,
    backend: str = "trtllm",
    output_dir: str = "./output",
) -> dict:
    """Fallback: naive config generation requires the upstream generator."""
    raise NotImplementedError(
        "The 'generate' mode requires the upstream config generator, which is not "
        "installed in this environment. Install it with: "
        "pip install aiconfigurator --extra-index-url https://pypi.nvidia.com/ "
        "Alternatively use 'aic-npu cli default' for the full SLA-driven sweep."
    )


if not _UPSTREAM:
    add_generator_override_arguments = _noop_add_generator_override_arguments
    generator_cli_helper = _noop_generator_cli_helper
    load_generator_overrides_from_args = _load_generator_overrides_from_args
    get_default_dynamo_version_mapping = _get_default_dynamo_version_mapping
    resolve_backend_version_for_dynamo = _resolve_backend_version_for_dynamo
    generate_backend_artifacts = _generate_backend_artifacts
    generate_naive_config = _generate_naive_config


__all__ = [
    "add_generator_override_arguments",
    "generate_backend_artifacts",
    "generate_naive_config",
    "generator_cli_helper",
    "get_default_dynamo_version_mapping",
    "load_generator_overrides_from_args",
    "resolve_backend_version_for_dynamo",
]
