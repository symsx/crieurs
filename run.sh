#!/bin/bash
# Script de lancement - active l'environnement virtuel et exécute le programme

cd "$(dirname "$0")"

# Active l'environnement virtuel
source venv/bin/activate

# Vérifie que .env existe
if [ ! -f .env ]; then
    echo "❌ Erreur: Fichier .env non trouvé!"
    echo ""
    echo "Créez un fichier .env en copiant .env.example:"
    echo "  cp .env.example .env"
    echo ""
    echo "Puis éditez .env avec vos identifiants email."
    exit 1
fi

# Lance le programme (nouvelle version avec deux sources)
cd src
python3 main_v2.py
cd ..

