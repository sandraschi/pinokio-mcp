# Copilot instructions (Pinokio-MCP)

Pinokio app control via MCP: list, launch, stop, monitor local AI apps.

Before starting work:
1. `system_management(action="ping")` — confirm Pinokio is reachable
2. `app_management(action="list")` — see installed apps and running state

At end of work:
- Stop anything you started: `app_management(action="stop", app="<folder>")`
