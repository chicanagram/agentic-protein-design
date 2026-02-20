from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import pandas as pd
import requests

from agentic_protein_design.core import apply_optional_text_inputs
from agentic_protein_design.core.chat_store import create_thread, list_threads, load_thread
from agentic_protein_design.core.pipeline_utils import (
    get_openai_client,
    persist_thread_message,
    save_text_output,
    save_text_output_with_assets_copy,
    summarize_compact_text,
    table_records,
)
from project_config.variables import address_dict, subfolders


REQUIRED_SUBFOLDERS = ["sequences", "msa", "pdb", "sce", "expdata", "processed"]
LLM_PROCESS_TAG = "literature_review"
REQUEST_TIMEOUT = 30

literature_review_agent_prompt = """
You are an AI research agent supporting an enzyme engineering project.
Your role is to conduct a structured, technically rigorous literature review and generate a concise but insight-dense summary to guide experimental design.

INPUTS (provided dynamically)
- enzyme_family: {enzyme_family}
- seed_sequences (optional): {seed_sequences}
- reactions_of_interest: {reactions_of_interest}
- substrates_of_interest (optional): {substrates_of_interest}
- application_context (optional): {application_context}
- constraints (optional): {constraints}

OBJECTIVE
Gather and synthesize current knowledge on:
1. Enzyme class structure and fold
2. Reaction mechanism (including intermediates, catalytic residues, cofactors)
3. Substrate scope and known selectivity trends
4. Cofactor requirements and catalytic cycle
5. Known engineering efforts (mutagenesis, directed evolution, ML-guided design)
6. Stability, expression, and formulation constraints
7. Gaps in knowledge and opportunities for engineering

SOURCES TO CONSULT
- Protein databases: UniProt, PDB, AlphaFold DB, InterPro, Pfam
- Literature databases: PubMed, Nature, PNAS, Science, ScienceDirect, ACS, Wiley, bioRxiv, ChemRxiv
- Reviews and meta-analyses when available
- Structural studies (crystal structures, cryo-EM)
- Mechanistic enzymology papers
- Directed evolution and protein engineering studies

INSTRUCTIONS FOR INFORMATION GATHERING
- Prioritize peer-reviewed literature and high-impact reviews.
- Distinguish between experimentally validated findings and computational predictions.
- Extract quantitative data when possible (kcat, KM, TTN, enantioselectivity, stability metrics, mutation effects).
- Identify conserved catalytic residues and structural motifs.
- Map engineering-relevant residues (active site, access channel, gating residues, stability hotspots).
- Note contradictions or unresolved mechanistic questions.

OUTPUT FORMAT

1. Executive Summary (<=10 bullet points)
   - High-level takeaways most relevant to engineering strategy.

2. Structural Overview
   - Fold classification
   - Domain architecture
   - Active site organization
   - Access channels / substrate tunnels
   - Cofactor binding
   - Known motifs or epitopes

3. Reaction Mechanism
   - Catalytic cycle steps
   - Key intermediates
   - Rate-limiting steps (if known)
   - Competing pathways (e.g. peroxygenation vs peroxidation)
   - Determinants of chemoselectivity / regioselectivity

4. Substrate Scope & Selectivity Trends
   - Classes of substrates accepted
   - Structural features tolerated
   - Trends in polarity, size, electronics
   - Known limitations

5. Engineering Landscape
   - Mutations known to affect activity/selectivity
   - Stability-enhancing mutations
   - Expression improvements
   - Channel reshaping strategies
   - ML-guided or computational design efforts
   - Reported performance gains (quantitative if available)

6. Practical Constraints
   - Cofactor stability (e.g. H2O2 sensitivity)
   - Uncoupling / inactivation pathways
   - Expression hosts used
   - Solvent/temperature/pH tolerance

7. Comparative Analysis (if multiple homologs provided)
   - Structural or mechanistic differences
   - Performance trade-offs
   - Known phenotypic clusters

8. Engineering Opportunities
   - Hypothesis-driven mutation targets
   - Channel/gating positions
   - Electrostatic tuning opportunities
   - Stability engineering strategies
   - Assay design suggestions

9. References
   - Provide full citations (authors, year, journal)
   - Include DOI or PubMed ID where available
   - Clearly distinguish review vs primary research

STYLE REQUIREMENTS
- Write clearly and technically, suitable for a PhD-level enzyme engineering audience.
- Emphasize mechanistic reasoning and structure-function relationships.
- Avoid generic textbook explanations.
- Highlight actionable insights for experimental design.
- Be concise but information-dense.

If seed_sequences are provided:
- Identify closest homologs.
- Summarize known structures and variants for those sequences.
- Highlight residue positions frequently engineered.

If reactions_of_interest are specified:
- Focus mechanistic discussion on those reaction classes.
- Distinguish between productive and competing pathways.

The goal is not just to summarize literature, but to extract engineering-relevant insight that can guide rational or ML-assisted enzyme optimization.
"""


def resolve_project_root() -> Path:
    root = Path.cwd().resolve()
    if root.name == "notebooks":
        return root.parent
    return root


def setup_data_root(root_key: str, project_root: Optional[Path] = None) -> Tuple[Path, Dict[str, Path]]:
    if root_key not in address_dict:
        raise KeyError(f"Unknown root_key: {root_key}")

    base = project_root or resolve_project_root()
    data_root = (base / address_dict[root_key]).resolve()

    resolved_dirs: Dict[str, Path] = {}
    for key in REQUIRED_SUBFOLDERS:
        if key not in subfolders:
            raise KeyError(f"Missing subfolder key in variables.subfolders: {key}")
        resolved = data_root / subfolders[key]
        resolved.mkdir(parents=True, exist_ok=True)
        resolved_dirs[key] = resolved

    return data_root, resolved_dirs


