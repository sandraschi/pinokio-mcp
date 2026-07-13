param(
    [string]$HostName = "localhost",
    [int]$PortMin = 42000,
    [int]$PortMax = 42059
)

$found = $null
for ($port = $PortMin; $port -le $PortMax; $port++) {
    $url = "http://${HostName}:$port/check"
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) {
            $found = $port
            Write-Host "Pinokio /check OK on port $port" -ForegroundColor Green
            break
        }
    }
    catch {
        continue
    }
}

if (-not $found) {
    Write-Host "No Pinokio daemon on ${HostName}:$PortMin-$PortMax" -ForegroundColor Yellow
    exit 1
}

$base = "http://${HostName}:$found"
$endpoints = @("/pinokio/info", "/pinokio/port", "/proxy")
foreach ($ep in $endpoints) {
    $url = "$base$ep"
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        Write-Host "$ep -> $($resp.StatusCode)" -ForegroundColor Cyan
    }
    catch {
        Write-Host "$ep -> failed: $($_.Exception.Message)" -ForegroundColor DarkYellow
    }
}

exit 0
