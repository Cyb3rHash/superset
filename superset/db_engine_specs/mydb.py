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
Engine spec for mydb via the mydriver SQLAlchemy dialect.

This module follows Superset's `db_engine_specs` conventions:
- It defines a subclass of `BaseEngineSpec`.
- It is auto-discovered by `superset.db_engine_specs.load_engine_specs()` which
  imports all python modules in this package and picks up `BaseEngineSpec`
  subclasses.

To make this connector functional at runtime, the environment must have:
- a SQLAlchemy dialect registered for the "mydb" backend, and
- a DBAPI driver usable by that dialect (here referenced as "mydriver").

The connection string format expected by this spec:

    mydb+mydriver://user:password@host:port/dbname[?key=value&key=value...]

"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import types

from superset.db_engine_specs.base import BaseEngineSpec


class MyDBEngineSpec(BaseEngineSpec):
    """
    Engine spec for mydb using the mydriver SQLAlchemy driver.

    This is intentionally minimal (similar to `template.py`) and provides only:
    - engine/engine_name/driver metadata for discovery + UI connection help
    - a conservative datetime literal conversion implementation

    If the mydb dialect requires special handling (time grains, schema listing,
    error message parsing, etc.), extend this class accordingly.
    """

    engine = "mydb"
    engine_name = "MyDB"

    # List known/official drivers for this backend.
    drivers = {
        "mydriver": "MyDB SQLAlchemy driver (mydriver)",
    }
    default_driver = "mydriver"

    sqlalchemy_uri_placeholder = (
        "mydb+mydriver://user:password@host:port/dbname[?key=value&key=value...]"
    )

    # Minimal: if time grain support is required, add expressions here.
    _time_grain_expressions = {
        None: "{col}",
    }

    @classmethod
    def epoch_to_dttm(cls) -> str:
        """
        Convert an epoch-in-seconds expression to a datetime expression.

        The returned SQL must include the "{col}" placeholder which is replaced by
        Superset with the epoch column/expression.

        :raises NotImplementedError: because epoch conversion is database-specific.
        """
        raise NotImplementedError(
            "MyDBEngineSpec.epoch_to_dttm must be implemented for mydb if epoch "
            "conversion is required"
        )

    @classmethod
    def convert_dttm(  # pylint: disable=unused-argument
        cls,
        target_type: str,
        dttm: datetime,
        db_extra: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Convert a Python datetime object to a mydb SQL expression.

        This minimal implementation uses ISO-formatted literals for DATE and
        TIMESTAMP-like types. If mydb requires timezone conversion or a specific
        function for timestamp literals, override this accordingly.
        """
        sqla_type = cls.get_sqla_column_type(target_type)
        if isinstance(sqla_type, types.Date):
            return f"DATE '{dttm.date().isoformat()}'"
        if isinstance(sqla_type, (types.DateTime, types.TIMESTAMP)):
            return f"TIMESTAMP '{dttm.isoformat(sep=' ', timespec='seconds')}'"
        return None
