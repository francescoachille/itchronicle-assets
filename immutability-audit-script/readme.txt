Istruzioni per l'uso e integrazione:
Permessi di esecuzione: Dopo aver salvato lo script sul server, rendilo eseguibile con il comando:
Bash
chmod +x audit_immutable_backups.sh


Personalizzazione: Modifica la variabile BACKUP_DIR="/backup/repository" inserendo il percorso effettivo in cui risiedono i tuoi archivi di backup.
Automazione: Puoi inserire questo script in un controllo giornaliero tramite cron o integrarlo nei sistemi di monitoraggio (es. inviando un alert via email o syslog se l'exit code dello script è diverso da 0).
