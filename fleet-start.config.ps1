# Per-repo fleet start config for pinokio-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'pinokio-mcp'
    BackendPort  = 0
    FrontendPort = 0
    HealthPath   = '/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind = 'none'
    }
    Frontend = @{
        Kind = 'none'
    }
}
