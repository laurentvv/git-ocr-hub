<#
.SYNOPSIS
    Interface PowerShell pour Git OCR Hub.
.DESCRIPTION
    Permet de piloter la supervision Git, la synchronisation sécurisée et les revues de code IA locales.
.PARAMETER Action
    Choix de l'action : 'status', 'sync', 'review', 'all', 'dashboard'.
.EXAMPLE
    .\run-hub.ps1 status
    .\run-hub.ps1 all -OpenDashboard
#>

[CmdletBinding()]
param (
    [Parameter(Position = 0)]
    [ValidateSet("status", "sync", "review", "scan", "all", "dashboard", "help")]
    [string]$Action = "",

    [string]$Repo = "",
    [string]$Path = "",
    [string]$Commit = "",
    [switch]$Preview,
    [switch]$OpenDashboard,
    [int]$Timeout = 600
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Vérification de Python
$pythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "Python 3 est requis mais n'a pas été trouvé dans votre PATH."
    exit 1
}

# 2. Menu interactif si aucune action spécifiée
if (-not $Action) {
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "                Git OCR Hub - Menu Principal              " -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "  1. Afficher l'état de tous les dépôts (status)"
    Write-Host "  2. Synchroniser les dépôts propres (sync : fetch + pull FF)"
    Write-Host "  3. Revue diff OCR sur modifications locales (review)"
    Write-Host "  4. Audit complet d'un dépôt entier sans diff (scan)"
    Write-Host "  5. Exécution complète (sync + review + dashboard)"
    Write-Host "  6. Ouvrir le Dashboard HTML dans le navigateur (dashboard)"
    Write-Host "  Q. Quitter"
    Write-Host "==========================================================" -ForegroundColor Cyan
    $choice = Read-Host "Votre choix (1-6 ou Q)"

    switch ($choice) {
        "1" { $Action = "status" }
        "2" { $Action = "sync" }
        "3" { $Action = "review" }
        "4" {
            $Action = "scan"
            $Repo = Read-Host "Chemin du dépôt à auditer (ex: C:\GIT\mon-depot)"
            $OpenDashboard = $true
        }
        "5" { $Action = "all"; $OpenDashboard = $true }
        "6" { $Action = "dashboard" }
        default { Write-Host "Opération annulée."; exit 0 }
    }
}

# 3. Exécution de la commande Python correspondante
$orchestratorPath = Join-Path $ScriptDir "orchestrator.py"
$pyArgs = @($orchestratorPath, $Action)

if ($Action -eq "review") {
    if ($Repo) { $pyArgs += @("--repo", $Repo) }
    if ($Commit) { $pyArgs += @("--commit", $Commit) }
    if ($Preview) { $pyArgs += "--preview" }
    if ($OpenDashboard) { $pyArgs += "--open" }
    $pyArgs += @("--timeout", $Timeout)
}
elseif ($Action -eq "scan") {
    if ($Repo) { $pyArgs += @("--repo", $Repo) }
    if ($Path) { $pyArgs += @("--path", $Path) }
    if ($Preview) { $pyArgs += "--preview" }
    if ($OpenDashboard) { $pyArgs += "--open" }
    $pyArgs += @("--timeout", $Timeout)
}
elseif ($Action -eq "all") {
    if ($OpenDashboard) { $pyArgs += "--open" }
    $pyArgs += @("--timeout", $Timeout)
}

& $pythonCmd.Source @pyArgs