def init_thread(root_key: str, existing_thread_id: Optional[str] = None) -> Tuple[Dict[str, Any], pd.DataFrame]:
    if existing_thread_id:
        thread = load_thread(root_key, existing_thread_id, llm_process_tag=LLM_PROCESS_TAG)
    else:
        thread = create_thread(
            root_key=root_key,
            title="UPO literature review",
            metadata={"notebook": "00_literature_review"},
            llm_process_tag=LLM_PROCESS_TAG,
        )
    preview = pd.DataFrame(list_threads(root_key, llm_process_tag=LLM_PROCESS_TAG)[:5])
    return thread, preview


def default_user_inputs() -> Dict[str, Any]:
    return {
        "enzyme_family": "unspecific peroxygenases (UPOs)",
        "seed_sequences": ["CviUPO"],
        "reactions_of_interest": "peroxygenation of aromatics",
        "substrates_of_interest": ["Veratryl alcohol", "Naphthalene", "NBD", "ABTS", "S82"],
        "application_context": "biocatalysis and green chemistry",
        "constraints": ["H2O2 tolerance", "stability", "expression host compatibility"],
        "keywords": ["peroxygenation"],
        "search_sources": [
            "UniProt",
            "InterPro",
            "PDB",
            "AlphaFold DB",
            "PubMed",
            "EuropePMC",
            "OpenAlex",
            "WebSearch",
        ],
        "literature_targets": ["bioRxiv", "Nature", "ScienceDirect"],
        "evidence_focus": [
            "protein_annotations",
            "structure",
            "reaction_mechanism",
            "historical_mutations",
        ],
        "max_results_per_source": 20,
        "fetch_open_access_fulltext": True,
        "fulltext_max_chars": 6000,
        "llm_model": "gpt-5.2",
        "llm_temperature": 0.2,
        "llm_max_rows_per_table": 250,
        "enable_relaxed_fallback": True,
        "min_quality_score_for_llm_context": 0.35,
        "data_fbase_key": "examples",  # key in project_config.variables.address_dict
        "data_fbase": "",  # optional explicit fallback path (used when data_fbase_key is blank)
        "data_subfolder": "",  # optional; can be ""
        "enable_pdf_rag": True,
        "pdf_rag_max_files": 20,
        "pdf_rag_max_chars_per_file": 8000,
        "pdf_rag_max_total_chars": 50000,
    }


def _safe_join(items: List[str]) -> str:
    cleaned = [str(x).strip() for x in items if str(x).strip()]
    return " ".join(cleaned)


def _build_query(inputs: Dict[str, Any]) -> str:
    parts = [
        str(inputs.get("enzyme_family", "")),
        _safe_join(inputs.get("seed_sequences", [])),
        str(inputs.get("reactions_of_interest", "")),
        _safe_join(inputs.get("keywords", [])),
        _safe_join(inputs.get("literature_targets", [])),
    ]
    return _safe_join(parts)


def _build_relaxed_query(inputs: Dict[str, Any]) -> str:
    parts = [
        str(inputs.get("enzyme_family", "")),
        _safe_join(inputs.get("seed_sequences", [])),
        _safe_join(inputs.get("keywords", [])),
    ]
    return _safe_join(parts)


def build_literature_agent_prompt(inputs: Dict[str, Any]) -> str:
    return literature_review_agent_prompt.format(
        enzyme_family=str(inputs.get("enzyme_family", "")),
        seed_sequences=_safe_join(inputs.get("seed_sequences", [])) or "None provided",
        reactions_of_interest=str(inputs.get("reactions_of_interest", "")),
        substrates_of_interest=_safe_join(inputs.get("substrates_of_interest", [])) or "None provided",
        application_context=str(inputs.get("application_context", "")) or "None provided",
        constraints=_safe_join(inputs.get("constraints", [])) or "None provided",
    )


def resolve_data_fbase(inputs: Dict[str, Any], project_root: Optional[Path] = None) -> Path:
    base = project_root or resolve_project_root()
    key = str(inputs.get("data_fbase_key", "")).strip()
    if key:
        if key not in address_dict:
            raise KeyError(
                f"Unknown data_fbase_key: {key}. Available keys: {sorted(address_dict.keys())}"
            )
        return (base / address_dict[key]).resolve()

    explicit = str(inputs.get("data_fbase", "")).strip()
    if explicit:
        p = Path(explicit).expanduser()
        if not p.is_absolute():
            p = (base / p).resolve()
        return p

    return (base / address_dict.get("examples", "./examples/")).resolve()


def resolve_literature_docs_dir(inputs: Dict[str, Any], project_root: Optional[Path] = None) -> Path:
    data_fbase = resolve_data_fbase(inputs, project_root=project_root)
    data_subfolder_raw = inputs.get("data_subfolder", "")
    data_subfolder = "" if data_subfolder_raw is None else str(data_subfolder_raw).strip().strip("/")
    if data_subfolder:
        return (data_fbase / "literature" / data_subfolder).resolve()
    return (data_fbase / "literature").resolve()


