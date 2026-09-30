<#
.SYNOPSIS
    Active Directory SPN Scanner for Kerberoasting Vulnerabilities.
    Scanner di SPN in Active Directory per vulnerabilità Kerberoasting.

.DESCRIPTION
    EN: This script queries Active Directory for active user accounts that have a Service Principal Name (SPN) set,
        making them potential targets for Kerberoasting. It checks the 'msDS-SupportedEncryptionTypes'
        attribute to identify accounts that do not explicitly enforce AES encryption, meaning they
        might fall back to weak RC4 encryption.

    IT: Questo script interroga Active Directory per trovare account utente attivi con un Service Principal Name (SPN) configurato,
        il che li rende potenziali bersagli per il Kerberoasting. Controlla l'attributo 'msDS-SupportedEncryptionTypes'
        per identificare gli account che non forzano esplicitamente la cifratura AES e che potrebbero quindi
        ripiegare sulla più debole cifratura RC4.
#>

# EN: Import the ActiveDirectory module. Ensure you are running this on a domain-joined machine with RSAT installed.
# IT: Importa il modulo ActiveDirectory. Assicurati di eseguire lo script su una macchina a dominio con RSAT installato.
Import-Module ActiveDirectory -ErrorAction Stop

# EN: Define an array to hold the vulnerable accounts.
# IT: Definisce un array per contenere gli account vulnerabili trovati.
$VulnerableAccounts = @()

# EN: Query AD for any user account with at least one SPN registered.
# IT: Interroga AD per qualsiasi account utente con almeno un SPN registrato.
# EN: We use an LDAP filter to exclude disabled accounts (userAccountControl) to reduce noise and focus on active threats.
# IT: Usiamo un filtro LDAP per escludere gli account disabilitati per ridurre il rumore e concentrarci sulle minacce attive.
$LDAPFilter = "(&(servicePrincipalName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
$AccountsWithSPN = Get-ADUser -LDAPFilter $LDAPFilter -Properties servicePrincipalName, msDS-SupportedEncryptionTypes, PasswordLastSet

foreach ($Account in $AccountsWithSPN) {
    
    $EncType = $Account.'msDS-SupportedEncryptionTypes'
    $IsWeak = $false

    # EN: In AD, AES128 is represented by the bitwise value 8, and AES256 by 16. Combined (24).
    # EN: If the attribute is not set ($null) or the bitwise check for AES returns 0, the account allows RC4.
    # IT: In AD, AES128 è rappresentato dal valore bitwise 8, e AES256 da 16. Insieme (24).
    # IT: Se l'attributo non è impostato ($null) o il controllo bitwise per AES restituisce 0, l'account permette RC4.
    if ($null -eq $EncType -or ($EncType -band 24) -eq 0) {
        $IsWeak = $true
    }

    if ($IsWeak) {
        # EN: Create a custom object to neatly format the output.
        # IT: Crea un oggetto personalizzato per formattare ordinatamente l'output.
        $Obj = [PSCustomObject]@{
            AccountName     = $Account.SamAccountName
            PasswordLastSet = if ($Account.PasswordLastSet) { $Account.PasswordLastSet.ToString("yyyy-MM-dd") } else { "N/A" }
            # EN: Join multiple SPNs into a single string for readability.
            # IT: Unisce più SPN in un'unica stringa separata da punto e virgola per una migliore leggibilità.
            SPN_List        = $Account.servicePrincipalName -join "; "
            AES_Enforced    = $false
            RiskLevel       = "Critical / Critico"
        }
        $VulnerableAccounts += $Obj
    }
}

# EN: Output the results to the console.
# IT: Mostra i risultati nella console.
Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " IT Chronicle - Active Directory Kerberoasting Scanner   " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

if ($VulnerableAccounts.Count -gt 0) {
    Write-Host "[!] Found $($VulnerableAccounts.Count) vulnerable accounts. / Trovati $($VulnerableAccounts.Count) account vulnerabili." -ForegroundColor Red
    Write-Host "[!] Action required: Implement gMSA or enforce AES. / Azione richiesta: Implementare gMSA o forzare AES." -ForegroundColor Yellow
    Write-Host ""
    
    # EN: Display as a formatted table. Can be exported to CSV by piping to Export-Csv.
    # IT: Mostra come tabella formattata. Può essere esportato in CSV aggiungendo Export-Csv alla pipeline.
    $VulnerableAccounts | Format-Table -AutoSize
} else {
    Write-Host "[V] No vulnerable accounts found. Great job! / Nessun account vulnerabile trovato. Ottimo lavoro!" -ForegroundColor Green
}
