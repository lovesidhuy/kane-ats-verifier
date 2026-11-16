# Kane NDJSON fixtures (byte-copied from sealed evidence packs)

These files are **not hand-written**. Each file is an exact byte copy of a console NDJSON log inside a finalized `.evidence` pack. Provenance is also recorded in `tests/fixtures/kane_loop/provenance.json` (SHA-256).

| Fixture | Source evidence pack (repo path) | Test id inside pack | Inner path in pack | SHA-256 |
|---------|----------------------------------|---------------------|--------------------|---------|
| `red.ndjson` | `evidence/testrun_13_30_initial.evidence` | `17-persona-visa-ashby-strict-12ccb310` | `tests/17-persona-visa-ashby-strict-12ccb310/logs/1-console.ndjson` | `02729ab56d79d15206c64a2726269413a395ab4c5c7230553f53f3fa44013529` |
| `broken.ndjson` | *(same as `red.ndjson`)* | same | same | same |
| `green.ndjson` | `evidence/17_persona_visa_ashby_strict_passed.evidence` | `17-persona-visa-ashby-strict-12ccb310` | `tests/17-persona-visa-ashby-strict-12ccb310/logs/0-console.ndjson` | `4a85c1490c4b635335e62bb7b349751160d17200a4028a723e8491471fbc79b1` |

Suite under test: `tests/kane/17_persona_visa_ashby_strict_test.md`.

Verify locally:

```bash
python3 -c "import hashlib, pathlib; p=pathlib.Path('tests/fixtures/ndjson/red.ndjson'); print(hashlib.sha256(p.read_bytes()).hexdigest())"
pytest tests/test_kane_loop.py::test_ndjson_fixtures_match_evidence_bytes -q
```