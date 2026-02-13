from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import quote_plus

from tools.api.http import http_get_json


def search_uniprot(query: str, *, size: int = 25, fields: Optional[str] = None) -> Dict[str, Any]:
    selected_fields = fields or "accession,id,protein_name,organism_name,length"
    url = (
        "https://rest.uniprot.org/uniprotkb/search"
        f"?query={quote_plus(query)}&format=json&size={int(size)}&fields={quote_plus(selected_fields)}"
    )
    return http_get_json(url)

