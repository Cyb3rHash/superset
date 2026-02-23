# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Template DB engine spec.

This module provides a minimal example EngineSpec implementation to serve as a
starting point for adding a new database connector to Superset.

Notes for implementers:
- The spec is auto-discovered by `superset.db_engine_specs.load_engine_specs()`,
  which imports all python modules in this package and picks up subclasses of
  `BaseEngineSpec`.
- To make this connector functional, you must:
  1) Provide a SQLAlchemy dialect/driver that registers `engine` as a backend, and
  2) Update time grain expressions, column type mappings, and feature flags as needed.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import types

from superset.db_engine_specs.base import BaseEngineSpec


class TemplateEngineSpec(BaseEngineSpec):
    """
    Minimal EngineSpec stub for new connectors.

    This class intentionally implements the smallest surface area required for a
    valid EngineSpec module while demonstrating common override points.

    Replace `engine`/`engine_name`/`drivers` with your own values.
    """

    # SQLAlchemy backend name, ie, the part before "://", or before "+driver://".
    # Example: "postgresql", "trino", "bigquery".
    engine = "template"

    # Human readable engine name (used in user-facing places and error extras).
    engine_name = "TemplateDB"

    # Optional: enumerate known/official drivers. If omitted, backend-only matching
    # will still work (see `supports_backend` in BaseEngineSpec), but explicitly
    # listing drivers helps UI and documentation.
    drivers = {
        "driver": "TemplateDB DBAPI driver (placeholder)",
    }
    default_driver = "driver"

    # Placeholder shown in the UI when creating a database connection.
    sqlalchemy_uri_placeholder = (
        "template+driver://user:password@host:port/dbname[?key=value&key=value...]"
    )

    # Keep this minimal; real engines should define supported grains.
    _time_grain_expressions = {
        None: "{col}",
        # Examples for real implementations:
        # "PT1M": "DATE_TRUNC('minute', {col})",
        # "P1D": "DATE_TRUNC('day', {col})",
    }

    @classmethod
    def epoch_to_dttm(cls) -> str:
        """
        Convert an epoch-in-seconds expression to a datetime expression.

        The returned SQL must include the "{col}" placeholder which is replaced by
        Superset with the epoch column/expression.

        This stub is intentionally not implemented because the correct expression is
        database-specific.

        :raises NotImplementedError: Always (until a real implementation is provided).
        """
        raise NotImplementedError(
            "TemplateEngineSpec.epoch_to_dttm must be implemented for a real connector"
        )

    @classmethod
    def convert_dttm(  # pylint: disable=unused-argument
        cls,
        target_type: str,
        dttm: datetime,
        db_extra: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Convert a Python datetime object to a database SQL expression.

        This minimal implementation supports common DATE/TIMESTAMP coercions using
        ISO formatted literals. Real connectors may need timezone handling, precision,
        or database-specific functions.
        """
        sqla_type = cls.get_sqla_column_type(target_type)
        if isinstance(sqla_type, types.Date):
            return f"DATE '{dttm.date().isoformat()}'"
        if isinstance(sqla_type, (types.DateTime, types.TIMESTAMP)):
            # Use seconds precision for broad compatibility.
            return f"TIMESTAMP '{dttm.isoformat(sep=' ', timespec='seconds')}'"
        return None
