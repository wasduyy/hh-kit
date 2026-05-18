$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot | Split-Path -Parent | Split-Path -Parent
Set-Location $ProjectRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv not found. Install: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
}

$HarnessDir = Join-Path $ProjectRoot ".harness"
$VenvPython = Join-Path $ProjectRoot ".venv" "Scripts" "python.exe"
$ControlDir = Join-Path $ProjectRoot ".control"
$HarnessYml = Join-Path $ControlDir "harness.yml"

$ProjectName = ""
if (Test-Path $HarnessYml) {
    $content = Get-Content $HarnessYml -Raw
    if ($content -match 'name:\s*"([^"]+)"') {
        $ProjectName = $Matches[1]
    }
}
$McpServerName = if ($ProjectName) { "hh-kit--$ProjectName" } else { "hh-kit" }

Set-Location $HarnessDir

if (-not (Test-Path $VenvPython)) {
    Write-Output "[1/4] Creating venv and installing dependencies..."
    uv sync
} else {
    Write-Output "[1/4] venv already exists, checking dependencies..."
    uv sync
}

Write-Output "[2/4] Verifying MCP Server..."
& $VenvPython -c "import sys; sys.path.insert(0, '.scaffold/mcp-server'); import server; print('  OK')"

$pythonJson = ($VenvPython -replace '\\', '\\')
$projectJson = ($ProjectRoot -replace '\\', '\\')

$mcpJson = @"
{
    "mcpServers": {
        "$McpServerName": {
            "command": "$pythonJson",
            "args": [".harness/.scaffold/mcp-server/server.py"],
            "cwd": "$projectJson"
        }
    }
}
"@

Write-Output "[3/4] Generating .trae/mcp.json..."
$traeDir = Join-Path $ProjectRoot ".trae"
if (-not (Test-Path $traeDir)) { New-Item -ItemType Directory -Path $traeDir -Force | Out-Null }
$mcpPath = Join-Path $traeDir "mcp.json"
[System.IO.File]::WriteAllText($mcpPath, $mcpJson, [System.Text.Encoding]::UTF8)
Write-Output "  Written: .trae/mcp.json"
Write-Output "  MCP server name: $McpServerName"
Write-Output "  Python: $VenvPython"

Write-Output "[4/4] Copying rules to .trae/rules/..."
$rulesDir = Join-Path $traeDir "rules"
if (-not (Test-Path $rulesDir)) { [System.IO.Directory]::CreateDirectory($rulesDir) | Out-Null }
$srcRules = Join-Path $HarnessDir ".scaffold\adapters\trae\rules-template.md"
$projectRules = Join-Path $ProjectRoot ".trae\rules\project_rules.md"
if (Test-Path $projectRules) {
    Write-Output "  SKIP: .trae/rules/project_rules.md already exists"
} elseif (Test-Path $srcRules) {
    [System.IO.File]::Copy($srcRules, $projectRules, $false)
    Write-Output "  Written: .trae/rules/project_rules.md (from template)"
} else {
    Write-Output "  SKIP: no rules template found"
}

Write-Output ""
Write-Output "Done. Restart Trae IDE to load MCP Server and rules."