def _extract_pdf_text(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("PDF extraction requires `pypdf` package.") from exc

    reader = PdfReader(str(pdf_path))
    parts: List[str] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text:
            parts.append(text)
    return _clean_text("\n\n".join(parts), max_chars=10_000_000)


def ingest_local_literature_docs(inputs: Dict[str, Any], project_root: Optional[Path] = None) -> Dict[str, Any]:
    docs_dir = resolve_literature_docs_dir(inputs, project_root=project_root)
    max_files = int(inputs.get("pdf_rag_max_files", 20))
    max_chars_per_file = int(inputs.get("pdf_rag_max_chars_per_file", 8000))
    max_total_chars = int(inputs.get("pdf_rag_max_total_chars", 50000))
    enable_pdf_rag = bool(inputs.get("enable_pdf_rag", True))

    if not enable_pdf_rag:
        print(f"[LocalPDF] disabled; docs_dir={docs_dir}")
        return {
            "docs_dir": str(docs_dir),
            "local_document_hits": pd.DataFrame(),
            "local_document_context": "",
            "doc_errors": [],
            "n_docs_discovered": 0,
            "n_docs_used": 0,
        }

    pdf_files = sorted(docs_dir.glob("*.pdf")) if docs_dir.exists() else []
    pdf_files = pdf_files[:max_files]
    print(
        f"[LocalPDF] docs_dir={docs_dir} discovered={len(pdf_files)} "
        f"max_files={max_files} max_chars_per_file={max_chars_per_file} max_total_chars={max_total_chars}"
    )

    rows: List[Dict[str, Any]] = []
    context_chunks: List[str] = []
    errors: List[str] = []
    used_chars = 0
    n_used = 0

    for p in pdf_files:
        try:
            text = _extract_pdf_text(p)
        except Exception as exc:
            err = f"{p.name}: {type(exc).__name__}: {exc}"
            errors.append(err)
            print(f"[LocalPDF] ERROR file={p.name} reason={type(exc).__name__}: {exc}")
            continue

        if not text.strip():
            err = f"{p.name}: empty extracted text"
            errors.append(err)
            print(f"[LocalPDF] ERROR file={p.name} reason=empty extracted text")
            continue

        extracted_chars = len(text)
        file_text = text[:max_chars_per_file]
        remaining = max_total_chars - used_chars
        if remaining <= 0:
            print(f"[LocalPDF] STOP file={p.name} reason=global character budget exhausted")
            break
        file_text = file_text[:remaining]
        if not file_text:
            print(f"[LocalPDF] STOP file={p.name} reason=no remaining chars after budgeting")
            break

        excerpt = _clean_text(file_text, max_chars=max_chars_per_file)
        used_this_file = len(excerpt)
        truncated = used_this_file < extracted_chars
        rows.append(
            {
                "source": "LocalPDF",
                "id": p.name,
                "title": p.stem,
                "journal": "",
                "year": "",
                "abstract": excerpt[:1200],
                "is_open_access": True,
                "fulltext_url": str(p),
                "url": str(p),
                "pmcid": "",
                "host_venue": "Local literature folder",
                "fulltext_excerpt": excerpt,
            }
        )
        context_chunks.append(f"[LocalPDF: {p.name}]\n{excerpt}")
        used_chars += used_this_file
        n_used += 1
        print(
            f"[LocalPDF] OK file={p.name} extracted_chars={extracted_chars} "
            f"used_chars={used_this_file} truncated={truncated} total_used_chars={used_chars}"
        )

    return {
        "docs_dir": str(docs_dir),
        "local_document_hits": pd.DataFrame(rows),
        "local_document_context": "\n\n".join(context_chunks),
        "doc_errors": errors,
        "n_docs_discovered": int(len(pdf_files)),
        "n_docs_used": int(n_used),
    }


def _request_json(url: str, *, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if method == "POST":
        resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    else:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def search_uniprot(query: str, max_results: int = 20) -> pd.DataFrame:
    fields = [
        "accession",
        "id",
        "protein_name",
        "gene_names",
        "organism_name",
        "length",
        "cc_function",
        "xref_pdb",
    ]
    url = (
        "https://rest.uniprot.org/uniprotkb/search"
        f"?query={requests.utils.quote(query)}"
        f"&fields={','.join(fields)}&format=json&size={max_results}"
    )
    data = _request_json(url)
    rows: List[Dict[str, Any]] = []
    for r in data.get("results", []):
        rows.append(
            {
                "source": "UniProt",
                "id": r.get("primaryAccession", ""),
                "title": r.get("uniProtkbId", ""),
                "organism": (r.get("organism") or {}).get("scientificName", ""),
                "summary": ((r.get("proteinDescription") or {}).get("recommendedName") or {}).get("fullName", {}).get("value", ""),
                "url": f"https://www.uniprot.org/uniprotkb/{r.get('primaryAccession', '')}",
            }
        )
    return pd.DataFrame(rows)


def search_interpro(query: str, max_results: int = 20) -> pd.DataFrame:
    url = (
        "https://www.ebi.ac.uk/interpro/api/entry/interpro/"
        f"?search={requests.utils.quote(query)}&page_size={max_results}"
    )
    data = _request_json(url)
    rows: List[Dict[str, Any]] = []
    for r in data.get("results", []):
        metadata = r.get("metadata", {})
        rows.append(
            {
                "source": "InterPro",
                "id": metadata.get("accession", ""),
                "title": metadata.get("name", ""),
                "organism": "",
                "summary": metadata.get("type", ""),
                "url": f"https://www.ebi.ac.uk/interpro/entry/interpro/{metadata.get('accession', '')}/",
            }
        )
    return pd.DataFrame(rows)


def search_pdb(query: str, max_results: int = 20) -> pd.DataFrame:
    url = "https://search.rcsb.org/rcsbsearch/v2/query"
    payload = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {"attribute": "rcsb_entry_info.struct_keywords.text", "operator": "contains_phrase", "value": query},
        },
        "request_options": {"paginate": {"start": 0, "rows": max_results}},
        "return_type": "entry",
    }
    data = _request_json(url, method="POST", payload=payload)
    rows: List[Dict[str, Any]] = []
    for r in data.get("result_set", []):
        pdb_id = r.get("identifier", "")
        rows.append(
            {
                "source": "PDB",
                "id": pdb_id,
                "title": pdb_id,
                "organism": "",
                "summary": "Protein structure entry",
                "url": f"https://www.rcsb.org/structure/{pdb_id}",
            }
        )
    return pd.DataFrame(rows)


