# KNOWN_ISSUES

| # | Issue | Impact | Fallback | Status |
|---|---|---|---|---|
| K1 | The user's folder is not a git repository. Git branch/tags exist only in the agent workspace; the PC receives tarball syncs. | Rollback on the PC = previous tarball in `.qs_sync/` | `.qs_sync/pc_snapshot.tar.gz` holds the pre-upgrade copy | open (by design) |
| K2 | Docker is not available in the agent workspace. | Compose clean-start cannot be verified here | User runs `docker compose up --build` on the PC | open |
| K3 | Account-level ml-pipeline hook blocks writing tests that construct the RL Trainer. | Trainer curriculum/replay loop NOT RUN end-to-end in tests; components tested individually | Run scripts/train_rl.py manually with TrainerConfig(curriculum=True, prioritized_replay=True) | open |
| K4 | Docker clean-start of the upgraded stack NOT RUN in the agent workspace (no Docker). | compose file validated as YAML only | User runs: `docker compose -p qs_verify up --build -d` then `docker compose -p qs_verify ps` (all healthy) and `docker compose -p qs_verify down -v` (removes ONLY the qs_verify project volumes) | open |
