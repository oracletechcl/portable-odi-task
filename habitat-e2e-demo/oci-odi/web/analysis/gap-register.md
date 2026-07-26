# Gap Register

| ID | Gap | Effect | Resolution |
| --- | --- | --- | --- |
| GAP-01 | `guardarArchivoAcceso.sh` is referenced but absent. | Its side effects cannot be reproduced safely. | Preserve success/failure semantics; defer shell-specific behavior. |
| GAP-02 | Representative production rows and reconciliation totals are absent. | Production parity cannot be measured offline. | Use deterministic synthetic fixtures and byte-exact golden outputs. |
| GAP-03 | Production schedule, volume, SLA, and retry policy are not evidenced. | No operational targets can be claimed. | Keep configurable and require live owner confirmation. |
| GAP-04 | Existing mock route audit was waived by user direction. | Route/health compatibility is not independently proven. | Trust operator-supplied service on port 8000; keep URL deployment-time only. |
| GAP-05 | OCI workspace/application authorization was not supplied. | Import, materialization, publication, and run remain unverified. | Use `./deploy.sh --config ... --app-name ...` after authorization. |

