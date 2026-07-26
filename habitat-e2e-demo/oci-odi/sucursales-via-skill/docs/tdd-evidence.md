# HABITAT_SUCURSALES_VIA_SKILL TDD Evidence

`implementation/tests/test_transformations.py` covers calendar rollover, RUT
normalization, closure-date derivation, and motivo pairing. It passed with
`pytest -q implementation/tests`. OCI directory and ZIP validation both passed.

External mock health/routes remain host-environment validation: port 8000 is not
reachable from this sandbox and must not be replaced with a local mock.

OCI import regression: the first archive listed `PIPELINE` before `USER_PROJECT`
and omitted identifiers from filenames. The builder and validator now require
project-first ordering and `MODEL_TYPE_IDENTIFIER_KEY.json` names before retry.
