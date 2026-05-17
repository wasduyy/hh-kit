$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot | Split-Path -Parent | Split-Path -Parent
Set-Location $ProjectRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv not found. Install: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
}

Set-Location ".harness"

if (-not (Test-Path "../.venv/Scripts/python.exe")) {
    Write-Output "[1/4] Creating venv and installing dependencies..."
    uv run python --version
} else {
    Write-Output "[1/4] venv already exists, checking dependencies..."
    uv sync
}

Write-Output "[2/4] Verifying MCP Server..."
& "..\.venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, '.scaffold/mcp-server'); import server; print('  OK')"

$pythonAbs = (Resolve-Path "..\.venv\Scripts\python.exe").Path
$pythonJson = $pythonAbs -replace '\\', '\\'
$projectAbs = (Resolve-Path "..").Path
$projectJson = $projectAbs -replace '\\', '\\'

$mcpJson = @"
{
    "mcpServers": {
        "harness": {
            "command": "$pythonJson",
            "args": [".harness/.scaffold/mcp-server/server.py"],
            "cwd": "$projectJson"
        }
    }
}
"@

Write-Output "[3/4] Generating .trae/mcp.json..."
$mcpDir = (Resolve-Path "..\.trae").Path
if (-not (Test-Path $mcpDir)) { New-Item -ItemType Directory -Path $mcpDir -Force | Out-Null }
$mcpPath = Join-Path $mcpDir "mcp.json"
[System.IO.File]::WriteAllText($mcpPath, $mcpJson, [System.Text.Encoding]::UTF8)
Write-Output "  Written: .trae/mcp.json"
Write-Output "  Python: $pythonAbs"

Write-Output "[4/4] Copying rules to .trae/rules/..."
$rulesDir = Join-Path $mcpDir "rules"
if (-not (Test-Path $rulesDir)) { [System.IO.Directory]::CreateDirectory($rulesDir) | Out-Null }
$srcRules = Join-Path $PWD ".scaffold\adapters\trae\rules-template.md"
$dstRules = Join-Path $rulesDir "project_rules.md"
[System.IO.File]::Copy($srcRules, $dstRules, $true)
Write-Output "  Written: .trae/rules/project_rules.md"

Write-Output ""
Write-Output "Done. Restart Trae IDE to load MCP Server and rules."
