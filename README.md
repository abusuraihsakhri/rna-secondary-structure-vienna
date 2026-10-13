# RNA Secondary Structure Vienna

An RNA secondary-structure project with two **distinct** prediction methods: a standalone browser explorer using the Nussinov maximum-base-pair algorithm, and real thermodynamic minimum-free-energy (MFE) folding using the optional [ViennaRNA Python bindings](https://viennarna.readthedocs.io/en/latest/api_python.html).

The repository also retains a legacy numeric-threshold audit CLI/API for compatibility. Those audits are **not** RNA structure or free-energy calculations.

## Browser explorer

The static application is in [`web/`](web/). It runs locally in modern browsers and can be deployed to GitHub Pages. Enter a plain RNA sequence or a single FASTA record and select **Predict structure**.

Features:
- Canonical AU/GC and GU wobble base pairing; at least three unpaired hairpin nucleotides.
- Pseudoknot-free Nussinov dynamic programming (maximum paired bases, not MFE).
- Dot-bracket sequence, pairing arcs, length, paired-base count and GC percentage.
- Copy and text export; clear invalid-input messages; a 240-nt browser limit.
- No backend, analytics or sequence upload.

**Scientific limitation:** The browser algorithm does not model nearest-neighbor/Turner thermodynamics, loop free energies, temperature-dependent folding or partition functions. Its result may differ substantially from ViennaRNA and should not be interpreted as an MFE prediction. It is educational and exploratory, not clinically validated.

## ViennaRNA MFE prediction (Python)

Requires Python 3.10–3.12 (CI-tested targets) and the separately installed ViennaRNA bindings:

```bash
git clone https://github.com/abusuraihsakhri/rna-secondary-structure-vienna.git
cd rna-secondary-structure-vienna
python -m pip install -e ".[api,vienna]"
python cli.py fold --sequence GGGAAACCC
python -m rna_shape_predictor.cli fold --sequence GGGAAACCC --json
```

The `fold` commands normalize single-entry FASTA input and `T` → `U`, reject unsupported ambiguity codes, and enforce a 500-nucleotide limit. They return ViennaRNA's dot-bracket MFE prediction and its energy in kcal/mol (default ViennaRNA model). If ViennaRNA is absent, they report a dependency error; **they never substitute the browser approximation**.

Run the local API:

```bash
python cli.py serve --host 127.0.0.1 --port 8000
curl -s -X POST http://127.0.0.1:8000/api/fold \
  -H 'Content-Type: application/json' \
  -d '{"sequence":"GGGAAACCC"}'
```

The API returns `422` for invalid sequences and `503` when the native ViennaRNA dependency is unavailable. FastAPI serves interactive API documentation at `/docs`.

## Legacy audit workflows

Existing numeric threshold and audit features remain usable; they operate on `task_id`, `target_identifier`, `primary_metric`, `secondary_metric`, `status_descriptor` and `is_critical_flag`.

```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2
python cli.py batch --input sample.csv --output results.csv
python cli.py verify-audit
python cli.py chat "What is the system status?"
```

The API also retains `/health`, `/metrics`, `/api/audit`, `/api/chat`, and `/api/audit/logs`. A second legacy server entry point exists at `rna_shape_predictor.server:create_app`. Legacy enrichment modules are threshold demonstrations rather than validated RNA-structure algorithms. Mock chat providers perform no language-model inference.

## Security and privacy

The browser explorer performs computation entirely in the browser and does not transmit sequences. The Python API is self-hosted; it processes supplied sequences locally. The legacy audit service retains in-memory task metadata and an in-memory chained HMAC audit log; these disappear on restart. An HMAC protects log integrity **only while its secret remains private**; it does not encrypt the log or provide durable storage. Basic identifier-pattern checks are **not** comprehensive PHI de-identification. Do not submit patient data to an unprotected server.

For Docker Compose, generate a unique audit key and provide `AUDIT_SECRET_KEY` as an environment variable. The sample configuration intentionally contains no real secret.

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Export the generated value privately as AUDIT_SECRET_KEY.
docker compose up --build
```

The default Docker service binds port 8000 to the host. Restrict its network exposure and add authentication and TLS before placing any endpoints on a public network; the bundled API is not an authenticated multi-user service.

## Development and tests

```bash
python -m pip install -e ".[api,vienna,test]"
python -m pytest -q
node --test tests/test_web.cjs
python -m compileall -q agents rna_shape_predictor
```

CI tests Python 3.10–3.12, the ViennaRNA adapter, browser folding, validation, and audit integrity. Modern Chromium, Firefox and Safari support the browser application; it uses standard JavaScript/DOM/SVG APIs and has no browser-Python runtime. The Pages workflow deploys only `web/` on pushes to `master`.

## License

[MIT](LICENSE). The upstream ViennaRNA library has its own licensing terms; consult the [official project](https://github.com/ViennaRNA/ViennaRNA) for details.
