#!/bin/bash
# Script de migration vers la structure GitHub
# Organise les fichiers dans les répertoires appropriés

echo "🔄 Préparation du projet pour GitHub..."

# Créer les répertoires s'ils n'existent pas
mkdir -p src output data public docs tests

# Copier les fichiers Python vers src/
echo "📁 Déplacement des fichiers Python..."
cp -v main.py src/main.py
cp -v email_reader.py src/email_reader.py
cp -v geocoding.py src/geocoding.py

# Copier les fichiers front vers public/
echo "📁 Déplacement des fichiers web..."
cp -v style.css public/style.css
cp -v script.js public/script.js
cp -v script_carte.js public/script_carte.js

# Copier les fichiers de données vers data/
echo "📁 Déplacement des fichiers de données..."
[ -f corrections_annonces.json ] && cp -v corrections_annonces.json data/corrections_annonces.json
[ -f corrections_geolocalisation.json ] && cp -v corrections_geolocalisation.json data/corrections_geolocalisation.json
[ -f communes_coordinates.json ] && cp -v communes_coordinates.json data/communes_coordinates.json

# Créer un fichier .gitkeep dans output/ (pour conserver le dossier vide)
touch output/.gitkeep
touch data/.gitkeep

echo "✅ Migration terminée!"
echo ""
echo "Fichiers organisés :"
echo "  src/             → Code Python (main.py, email_reader.py, geocoding.py)"
echo "  public/          → Assets web (CSS, JavaScript)"
echo "  data/            → Fichiers de configuration et cache"
echo "  output/          → Fichiers générés (HTML, carte)"
echo "  docs/            → Documentation"
echo "  tests/           → Tests unitaires (à créer)"
echo ""
echo "⚠️  ATTENTION: Fichiers originaux non supprimés!"
echo "Vérifiez que tout fonctionne, puis supprimez les originaux:"
echo "  rm main.py email_reader.py geocoding.py"
echo "  rm style.css script.js script_carte.js"
echo "  rm corrections_*.json communes_coordinates.json"