def search_alphafold(query: str, max_results: int = 20) -> pd.DataFrame:
    url = f"https://alphafold.ebi.ac.uk/api/search?q={requests.utils.quote(query)}"
    data = _request_json(url)
    rows: List[Dict[str, Any]] = []
    for r in data[:max_results] if isinstance(data, list) else []:
        accession = r.get("entryId", "")
        rows.append(
            {
                "source": "AlphaFold DB",
                "id": accession,
                "title": r.get("uniprotDescription", ""),
                "organism": r.get("organismScientificName", ""),
                "summary": "Predicted protein structure",
                "url": f"https://alphafold.ebi.ac.uk/entry/{accession}",
            }
        )
    return pd.DataFrame(rows)


def search_pubmed(query: str, max_results: int = 20) -> pd.DataFrame:
    esearch = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&retmode=json&retmax={max_results}&term={requests.utils.quote(query)}"
    )
    ids = _request_json(esearch).get("esearchresult", {}).get("idlist", [])
    if not ids:
        return pd.DataFrame(columns=["source", "id", "title", "journal", "year", "abstract", "is_open_access", "fulltext_url", "url"])

    efetch = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        f"?db=pubmed&id={','.join(ids)}&retmode=xml"
    )
    resp = requests.get(efetch, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    rows: List[Dict[str, Any]] = []
    for article in root.findall(".//PubmedArticle"):
        pmid = "".join(article.findtext(".//PMID", default="").split())
        title = article.findtext(".//ArticleTitle", default="")
        journal = article.findtext(".//Journal/Title", default="")
        year = article.findtext(".//PubDate/Year", default="")
        abstract = " ".join([a.text or "" for a in article.findall(".//Abstract/AbstractText")]).strip()

        pmcid = ""
        for aid in article.findall(".//ArticleId"):
            if aid.attrib.get("IdType") == "pmc":
                pmcid = (aid.text or "").strip()
                break

        fulltext_url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/" if pmcid else ""
        rows.append(
            {
                "source": "PubMed",
                "id": pmid,
                "title": title,
                "journal": journal,
                "year": year,
                "abstract": abstract,
                "is_open_access": bool(pmcid),
                "fulltext_url": fulltext_url,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "pmcid": pmcid,
                "host_venue": journal,
            }
        )
    return pd.DataFrame(rows)


def search_europe_pmc(query: str, max_results: int = 20) -> pd.DataFrame:
    url = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        f"?query={requests.utils.quote(query)}&format=json&pageSize={max_results}&resultType=core"
    )
    data = _request_json(url)
    results = (data.get("resultList") or {}).get("result", [])
    rows: List[Dict[str, Any]] = []
    for r in results:
        pmcid = r.get("pmcid", "")
        fulltext_url = r.get("fullTextUrl", "")
        if not fulltext_url and pmcid:
            fulltext_url = f"https://europepmc.org/articles/{pmcid}"

        rows.append(
            {
                "source": "EuropePMC",
                "id": r.get("id", ""),
                "title": r.get("title", ""),
                "journal": r.get("journalTitle", ""),
                "year": r.get("pubYear", ""),
                "abstract": r.get("abstractText", ""),
                "is_open_access": str(r.get("isOpenAccess", "N")).upper() == "Y",
                "fulltext_url": fulltext_url,
                "url": r.get("doi", "") and f"https://doi.org/{r.get('doi')}" or "",
                "pmcid": pmcid,
                "host_venue": r.get("journalTitle", ""),
            }
        )
    return pd.DataFrame(rows)


def search_openalex(query: str, max_results: int = 20) -> pd.DataFrame:
    url = (
        "https://api.openalex.org/works"
        f"?search={requests.utils.quote(query)}&per-page={max_results}&select=id,display_name,publication_year,primary_location,open_access,host_venue"
    )
    data = _request_json(url)
    rows: List[Dict[str, Any]] = []
    for r in data.get("results", []):
        oa = r.get("open_access") or {}
        pl = r.get("primary_location") or {}
        source = (pl.get("source") or {}).get("display_name", "")

        rows.append(
            {
                "source": "OpenAlex",
                "id": r.get("id", ""),
                "title": r.get("display_name", ""),
                "journal": source,
                "year": r.get("publication_year", ""),
                "abstract": "",
                "is_open_access": bool(oa.get("is_oa", False)),
                "fulltext_url": oa.get("oa_url", "") or pl.get("landing_page_url", ""),
                "url": pl.get("landing_page_url", ""),
                "pmcid": "",
                "host_venue": source,
            }
        )
    return pd.DataFrame(rows)


def search_general_web(query: str, max_results: int = 20) -> pd.DataFrame:
    """
    General web search with Tavily (preferred) and DuckDuckGo fallback.
    Returns title/url/snippet rows.
    """
    # Preferred: Tavily if key is available.
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if tavily_key:
        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=tavily_key)
            data = client.search(query=query, max_results=max_results)
            rows: List[Dict[str, Any]] = []
            for r in data.get("results", []):
                rows.append(
                    {
                        "source": "WebSearch",
                        "id": r.get("url", ""),
                        "title": r.get("title", ""),
                        "journal": "",
                        "year": "",
                        "abstract": r.get("content", ""),
                        "is_open_access": "",
                        "fulltext_url": r.get("url", ""),
                        "url": r.get("url", ""),
                        "pmcid": "",
                        "host_venue": r.get("url", ""),
                    }
                )
            return pd.DataFrame(rows)
        except Exception:
            pass

    # Fallback: DuckDuckGo Instant Answer API (no key).
    url = (
        "https://api.duckduckgo.com/"
        f"?q={requests.utils.quote(query)}&format=json&no_html=1&skip_disambig=1"
    )
    data = _request_json(url)
    rows = []

    heading = data.get("Heading", "")
    abstract = data.get("AbstractText", "")
    abstract_url = data.get("AbstractURL", "")
    if heading or abstract:
        rows.append(
            {
                "source": "WebSearch",
                "id": abstract_url,
                "title": heading or query,
                "journal": "",
                "year": "",
                "abstract": abstract,
                "is_open_access": "",
                "fulltext_url": abstract_url,
                "url": abstract_url,
                "pmcid": "",
                "host_venue": abstract_url,
            }
        )

    for topic in data.get("RelatedTopics", [])[:max_results]:
        if isinstance(topic, dict) and "Text" in topic:
            first_url = topic.get("FirstURL", "")
            rows.append(
                {
                    "source": "WebSearch",
                    "id": first_url,
                    "title": topic.get("Text", "")[:160],
                    "journal": "",
                    "year": "",
                    "abstract": topic.get("Text", ""),
                    "is_open_access": "",
                    "fulltext_url": first_url,
                    "url": first_url,
                    "pmcid": "",
                    "host_venue": first_url,
                }
            )
    return pd.DataFrame(rows[:max_results])


