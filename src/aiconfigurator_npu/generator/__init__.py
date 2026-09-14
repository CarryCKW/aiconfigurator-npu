# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Config generator bridge for aiconfigurator-npu.

Prefers the upstream ``aiconfigurator.generator`` package when installed
(``pip install aiconfigurator --extra-index-url https://pypi.nvidia.com/``);
otherwise falls back to local minimal implementations so that the core
search flow (``aic-npu cli default/exp/estimate/support``) works standalone.
"""

from aiconfigurator_npu.generator import api, module_bridge  # noqa: F401
