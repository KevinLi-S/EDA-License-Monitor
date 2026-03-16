## [ERR-20260313-001] local-backend-selftest

**Logged**: 2026-03-13T14:50:00+08:00
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
Local TestClient self-check for `eda-license-hub-v1.4.0` failed because APScheduler is not installed in the current host Python environment.

### Error
```
ModuleNotFoundError: No module named 'apscheduler'
```

### Context
- Attempted to import `app.main` and run FastAPI `TestClient`
- Project path: `C:\Tools\LM\eda-license-hub-v1.4.0`
- Failure occurs at `backend/app/collectors/scheduler.py` import time
- This confirms the py36/offline dependency gap is real, not hypothetical

### Suggested Fix
- Treat `APScheduler` as a required offline dependency for packaging
- Ensure matching py36-compatible APScheduler (and its dependency wheels such as `tzlocal`) are present in `backend/offline/wheels-py36`
- If needed, add graceful import handling for local no-scheduler diagnostic runs

### Metadata
- Reproducible: yes
- Related Files: C:\Tools\LM\eda-license-hub-v1.4.0\backend\app\collectors\scheduler.py, C:\Tools\LM\eda-license-hub-v1.4.0\backend\requirements-py36.txt

---
## [ERR-20260316-001] exec.powershell-chaining

**Logged**: 2026-03-16T10:33:52.4396817+08:00
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
PowerShell exec command failed when using bash-style && chaining.

### Error
`
The token '&&' is not a valid statement separator in this version.
`

### Context
- Command attempted: git status --short && git add IDENTITY.md && git commit -m "Update assistant name to Κ―Αρ"
- Environment: OpenClaw exec using PowerShell on Windows

### Suggested Fix
Use PowerShell separators like ; with explicit exit checks, or invoke through bash/cmd when chaining syntax is required.

### Metadata
- Reproducible: yes
- Related Files: .learnings/ERRORS.md, TOOLS.md

---
