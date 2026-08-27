# Data Governance & Privacy Safeguards

## 1. Privacy Principles

Spotify Extended Streaming History contains personal listening behavior, timestamp logs, and connection IP addresses. To protect listener privacy:

1. **Zero Raw Data Publishing**: Raw JSON files with personal IP addresses and granular account details are strictly excluded from public version control via `.gitignore`.
2. **Deterministic Pseudonymization**: Entity IDs (`trk_...`, `art_...`, `prj_...`) are computed via deterministic one-way MD5 hashing.
3. **Public Demonstration Dataset**: A synthetic, sanitized 500-record sample dataset is provided in `data/sample/sample_streaming_history.json` with redacted IP addresses (`0.0.0.0`) for public testing and reproducibility.
4. **Aggregated API Responses**: The REST API serves analytical aggregations, lifecycles, and model inference results rather than exposing raw personal connection logs.
