param(
    [string]$Workspace = (Get-Location).Path
)

Write-Host "Workspace: $Workspace"

$level1 = Split-Path $Workspace

$target = Join-Path $level1 "development_repos"

if (!(Test-Path $target)) {
    Write-Host "Creating folder: $target"
    New-Item -ItemType Directory -Path $target -Force | Out-Null
} else {
    Write-Host "Folder already exists: $target"
}

Write-Host "Done."
