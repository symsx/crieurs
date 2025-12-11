#!/bin/bash
# Script de lancement - traite les fichiers .eml du dossier CE

cd "$(dirname "$0")"

# Active l'environnement virtuel
source venv/bin/activate

# Lance le programme pour fichiers .eml
python3 main_eml.py