def _clean_text(text: str, max_chars: int = 6000) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text[:max_chars]


def fetch_pmc_fulltext_xml(pmcid: str, max_chars: int = 6000) -> str:
    if not pmcid:
        return ""
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    if resp.status_code != 200:
        return ""
    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError:
        return ""
    text = " ".join(root.itertext())
    return _clean_text(text, max_chars=max_chars)


def enrich_open_access_fulltext(literature_df: pd.DataFrame, max_chars: int = 6000) -> pd.DataFrame:
    if literature_df.empty:
        out = literature_df.copy()
        out["fulltext_excerpt"] = ""
        return out

    out = literature_df.copy()
    excerpts: List[str] = []
    for _, row in out.iterrows():
        is_oa = bool(row.get("is_open_access", False))
        pmcid = str(row.get("pmcid", "") or "")
        excerpt = ""
        if is_oa and pmcid:
            excerpt = fetch_pmc_fulltext_xml(pmcid, max_chars=max_chars)
        excerpts.append(excerpt)

    out["fulltext_excerpt"] = excerpts
    return out


def annotate_literature_targets(literature_df: pd.DataFrame) -> pd.DataFrame:
    if literature_df.empty:
        out = literature_df.copy()
        out["is_biorxiv"] = False
        out["is_nature"] = False
        out["is_sciencedirect"] = False
        out["target_matches"] = ""
        return out

    out = literature_df.copy()
    text = (
        out.get("title", "").fillna("").astype(str)
        + " "
        + out.get("journal", "").fillna("").astype(str)
        + " "
        + out.get("host_venue", "").fillna("").astype(str)
        + " "
        + out.get("url", "").fillna("").astype(str)
        + " "
        + out.get("fulltext_url", "").fillna("").astype(str)
    ).str.lower()

    out["is_biorxiv"] = text.str.contains("biorxiv", regex=False)
    out["is_nature"] = text.str.contains("nature", regex=False)
    out["is_sciencedirect"] = text.str.contains("sciencedirect", regex=False) | text.str.contains(
        "elsevier", regex=False
    )

    def _match_labels(row: pd.Series) -> str:
        labels: List[str] = []
        if bool(row.get("is_biorxiv", False)):
            labels.append("bioRxiv")
        if bool(row.get("is_nature", False)):
            labels.append("Nature")
        if bool(row.get("is_sciencedirect", False)):
            labels.append("ScienceDirect")
        return "; ".join(labels)

    out["target_matches"] = out.apply(_match_labels, axis=1)
    return out


def build_source_report(literature_df: pd.DataFrame) -> pd.DataFrame:
    if literature_df.empty:
        return pd.DataFrame(
            [
                {"metric": "total_literature_hits", "value": 0},
                {"metric": "biorxiv_hits", "value": 0},
                {"metric": "nature_hits", "value": 0},
                {"metric": "sciencedirect_hits", "value": 0},
                {"metric": "open_access_hits", "value": 0},
                {"metric": "local_pdf_hits", "value": 0},
                {"metric": "high_quality_hits", "value": 0},
                {"metric": "medium_quality_hits", "value": 0},
                {"metric": "low_quality_hits", "value": 0},
            ]
        )

    return pd.DataFrame(
        [
            {"metric": "total_literature_hits", "value": int(len(literature_df))},
            {"metric": "biorxiv_hits", "value": int(literature_df["is_biorxiv"].sum())},
            {"metric": "nature_hits", "value": int(literature_df["is_nature"].sum())},
            {"metric": "sciencedirect_hits", "value": int(literature_df["is_sciencedirect"].sum())},
            {"metric": "open_access_hits", "value": int(literature_df.get("is_open_access", pd.Series(dtype=bool)).sum())},
            {"metric": "local_pdf_hits", "value": int((literature_df.get("source", pd.Series(dtype=str)) == "LocalPDF").sum())},
            {"metric": "high_quality_hits", "value": int((literature_df.get("quality_tier", pd.Series(dtype=str)) == "high").sum())},
            {"metric": "medium_quality_hits", "value": int((literature_df.get("quality_tier", pd.Series(dtype=str)) == "medium").sum())},
            {"metric": "low_quality_hits", "value": int((literature_df.get("quality_tier", pd.Series(dtype=str)) == "low").sum())},
        ]
    )


