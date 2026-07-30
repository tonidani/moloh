# Moloh

<img src="moloh.png" alt="Moloh Logo" width="300"/>
# MolohLLM

**A semantic-cache-augmented HTTP honeypot with locally-hosted LLM response generation.**

MolohLLM is an open-source HTTP honeypot that uses a locally-hosted
open-weight large language model to generate contextually coherent
responses for *arbitrary* request paths — no predefined templates. A
three-tier semantic cache (exact → canonical → 768-dimensional vector
similarity) bounds model invocations to the number of *conceptually
distinct* endpoints an attacker probes, rather than the unbounded space of
textual path variants that scanners enumerate. All inference runs on-device
via [Ollama](https://ollama.com), so attacker traffic never leaves the
deployment.

This repository contains the system, the anonymised 30-day deployment
dataset, and a self-contained script that reproduces every quantitative
result in the accompanying paper.

---

## Reproducing the paper's results

All evaluation numbers (RQ2 caching efficiency and RQ3 response-dependence)
are recomputed directly from the released SQLite deployment database by a
single script, with **no dependencies beyond the Python standard library**
(SciPy is used automatically if present; otherwise an equivalent stdlib
fallback is used).

```bash
python3 analyze.py path/to/deployment.db
```

Options:

- `--keep-private` — include RFC 1918 / loopback source IPs (health checks
  and local testing). By default these 92 non-routable interactions are
  excluded from the behavioural analyses, matching the paper.

### What it computes

| Section | Reproduces | Paper reference |
|---|---|---|
| **RQ2** | LLM-invocation counts under each caching strategy, by offline replay of the full interaction stream (no-cache, Galah request-exact, path-exact, canonical-only, MolohLLM 3-tier) | Table (RQ2), cost-bounding figure |
| **RQ3** | Response-dependence tests on reconstructed sessions: continuation conditioned on HTTP status, and termination conditioned on latency, with a 15/30/60-minute session-gap sensitivity sweep | Tables (RQ3), logistic model |

### Expected output (abridged)

```
MolohLLM reproducibility report   (SciPy: yes)
Interactions: 12,631 analysed (92 non-routable excluded)   |   unique source IPs: 6,741

====================================================================
RQ2 — LLM inference calls by offline replay of the stream
====================================================================
Strategy                                    LLM calls  vs no-cache  vs MolohLLM
No-cache (stateless)                           12,631        1.00x       21.93x
Galah (request-exact, documented model)         1,867        6.77x        3.24x
Path-exact (hypothetical lower bound)           1,648        7.66x        2.86x
Canonical only (method+path+sorted-params)      1,737        7.27x        3.02x
MolohLLM (3-tier, resources generated)            576       21.93x        1.00x

  Semantic+canonical dedup absorbed 1,072 of 1,648 unique paths (65.0%).

====================================================================
RQ3 — Response-dependent engagement
====================================================================
Session-gap sensitivity (multi-request sessions):
    gap  sessions  multi | P(cont|200) P(cont|404)    chi2         p | P(end|fast) P(end|slow)    chi2         p
   15m      7,924    908 |       0.867       0.676   183.5   8.5e-42 |       0.177       0.068    46.5   9.0e-12
   30m      7,890    891 |       0.871       0.677   192.5   9.0e-44 |       0.174       0.066    45.6   1.4e-11
   60m      7,858    889 |       0.873       0.676   202.8   5.1e-46 |       0.173       0.063    48.3   3.7e-12
```

Interpretation, in short:

- **RQ2** — the semantic (vector) tier reduces model calls **3.24×** below
  a faithful reconstruction of Galah's documented request-exact caching,
  and **2.86×** below a stronger hypothetical path-exact cache.
  Canonicalisation *alone* is worse than path-exact, so the entire saving
  comes from the vector-similarity tier.
- **RQ3** — attacker continuation depends strongly on response status
  (≈87% after HTTP 200 vs ≈68% after 404; χ² ≈ 190), and generation
  latency does **not** increase session abandonment. Both effects are
  stable across session-gap thresholds.

---

## Requirements

- **Reproducibility script:** Python ≥ 3.8 (standard library only; SciPy
  optional).
- **Running the honeypot:** Docker + Docker Compose; an Ollama-served
  open-weight model (default `qwen2.5-coder:3b`) and the
  `nomic-embed-text` embedding model; SQLite with the `sqlite-vss`
  extension; Redis. A single consumer GPU is sufficient (the deployment
  used an RTX 4060 Mobile, 55 W).

---

## Dataset and ethics

The `deployment.db` file is the raw 30-day deployment log (interactions and
generated resources). All content served by the honeypot was
LLM-generated and **synthetic**: the emulated file fragments (e.g.
`/etc/passwd`, SSH keys) are fabricated and correspond to no real system,
no real credentials were ever exposed, and no submitted payload was
executed. Source IPs in released tables are partially anonymised.

The database exposes two primary tables used by `analyze.py`:

- `interactions` — one row per request/response, with `client_ip`,
  `method`, `path`, `query_params`, `semantic_key`, `request_body`,
  `response_body`, `response_status`, `requested_at`, `created_at`.
- `resources` — the canonical generated responses (one per conceptually
  distinct endpoint; `canonical_key` is unique).

---
<!---

## Citation

If you use MolohLLM or this dataset, please cite the accompanying paper.
*(BibTeX to be added on acceptance / camera-ready.)*

## License

*(Add your chosen license, e.g. MIT or Apache-2.0, before public release.)*
--->

## Features

-   🔥 **LLM-powered HTTP honeypot** (no SSH, no Telnet, no mixed
    protocols)
-   🧠 Realistic, model-generated responses to attacker HTTP traffic
-   🐳 Simple and reproducible **Docker Compose** deployment
-   📜 Full logging of interactions
-   🔧 Configurable through environment variables
-   🔄 Automatic model downloading via **Ollama**

------------------------------------------------------------------------

## Environment Variables

You can configure Moloh via `.env`:

### **Model used by the honeypot**

    MODEL="qwen2.5-coder:3b"

### **Optional OpenAI-compatible API**

    OPEN_API_KEY=""

### **Automatic model download via Ollama**

If set, Ollama will fetch the model automatically at container startup:

    DOWNLOAD_MODEL="llama3.1:8b"

------------------------------------------------------------------------

## Model Downloading

Moloh supports two model sources:

### ✔ **Ollama local models**

Ollama will automatically pull the model if:

    DOWNLOAD_MODEL="model_name"

### ✔ **OpenAI-compatible APIs**

If you set:

    OPEN_API_KEY="your-key"

Moloh can route LLM requests through an external API provider.

------------------------------------------------------------------------

## Templates Used by the LLM

Moloh uses predefined system and user prompt templates located here:

    backend/templates/
        mega_prompt_template.txt
        mega_system_prompt_template.txt
        small_prompt_template.txt
        small_system_prompt_template.txt

These define how the model behaves and responds during honeypot
interaction.

------------------------------------------------------------------------

## Deployment

### **Start with Docker Compose**
#### edit .env with your model settings
    cp .env_template .env
    docker-compose up --build

The honeypot will start automatically and download the required model
(if configured).

------------------------------------------------------------------------

## Contributing

Contributions, ideas, and bug reports are welcome!\
Feel free to open an issue or submit a pull request.

Possible areas to improve: - More supported protocols (SMTP,
Telnet, etc.) - Enhanced sandboxing for the LLM backend - Alerting or
monitoring integrations - Better data analysis pipelines

## License

This project is licensed under the **MIT License**

## Contact
For questions or suggestions, feel free to reach out through GitHub
issues.
