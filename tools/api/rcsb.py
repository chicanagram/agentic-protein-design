from __future__ import annotations

from typing import Any, Dict
from urllib.parse import quote_plus

from tools.api.http import http_get_json


def search_rcsb_text(query: str, *, rows: int = 25) -> Dict[str, Any]:
    """
    Simple text search against RCSB Search API.
    """
    # Using RCSB text endpoint via query JSON in URL for quick prototyping.
    query_json = (
        '{"query":{"type":"terminal","service":"text","parameters":{"value":"'
        + query.replace('"', '\\"')
        + '"}},"return_type":"entry","request_options":{"pager":{"start":0,"rows":'
        + str(int(rows))
        + "}}}"
    )
    url = f"https://search.rcsb.org/rcsbsearch/v2/query?json={quote_plus(query_json)}"
    return http_get_json(url)