def annotate_quality_scores(literature_df: pd.DataFrame) -> pd.DataFrame:
    if literature_df.empty:
        out = literature_df.copy()
        out["quality_score"] = pd.Series(dtype=float)
        out["quality_tier"] = pd.Series(dtype=str)
        return out

    source_base = {
        "PubMed": 0.95,
        "EuropePMC": 0.90,
        "OpenAlex": 0.80,
        "WebSearch": 0.45,
        "LocalPDF": 0.90,
    }
    trusted_domains = [
        "nature.com",
        "sciencedirect.com",
        "elsevier.com",
        "acs.org",
        "wiley.com",
        "pnas.org",
        "science.org",
        "biorxiv.org",
        "chemrxiv.org",
        "nih.gov",
        "ncbi.nlm.nih.gov",
        "europepmc.org",
    ]

    out = literature_df.copy()

    def _score_row(row: pd.Series) -> float:
        s = float(source_base.get(str(row.get("source", "")), 0.5))

        url = str(row.get("url", "") or row.get("fulltext_url", "") or "").strip().lower()
        domain = ""
        if url:
            try:
                domain = (urlparse(url).netloc or "").lower()
            except Exception:
                domain = ""
        if any(td in domain for td in trusted_domains):
            s += 0.25

        if bool(row.get("is_open_access", False)):
            s += 0.05

        abstract = str(row.get("abstract", "") or "").strip()
        fulltext_excerpt = str(row.get("fulltext_excerpt", "") or "").strip()
        if not abstract and not fulltext_excerpt:
            s -= 0.15

        if not url:
            s -= 0.10

        return max(0.0, min(1.0, s))

    out["quality_score"] = out.apply(_score_row, axis=1)
    out["quality_tier"] = out["quality_score"].apply(
        lambda x: "high" if x >= 0.75 else ("medium" if x >= 0.5 else "low")
    )
    out = out.sort_values(by="quality_score", ascending=False).reset_index(drop=True)
    return out


def _safe_call(func, *args, **kwargs) -> pd.DataFrame:
    try:
        return func(*args, **kwargs)
    except Exception:
        return pd.DataFrame()


def _call_with_debug(func, query: str, max_results: int) -> Tuple[pd.DataFrame, str]:
    try:
        df = func(query, max_results)
        return df, ""
    except Exception as exc:
        return pd.DataFrame(), f"{type(exc).__name__}: {exc}"


