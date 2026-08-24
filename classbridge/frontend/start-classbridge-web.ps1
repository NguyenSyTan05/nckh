$ErrorActionPreference = "Stop"
$webRoot = $PSScriptRoot
Set-Location -LiteralPath $webRoot
& (Get-Command npm.cmd).Source run dev
exit $LASTEXITCODE
