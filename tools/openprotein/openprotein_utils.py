#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

def connect_openprotein_session() -> Any:
    """
    Create and return an authenticated OpenProtein session.

    Input format:
        Credentials are loaded from `project_config.local_api_keys.openprotein_credentials`.

    Returns:
        Connected OpenProtein client/session object.
    """
    from project_config.local_api_keys import openprotein_credentials
    try:
        import openprotein
    except ImportError as exc:
        raise RuntimeError("Missing dependency `openprotein`. Install it in your environment.") from exc
    username = openprotein_credentials['username']
    password = openprotein_credentials['password']
    return openprotein.connect(username, password)