def run_literature_pipeline(inputs: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    query = _build_query(inputs)
    sources = set(inputs.get("search_sources", []))
    max_results = int(inputs.get("max_results_per_source", 20))
    enable_relaxed = bool(inputs.get("enable_relaxed_fallback", True))

    source_debug_rows: List[Dict[str, Any]] = []
    local_docs_bundle = ingest_local_literature_docs(inputs)
    local_document_hits = local_docs_bundle.get("local_document_hits", pd.DataFrame())
    source_debug_rows.append(
        {
            "source": "LocalPDF",
            "query_mode": "local_folder",
            "query": str(local_docs_bundle.get("docs_dir", "")),
            "rows": int(len(local_document_hits)),
            "error": "; ".join(local_docs_bundle.get("doc_errors", [])),
        }
    )

    protein_tables: List[pd.DataFrame] = []
    if "UniProt" in sources:
        df, err = _call_with_debug(search_uniprot, query, max_results)
        protein_tables.append(df)
        source_debug_rows.append({"source": "UniProt", "query_mode": "primary", "query": query, "rows": int(len(df)), "error": err})
    if "InterPro" in sources:
        df, err = _call_with_debug(search_interpro, query, max_results)
        protein_tables.append(df)
        source_debug_rows.append({"source": "InterPro", "query_mode": "primary", "query": query, "rows": int(len(df)), "error": err})
    if "PDB" in sources:
        df, err = _call_with_debug(search_pdb, query, max_results)
        protein_tables.append(df)
        source_debug_rows.append({"source": "PDB", "query_mode": "primary", "query": query, "rows": int(len(df)), "error": err})
    if "AlphaFold DB" in sources:
        df, err = _call_with_debug(search_alphafold, query, max_results)
        protein_tables.append(df)
        source_debug_rows.append({"source": "AlphaFold DB", "query_mode": "primary", "query": query, "rows": int(len(df)), "error": err})

    protein_nonempty = [t for t in protein_tables if not t.empty]
    protein_hits = pd.concat(protein_nonempty, ignore_index=True) if protein_nonempty else pd.DataFrame()

    lit_tables: List[pd.DataFrame] = []
    if "PubMed" in sources:
        df, err = _call_with_debug(search_pubmed, query, max_results)
        lit_tables.append(df)
        source_debug_rows.append({"source": "PubMed", "query_mode": "primary", "query": query, "rows": int(len(df)), "error": err})
    if "EuropePMC" in sources:
        df, err = _call_with_debug(search_europe_pmc, query, max_results)
        lit_tables.append(df)
        source_debug_rows.append({"source": "EuropePMC", "query_mode": "primary", "query": query, "rows": int(len(df)), "error": err})
    if "OpenAlex" in sources:
        df, err = _call_with_debug(search_openalex, query, max_results)
        lit_tables.append(df)
        source_debug_rows.append({"source": "OpenAlex", "query_mode": "primary", "query": query, "rows": int(len(df)), "error": err})
    if "WebSearch" in sources:
        df, err = _call_with_debug(search_general_web, query, max_results)
        lit_tables.append(df)
        source_debug_rows.append({"source": "WebSearch", "query_mode": "primary", "query": query, "rows": int(len(df)), "error": err})

    lit_nonempty = [t for t in lit_tables if not t.empty]
    literature_hits = pd.concat(lit_nonempty, ignore_index=True) if lit_nonempty else pd.DataFrame()

    if enable_relaxed and protein_hits.empty and literature_hits.empty:
        relaxed_query = _build_relaxed_query(inputs)
        if relaxed_query and relaxed_query != query:
            if "UniProt" in sources:
                df, err = _call_with_debug(search_uniprot, relaxed_query, max_results)
                protein_tables.append(df)
                source_debug_rows.append({"source": "UniProt", "query_mode": "relaxed", "query": relaxed_query, "rows": int(len(df)), "error": err})
            if "InterPro" in sources:
                df, err = _call_with_debug(search_interpro, relaxed_query, max_results)
                protein_tables.append(df)
                source_debug_rows.append({"source": "InterPro", "query_mode": "relaxed", "query": relaxed_query, "rows": int(len(df)), "error": err})
            if "PDB" in sources:
                df, err = _call_with_debug(search_pdb, relaxed_query, max_results)
                protein_tables.append(df)
                source_debug_rows.append({"source": "PDB", "query_mode": "relaxed", "query": relaxed_query, "rows": int(len(df)), "error": err})
            if "AlphaFold DB" in sources:
                df, err = _call_with_debug(search_alphafold, relaxed_query, max_results)
                protein_tables.append(df)
                source_debug_rows.append({"source": "AlphaFold DB", "query_mode": "relaxed", "query": relaxed_query, "rows": int(len(df)), "error": err})
            if "PubMed" in sources:
                df, err = _call_with_debug(search_pubmed, relaxed_query, max_results)
                lit_tables.append(df)
                source_debug_rows.append({"source": "PubMed", "query_mode": "relaxed", "query": relaxed_query, "rows": int(len(df)), "error": err})
            if "EuropePMC" in sources:
                df, err = _call_with_debug(search_europe_pmc, relaxed_query, max_results)
                lit_tables.append(df)
                source_debug_rows.append({"source": "EuropePMC", "query_mode": "relaxed", "query": relaxed_query, "rows": int(len(df)), "error": err})
            if "OpenAlex" in sources:
                df, err = _call_with_debug(search_openalex, relaxed_query, max_results)
                lit_tables.append(df)
                source_debug_rows.append({"source": "OpenAlex", "query_mode": "relaxed", "query": relaxed_query, "rows": int(len(df)), "error": err})
            if "WebSearch" in sources:
                df, err = _call_with_debug(search_general_web, relaxed_query, max_results)
                lit_tables.append(df)
                source_debug_rows.append({"source": "WebSearch", "query_mode": "relaxed", "query": relaxed_query, "rows": int(len(df)), "error": err})

            protein_nonempty = [t for t in protein_tables if not t.empty]
            protein_hits = pd.concat(protein_nonempty, ignore_index=True) if protein_nonempty else pd.DataFrame()
            lit_nonempty = [t for t in lit_tables if not t.empty]
            literature_hits = pd.concat(lit_nonempty, ignore_index=True) if lit_nonempty else pd.DataFrame()

    if bool(inputs.get("fetch_open_access_fulltext", True)):
        literature_hits = enrich_open_access_fulltext(
            literature_hits,
            max_chars=int(inputs.get("fulltext_max_chars", 6000)),
        )
    if not local_document_hits.empty:
        # Keep local PDFs in the same literature dataframe used for downstream scoring/LLM context.
        literature_hits = pd.concat([literature_hits, local_document_hits], ignore_index=True, sort=False)
    literature_hits = annotate_literature_targets(literature_hits)
    literature_hits = annotate_quality_scores(literature_hits)
    source_report = build_source_report(literature_hits)

    summary_rows: List[Dict[str, Any]] = []
    for _, r in literature_hits.head(max_results).iterrows():
        summary_rows.append(
            {
                "enzyme_class": inputs.get("enzyme_family", ""),
                "enzyme": _safe_join(inputs.get("seed_sequences", [])),
                "source": r.get("source", ""),
                "topic": "web_evidence" if r.get("source", "") == "WebSearch" else "literature_evidence",
                "finding": r.get("title", ""),
                "evidence": r.get("abstract", "") or r.get("fulltext_excerpt", ""),
                "confidence": float(r.get("quality_score", 0.6)),
                "quality_tier": r.get("quality_tier", ""),
                "url": r.get("url", "") or r.get("fulltext_url", ""),
            }
        )

    for _, r in protein_hits.head(max_results).iterrows():
        summary_rows.append(
            {
                "enzyme_class": inputs.get("enzyme_family", ""),
                "enzyme": _safe_join(inputs.get("seed_sequences", [])),
                "source": r.get("source", ""),
                "topic": "protein_database_evidence",
                "finding": r.get("title", ""),
                "evidence": r.get("summary", ""),
                "confidence": 0.7,
                "quality_tier": "high",
                "url": r.get("url", ""),
            }
        )

    literature_summary = pd.DataFrame(summary_rows)
    source_debug = pd.DataFrame(source_debug_rows)
    return {
        "protein_hits": protein_hits,
        "literature_hits": literature_hits,
        "local_document_hits": local_document_hits,
        "local_document_context": pd.DataFrame(
            [{"context_text": str(local_docs_bundle.get("local_document_context", ""))}]
        ),
        "literature_summary": literature_summary,
        "source_report": source_report,
        "source_debug": source_debug,
    }


def generate_literature_llm_review(outputs: Dict[str, pd.DataFrame], inputs: Dict[str, Any]) -> str:
    model = str(inputs.get("llm_model", "gpt-5.2"))
    temperature = float(inputs.get("llm_temperature", 0.2))
    max_rows = int(inputs.get("llm_max_rows_per_table", 250))

    prompt_text = build_literature_agent_prompt(inputs)
    min_quality = float(inputs.get("min_quality_score_for_llm_context", 0.35))
    lit_for_llm = outputs.get("literature_hits", pd.DataFrame())
    if not lit_for_llm.empty and "quality_score" in lit_for_llm.columns:
        lit_for_llm = lit_for_llm[lit_for_llm["quality_score"] >= min_quality].copy()

    local_ctx_df = outputs.get("local_document_context", pd.DataFrame())
    local_context_text = ""
    if not local_ctx_df.empty and "context_text" in local_ctx_df.columns:
        local_context_text = str(local_ctx_df.iloc[0].get("context_text", "") or "")

    payload = {
        "protein_database_hits": table_records(outputs.get("protein_hits", pd.DataFrame()), max_rows),
        "literature_hits": table_records(lit_for_llm, max_rows),
        "local_document_hits": table_records(outputs.get("local_document_hits", pd.DataFrame()), max_rows),
        "local_document_context": local_context_text,
        "literature_summary": table_records(outputs.get("literature_summary", pd.DataFrame()), max_rows),
        "source_report": table_records(outputs.get("source_report", pd.DataFrame()), max_rows),
    }

    client = get_openai_client(
        missing_package_message="The `openai` package is required for LLM review generation.",
        missing_key_message="OPENAI_API_KEY is not set. Export it or set it via local_api_keys.py before LLM review.",
    )
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are an expert computational enzymologist and literature synthesis agent."},
            {"role": "user", "content": f"{prompt_text}\n\nINPUT_DATA_JSON:\n{json.dumps(payload, ensure_ascii=True)}"},
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("LLM returned an empty literature review.")
    return text


def save_literature_llm_review(review_text: str, processed_dir: Path) -> Path:
    return save_text_output_with_assets_copy(
        review_text,
        processed_dir,
        "literature_review_llm_summary.md",
        assets_filename="literature_review_llm_summary.md",
    )


def summarize_text(text: str, max_chars: int = 1000) -> str:
    return summarize_compact_text(text, max_chars=max_chars)


def save_literature_outputs(outputs: Dict[str, pd.DataFrame], processed_dir: Path) -> Dict[str, Path]:
    out_paths = {
        "literature_summary": processed_dir / "literature_summary.csv",
        "literature_hits": processed_dir / "literature_hits.csv",
        "protein_database_hits": processed_dir / "protein_database_hits.csv",
        "literature_source_report": processed_dir / "literature_source_report.csv",
        "literature_source_debug.csv": processed_dir / "literature_source_debug.csv",
        "web_search_hits.csv": processed_dir / "web_search_hits.csv",
    }

    outputs.get("literature_summary", pd.DataFrame()).to_csv(out_paths["literature_summary"], index=False)
    outputs.get("literature_hits", pd.DataFrame()).to_csv(out_paths["literature_hits"], index=False)
    outputs.get("protein_hits", pd.DataFrame()).to_csv(out_paths["protein_database_hits"], index=False)
    outputs.get("source_report", pd.DataFrame()).to_csv(out_paths["literature_source_report"], index=False)
    outputs.get("source_debug", pd.DataFrame()).to_csv(out_paths["literature_source_debug.csv"], index=False)
    web_hits = outputs.get("literature_hits", pd.DataFrame())
    if not web_hits.empty and "source" in web_hits.columns:
        web_hits = web_hits[web_hits["source"] == "WebSearch"].copy()

    # Optional local document retrieval hits (for example PDF RAG) are merged into
    # the same output file to avoid proliferating separate artifacts.
    local_doc_hits = outputs.get("local_document_hits", pd.DataFrame()).copy()
    if not local_doc_hits.empty:
        if "source" not in local_doc_hits.columns:
            local_doc_hits["source"] = "LocalDocument"
        if "source" in local_doc_hits.columns:
            local_doc_hits["source"] = local_doc_hits["source"].replace("", "LocalDocument")

    combined_external_hits = (
        pd.concat([web_hits, local_doc_hits], ignore_index=True, sort=False)
        if (not web_hits.empty or not local_doc_hits.empty)
        else pd.DataFrame()
    )
    if not combined_external_hits.empty:
        dedupe_cols = [c for c in ["source", "id", "title", "url", "fulltext_url"] if c in combined_external_hits.columns]
        if dedupe_cols:
            combined_external_hits = combined_external_hits.drop_duplicates(subset=dedupe_cols).reset_index(drop=True)

    combined_external_hits.to_csv(out_paths["web_search_hits.csv"], index=False)
    return out_paths


def persist_thread_update(
    root_key: str,
    thread_id: str,
    inputs: Dict[str, Any],
    out_paths: Dict[str, Path],
    llm_review_path: Optional[Path] = None,
    llm_review_text: Optional[str] = None,
) -> str:
    return persist_thread_message(
        root_key=root_key,
        thread_id=thread_id,
        llm_process_tag=LLM_PROCESS_TAG,
        source_notebook="00_literature_review",
        content=build_literature_agent_prompt(inputs),
        metadata={
            "inputs": inputs,
            "outputs": {k: str(v) for k, v in out_paths.items()},
            "llm_review_path": "" if llm_review_path is None else str(llm_review_path),
            "llm_review_summary": "" if not llm_review_text else summarize_text(llm_review_text),
            "llm_model": str(inputs.get("llm_model", "")),
        },
    )


def run_literature_review_step(
    root_key: str,
    inputs: Dict[str, Any],
    *,
    input_paths: Optional[Dict[str, str]] = None,
    existing_thread_id: Optional[str] = None,
    run_llm: bool = True,
    persist: bool = True,
) -> Dict[str, Any]:
    """
    Run the full literature-review step and return outputs for downstream composition.
    """
    data_root, resolved_dirs = setup_data_root(root_key)
    thread, _ = init_thread(root_key, existing_thread_id)
    thread_id = str(thread["thread_id"])

    step_inputs = dict(inputs)
    apply_optional_text_inputs(step_inputs, input_paths or {}, data_root)

    outputs = run_literature_pipeline(step_inputs)
    out_paths = save_literature_outputs(outputs, resolved_dirs["processed"])

    llm_review_text: Optional[str] = None
    llm_review_path: Optional[Path] = None
    if run_llm:
        llm_review_text = generate_literature_llm_review(outputs, step_inputs)
        llm_review_path = save_literature_llm_review(llm_review_text, resolved_dirs["processed"])

    updated_at: Optional[str] = None
    if persist:
        updated_at = persist_thread_update(
            root_key=root_key,
            thread_id=thread_id,
            inputs=step_inputs,
            out_paths=out_paths,
            llm_review_path=llm_review_path,
            llm_review_text=llm_review_text,
        )

    return {
        "root_key": root_key,
        "thread_id": thread_id,
        "thread_updated_at": updated_at,
        "data_root": data_root,
        "resolved_dirs": resolved_dirs,
        "inputs": step_inputs,
        "outputs": outputs,
        "out_paths": out_paths,
        "llm_review_text": llm_review_text,
        "llm_review_path": llm_review_path,
    }
