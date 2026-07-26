# Mock Contract

- `mock-required`: yes
- Mock exists: packaged and deployed application-local service
- Port evidence: OCI and systemd are aligned on `8002`
- Action: immutable release `habitat-web-mock-backend-1.1.0.tar.gz`
- Runtime validation: systemd active, TCP listener confirmed, live route calls not
  performed
- Tracked endpoint: `http://mock-backend.invalid`
- Deployment binding: `MOCK_BASE_URL` in the explicit ignored config

## Required routes

The migration expects synchronous JSON POST boundaries:

- `/v1/web/configuracion-equipo-mesa`
- `/v1/web/configuracion-equipo-usuario`
- `/v1/web/opc-opcion`
- `/v1/web/sec-seccion`
- `/v1/web/sub-subseccion`
- `/v1/web/tb-log-sistema`
- `/v1/web/tb-sub-sistema-servicio`

Request: `{"runDate":"YYYY-MM-DD"}`. Response: a JSON array or an object with
`records`/`rows`, with each row matching the source-derived output schema.

Validator status: `READY_STATIC`. Local HTTP tests cover health, all seven
dataset routes, trailing slashes, malformed payloads, and unknown paths. The
deployed release checksum and registered route table were verified without
calling its HTTP endpoints.
