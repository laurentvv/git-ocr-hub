<#
.SYNOPSIS
    Surveille la fin du processus de scan OCR et joue une alerte sonore et vocale.
#>
param(
    [int[]]$ProcessIds = @(24480, 24308)
)

$running = $ProcessIds | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }

if ($running) {
    Write-Host "En attente de la fin des processus : $($running -join ', ')..."
    Wait-Process -Id $running -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 1

Write-Host "Le scan est terminé ! Émission de la notification sonore..."

# 1. Carillon mélodique ascendant (Do-Mi-Sol-Do)
[Console]::Beep(523, 180) # C5
[Console]::Beep(659, 180) # E5
[Console]::Beep(784, 180) # G5
[Console]::Beep(1046, 450) # C6

# 2. Son système Windows
[System.Media.SystemSounds]::Exclamation.Play()

# 3. Notification vocale en français
try {
    Add-Type -AssemblyName System.Speech -ErrorAction SilentlyContinue
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.Rate = 0
    $synth.Speak("Le scan de code est terminé.")
} catch {
    # Fallback si Speech Synthesizer indisponible
    [Console]::Beep(880, 400)
}

Write-Host "Notification terminée."
