---
name: pinokio
description: Control Pinokio AI apps - list, launch, stop, monitor local installs.
---

# Pinokio skill (Antigravity)

Pinokio app control via MCP (this repo's tools only).

Before starting work:
1. `system_management(action="ping")` - confirm Pinokio is reachable
2. `app_management(action="list")` - see installed apps and running state

At end of work:
- Stop anything you started: `app_management(action="stop", app="<folder>")`
