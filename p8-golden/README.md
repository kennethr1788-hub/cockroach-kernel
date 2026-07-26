# P8 Golden Validation

This local synthetic layer records success and failure incidents, treats
reflection proposals as untrusted input, and replays every proposal against a
frozen incident set. A deterministic authority function produces an
evidence-backed promotion or rejection receipt for every proposal.

It does not train a foundation model, call a model, mutate policy silently,
access a network service, or write outside its generated trial roots.

Run:

```sh
python3 p8-golden/make_fixtures.py
(cd p8-golden && PYTHONWARNINGS=error python3 -m unittest -v)
python3 p8-golden/run_integration.py
```
