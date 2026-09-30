<#
.SYNOPSIS
    Verifica la prontezza del sistema per l'upgrade a Windows 11 (Focus su TPM e Secure Boot).
.DESCRIPTION
    Lo script controlla se il modulo TPM è presente, pronto e in versione 2.0.
    Verifica inoltre se il Secure Boot è abilitato nel firmware UEFI.
#>

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Verifica Requisiti Windows 11          " -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan

# 1. Verifica TPM
Write-Host "[*] Controllo modulo TPM..."
try {
    $tpm = Get-Tpm
    if ($tpm.TpmPresent) {
        # La proprietà TpmReady indica se è pronto all'uso
        if ($tpm.TpmReady) {
            Write-Host "    [OK] TPM rilevato e pronto all'uso." -ForegroundColor Green
        } else {
            Write-Host "    [WARNING] TPM presente ma non inizializzato." -ForegroundColor Yellow
        }
    } else {
        Write-Host "    [ERRORE] Nessun modulo TPM rilevato sulla scheda madre." -ForegroundColor Red
    }
} catch {
    Write-Host "    [ERRORE] Impossibile interrogare il TPM. Assicurati di eseguire come Amministratore." -ForegroundColor Red
}

# 2. Verifica Secure Boot
Write-Host "`n[*] Controllo Secure Boot..."
try {
    $secureBoot = Confirm-SecureBootUEFI
    if ($secureBoot) {
        Write-Host "    [OK] Secure Boot abilitato nel firmware UEFI." -ForegroundColor Green
    } else {
        Write-Host "    [ERRORE] Secure Boot disabilitato. È necessario attivarlo nel BIOS/UEFI." -ForegroundColor Red
    }
} catch {
    Write-Host "    [ERRORE] Cmdlet non supportata o sistema in modalità BIOS Legacy (non UEFI)." -ForegroundColor Red
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Controllo terminato." -ForegroundColor Cyan
