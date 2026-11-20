<#
.SYNOPSIS
    NTLM Audit and Hardening Helper Script for Active Directory
.DESCRIPTION
    This script helps administrators query security event logs for NTLM authentication events (Event ID 8004)
    and assists in identifying potential legacy application bottlenecks before enforcing NTLM blocks.
#}

Write-Host "[*] Starting NTLM Authentication Audit Check..." -ForegroundColor Cyan

# Check if running with Administrator privileges
If (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "[!] Please run this script with Domain Administrator privileges!"
    Exit
}

# Query Event ID 8004 from local security log (or point to DC)
Try {
    $ntlmEvents = Get-WinEvent -FilterHashtable @{LogName='Security'; ID=8004} -MaxEvents 50 -ErrorAction Stop
    Write-Host "[+] Found $($ntlmEvents.Count) recent NTLM authentication events." -ForegroundColor Green
    
    foreach ($event in $ntlmEvents) {
        $xml = [xml]$event.ToXml()
        $targetName = $xml.Event.EventData.Data | Where-Object {$_.Name -eq 'TargetUserName'}
        $workstation = $xml.Event.EventData.Data | Where-Object {$_.Name -eq 'WorkstationName'}
        
        Write-Host "    - Time: $($event.TimeCreated) | User: $($targetName.('#text')) | Source: $($workstation.('#text'))" -ForegroundColor Yellow
    }
}
Catch {
    Write-Host "[-] No NTLM audit events found (or Auditing is not yet enabled on this machine)." -ForegroundColor Red
}

Write-Host "[*] Recommendation: Ensure GPO for NTLM Auditing is fully deployed before setting 'Deny all'." -ForegroundColor Cyan