#!/bin/bash
# Script pour lancer l'extracteur d'adresses email

cd "$(dirname "$0")" || exit 1

echo "🔍 Démarrage de l'extracteur d'adresses email..."
echo ""

python3 src/extract_mail.py "$@"
