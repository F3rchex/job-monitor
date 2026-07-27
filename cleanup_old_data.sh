#!/bin/bash

# Mantener solo los ultimos 10 archivos de cada fuente
echo "=== Limpieza de datos antiguos - $(date) ==="

# InfoJobs
cd /home/fernando/job-monitor/data-infojobs/
ANTES=$(ls *.json 2>/dev/null | wc -l)
ls -t *.json 2>/dev/null | tail -n +11 | xargs -r rm
DESPUES=$(ls *.json 2>/dev/null | wc -l)
echo "InfoJobs: $ANTES archivos -> $DESPUES archivos (borrados: $((ANTES - DESPUES)))"

# Indeed
cd /home/fernando/job-monitor/data-indeed/
ANTES=$(ls *.json 2>/dev/null | wc -l)
ls -t *.json 2>/dev/null | tail -n +11 | xargs -r rm
DESPUES=$(ls *.json 2>/dev/null | wc -l)
echo "Indeed: $ANTES archivos -> $DESPUES archivos (borrados: $((ANTES - DESPUES)))"

echo "Limpieza completada"
