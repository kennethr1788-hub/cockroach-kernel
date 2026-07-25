# P4 deterministic verifier

This verifier is standard-library-only, deterministic, offline, and model-free.
Quarantined records are stored separately and have no active retrieval path.
Verdicts are `PROMOTE`, `REFUSE`, or `INVALID` with stable reason codes.
