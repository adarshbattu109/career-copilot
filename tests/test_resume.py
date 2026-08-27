"""ATS/quality checks for career-copilot résumé output.

Encodes the checks we otherwise do by hand:
  - templates are ATS-safe (single <main>, no layout <table>, real text, standard headings)
  - any rendered résumé PDF extracts headings in correct reading order (the ATS proof)
  - the data files under ~/.career-copilot validate against a minimal schema

Run: source .venv/bin/activate && pytest -q     (or: uv run pytest -q)
"""
import json, os, glob, pathlib
import pytest
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "skills" / "tailor-resume" / "assets"
STORE = pathlib.Path(os.path.expanduser("~/.career-copilot"))
STD_HEADINGS = {"summary", "experience", "experiences", "education", "skills",
                "technical skills", "projects", "certifications", "certifications & awards",
                "awards & recognition"}

TEMPLATES = sorted(glob.glob(str(ASSETS / "resume-template*.html")))
PDFS = sorted(glob.glob(str(STORE / "resumes" / "*.pdf")))


@pytest.mark.parametrize("tpl", TEMPLATES, ids=[pathlib.Path(t).name for t in TEMPLATES])
def test_template_is_ats_safe(tpl):
    soup = BeautifulSoup(pathlib.Path(tpl).read_text(encoding="utf-8"), "html.parser")
    # single reading column
    assert len(soup.find_all("main")) == 1, "exactly one <main> (single reading column)"
    # no layout tables (the #1 ATS failure)
    assert not soup.find_all("table"), "no <table> — breaks ATS parsing"
    # headings are standard section names (h2)
    h2s = [h.get_text(strip=True).lower() for h in soup.find_all("h2")]
    assert h2s, "has section headings"
    assert any(h in STD_HEADINGS for h in h2s), f"standard headings; got {h2s}"
    # real text present (not an image-only résumé)
    assert len(soup.get_text(strip=True)) > 400, "substantive real text"


@pytest.mark.skipif(not PDFS, reason="no rendered PDFs in ~/.career-copilot/resumes yet")
@pytest.mark.parametrize("pdf", PDFS, ids=[pathlib.Path(p).name for p in PDFS])
def test_pdf_reading_order(pdf):
    from pypdf import PdfReader
    text = "\n".join((pg.extract_text() or "") for pg in PdfReader(pdf).pages).upper()
    seen = [h for h in ["SUMMARY", "EXPERIENCE", "EDUCATION"] if h in text]
    assert len(seen) >= 2, f"headings extractable; found {seen}"
    # reading order: SUMMARY before EXPERIENCE before EDUCATION (whichever are present)
    positions = [text.find(h) for h in seen]
    assert positions == sorted(positions), f"headings out of reading order in {pathlib.Path(pdf).name}"


@pytest.mark.skipif(not (STORE / "profile.json").exists(), reason="no profile.json captured yet")
def test_profile_schema():
    from jsonschema import validate
    profile = json.loads((STORE / "profile.json").read_text())
    schema = {
        "type": "object",
        "required": ["name", "contact", "current", "experience", "skills"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "contact": {"type": "object", "required": ["email"]},
            "current": {"type": "object", "required": ["title", "company"]},
            "experience": {"type": "array", "minItems": 1},
            "skills": {"type": "object"},
        },
    }
    validate(instance=profile, schema=schema)
    # every experience entry has provenance (drift-reconciliation invariant)
    for e in profile["experience"]:
        assert e.get("sources"), f"experience '{e.get('company')}' missing sources[]"
