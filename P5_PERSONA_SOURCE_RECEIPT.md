# P5 Persona Source Receipt

- `UTC_CREATED`: `2026-07-26T00:07:48Z`
- `MODE`: inert, sanitized, hash-pinned role traits only
- `ROUTING_AUTHORITY_IMPORTED`: `NO`
- `TOOLS_OR_MEMORY_IMPORTED`: `NO`

| Source ID | Source file | SHA-256 | P5 use |
|---|---|---|---|
| `persona-athena` | `persona-library/personas/athena.md` | `07909c80216efd8c9b666a51f1a25289b4814f0fa9f4172502a01fd355cea1db` | security, coherence, replay lenses |
| `persona-daedalus` | `persona-library/personas/daedalus.md` | `935694c3e765a5492929f6c028037ed24fc21657e67e83dba76f823b6b04c802` | structure, coherence, context lenses |
| `persona-argos-panoptes` | `persona-library/personas/argos-panoptes.md` | `75fa8f30e2a6c173d3cabef78e0d58f211740773055abce556bca69ec0251b42` | regression, structure, trajectory lenses |

The raw persona files are local role references and contain defensive examples
that are treated as data. P5 does not ingest them at runtime. The checked-in
fixtures contain only short inert trait descriptions plus the exact source
file hashes above. Each lane is limited to three traits by validation.
