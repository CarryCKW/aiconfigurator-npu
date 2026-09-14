# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Bridge from search-engine TaskConfig to the dynamo generator config format.

Prefers the upstream ``aiconfigurator.generator.module_bridge`` when installed;
otherwise converts the TaskConfig YAML into a generator-compatible dict so that
``generator_config.yaml`` remains meaningful without the upstream package.
"""

from __future__ import annotations

import logging

import yaml

logger = logging.getLogger(__name__)

try:  # Prefer upstream implementation when available.
    from aiconfigurator.generator.module_bridge import (  # type: ignore # noqa: F401
        task_config_to_generator_config,
    )

    _UPSTREAM = True
except ImportError:
    _UPSTREAM = False


def _fallback_task_config_to_generator_config(
    task_config,
    result_df=None,
    generator_overrides: dict | None = None,
) -> dict:
    """Convert a TaskConfig into a generator config dict.

    The upstream version maps results onto dynamo deploy parameters. Without
    it, we emit the task config YAML (mode + config) enriched with the runtime
    parallelism fields present in the winning result row, which keeps
    ``generator_config.yaml`` reproducible.
    """
    cfg = yaml.safe_load(task_config.to_yaml()) or {}

    if result_df is not None:
        row = result_df.to_dict() if hasattr(result_df, "to_dict") else dict(result_df)
        parallel_keys = (
            "tp",
            "pp",
            "ep",
            "tp_size",
            "pp_size",
            "ep_size",
            "attention_dp",
            "moe_tp",
            "moe_ep",
            "batch_size",
            "max_batch_size",
            "workers",
            "num_workers",
            "backend",
        )
        extra = {k: v for k, v in row.items() if k in parallel_keys}
        if extra:
            cfg.setdefault("config", {}).update(extra)

    if generator_overrides:
        cfg.setdefault("generator_overrides", {}).update(generator_overrides)

    return cfg


if not _UPSTREAM:
    task_config_to_generator_config = _fallback_task_config_to_generator_config


__all__ = ["task_config_to_generator_config"]
