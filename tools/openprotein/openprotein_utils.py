#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

def connect_openprotein_session() -> Any:
    from project_config.local_api_keys import openprotein_credentials
    try:
        import openprotein
    except ImportError as exc:
        raise RuntimeError("Missing dependency `openprotein`. Install it in your environment.") from exc
    username = openprotein_credentials['username']
    password = openprotein_credentials['password']
    return openprotein.connect(username, password)