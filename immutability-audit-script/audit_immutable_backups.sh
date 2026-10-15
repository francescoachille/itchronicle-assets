#!/bin/bash
# ==============================================================================
# Script Name: audit_immutable_backups.sh
# Description: Verifies the immutability status (+i flag) of Linux backups
# Author: IT Chronicle (https://itchronicle.com)
# ==============================================================================

# Configuration: Path to the directory containing the backup repositories

# ==============================================================================
# Script Name: audit_immutable_backups.sh
# Description: Verifica lo stato di immutabilità (flag +i) dei backup su Linux
# Autore: IT Chronicle (https://itchronicle.com)
# ==============================================================================

# Configurazione: Percorso della directory che contiene i repository di backup
BACKUP_DIR="/backup/repository"

# Controllo privilegi di root (necessari per leggere correttamente gli attributi estesi)
if [ "$EUID" -ne 0 ]; then
  echo "[ERRORE] Questo script deve essere eseguito con i privilegi di root (o tramite sudo)." >&2
  exit 1
fi

# Verifica esistenza della directory
if [ ! -d "$BACKUP_DIR" ]; then
  echo "[ERRORE] La directory specificata $BACKUP_DIR non esiste." >&2
  exit 1
fi

echo "=============================================================================="
echo " AVVIO AUDIT IMMUTABILITÀ BACKUP"
echo " Target Directory: $BACKUP_DIR"
echo " Data/Ora: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=============================================================================="
echo ""

# Contatori per il report
total_files=0
immutable_files=0
mutable_files=0

# Scansione ricorsiva dei file all'interno della directory di backup
# Utilizziamo find per isolare i file (escludendo le directory stesse)
while IFS= read -r file; do
  ((total_files++))
  
  # Estrae gli attributi del file usando lsattr
  # L'output tipico è simile a: "----i----------- /backup/repository/file.tar.gz"
  attr_output=$(lsattr -d "$file" 2>/dev/null)
  flags=$(echo "$attr_output" | awk '{print $1}')
  
  # Verifica se il carattere 'i' è presente nella stringa dei flag
  if [[ "$flags" == *i* ]]; then
    ((immutable_files++))
    echo "[PROTETTO]   [IMMUTABILE] -> $file (Flags: $flags)"
  else
    ((mutable_files++))
    echo "[ATTENZIONE] [MUTABILE]   -> $file (Flags: $flags)"
  fi

done < <(find "$BACKUP_DIR" -type f 2>/dev/null)

echo ""
echo "=============================================================================="
echo " REPORT FINALE AUDIT"
echo "------------------------------------------------------------------------------"
echo " Totale file di backup analizzati: $total_files"
echo " File protetti (Immutabili +i):     $immutable_files"
echo " File vulnerabili (Mutabili):       $mutable_files"
echo "=============================================================================="

# Valutazione dello stato di sicurezza complessivo
if [ "$total_files" -eq 0 ]; then
  echo "[INFO] Nessun file trovato nella directory di backup."
  exit 0
elif [ "$mutable_files" -eq 0 ]; then
  echo "[SUCCESSO] Ottimo! Tutti i file di backup sono protetti da immutabilità."
  exit 0
else
  echo "[CRITICO] Rilevati file di backup privi di protezione da immutabilità!"
  exit 2
fi
