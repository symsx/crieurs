# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projet

Crieurs lit les digests d'annonces du réseau « Crieurs Périgord-Limousin » (listes de diffusion Zimbra/Free hébergées sur `gco.ouvaton.net`) par IMAP, et génère des pages HTML statiques (liste + carte Leaflet) pour chaque type d'annonce, puis les envoie éventuellement par FTP. Le code, les commentaires et les messages console sont en français.

## Commandes

```bash
# Sur cette machine (Python 3.14, sans python3.14-venv/ensurepip) : venv sans pip puis amorçage depuis la wheel système
python3 -m venv --without-pip venv
venv/bin/python /usr/share/python-wheels/pip-*.whl/pip install pip
venv/bin/pip install -r requirements.txt   # htmlmin2 remplace htmlmin (cassé depuis Python 3.13 : module cgi supprimé)
cp .env.example .env                       # identifiants IMAP + FTP (chmod 600)

./run.sh            # point d'entrée réel : active venv, puis `cd src && python3 main_v2.py`
```

- Les scripts doivent être lancés **depuis `src/`** : les imports sont plats (`from email_reader import ...`, `from geocoding import ...`), pas `from src.…` comme l'indique `docs/PROJECT_STRUCTURE.md`.
- Il n'y a pas de tests automatisés (`tests/` est vide) ni de linter configuré. Les fichiers `test`, `test2`, `test3` à la racine sont des exemples bruts de digests (texte d'emails), utiles comme échantillons pour mettre au point le parsing.
- `run_eml.sh` / `main_eml.py` (mode fichiers `.eml` depuis `./CE`) et `src/main.py` (version mono-source) sont **legacy** : `main_eml.py` importe `email_reader` depuis la racine et ne fonctionne plus depuis le déplacement dans `src/`.

## Architecture

Pipeline dans `src/main_v2.py` → `main()` itère sur la liste `sources` (4 sources actuellement : Sorties, Expression Libre, Solidaire, Annonces Commerciales). Pour chaque source, `process_annonces_source()` :

1. **IMAP** — `EmailReader.get_emails()` (`src/email_reader.py`) lit `MAIL_FOLDER`, filtré par `DOMAIN_FILTER`. Note : une nouvelle connexion IMAP est ouverte pour chaque source.
2. **Filtre sujet** — garde les emails dont le sujet contient `source['filter']` (nom de la liste, ex. `crieur-des-sorties`).
3. **Extraction** — deux stratégies selon la source :
   - *Structurée* (sorties et autres) : `extract_sommaire` → `parse_events_from_sommaire` (lignes `* N - [liste] [Commune] - Titre - date - orga <mail>`) + `extract_messages`/`extract_message_fields` (blocs `Quand :`, `Où :`, descriptif…) puis `consolidate_events` fusionne les deux par titre. La commune vient de `types[1]` (2ᵉ crochet du sommaire).
   - *Texte libre* (`crieur-libre-expression` uniquement) : `extract_libre_expression_events` — texte entre lignes de tirets, pas de date. Voir `docs/EXPRESSION_LIBRE_PARSING.md`.
4. **Corrections manuelles** — `data/corrections_annonces.json`, indexé par titre exact (la clé `date` écrase `date_heure_sommaire`).
5. **Mapping** vers le dict attendu par `HTMLGenerator` (`subject`, `date`, `location`, `description`, `links`, `commune`, `is_libre_expression`…).
6. **Rendu** — `HTMLGenerator.generate()` et `generate_map_html()` dans `src/email_reader.py` produisent `output/<source>.html` et `output/carte_<source>.html`. Le HTML est écrit en f-strings dans le Python ; les pages référencent `../public/style.css`, `../public/script.js`, `../public/script_carte.js`.
7. **FTP** (si `ENABLE_FTP_UPLOAD=true`) — `ftp_upload()` envoie `output/` vers `FTP_REMOTE_PATH/output`, `upload_static_files()` envoie `public/` vers `FTP_REMOTE_PATH/public` (`src/ftp_uploader.py`).

Outils annexes, indépendants du pipeline : `src/extract_mail.py` (via `./extract_mail.sh`, qui appelle `python3` sans activer le venv) parcourt tous les dossiers IMAP et collecte les adresses From/To/Cc dans `data/adresses_emails.csv` ; `src/analyze_emails.py` en tire des statistiques et un export par domaine (`data/emails_by_domain/`). Voir `docs/OUTILS_EMAILS.md`. Le CSV contient des adresses personnelles : ne pas le committer.

Il reste un `EventExtractor` (regex de dates/lieux) dans `email_reader.py` : il n'est utilisé que par les chemins legacy, pas par `main_v2.py`.

### Ajouter / modifier une source

Ajouter une source exige de toucher plusieurs endroits couplés par le **nom** de la source (`source['name']`, copié dans `generator.source_type`) :

- la liste `sources` dans `main_v2.py` ;
- dans `HTMLGenerator.generate()` : le choix du lien carte du menu, le menu `top-navigation` codé en dur, et `window.currentPage` ;
- `public/script.js` / `public/style.css` pour l'état actif du menu (classes `active-if-*`).
Le filtre de date « À venir / Toutes » n'est affiché que pour `source_type == "Sorties"`.

### Géolocalisation (`src/geocoding.py`)

`Geocoder.geocode()` est appelé depuis `generate_map_html` via `add_coordinates_to_events`. Ordre de résolution : cache `data/lieux_coordinates.json` (écrit automatiquement après chaque appel API) → `data/corrections_geolocalisation.json` → API Nominatim (adresse avec code postal ou commune simple) → base locale `data/communes_coordinates.json` → commune extraite + Nominatim. Les résultats Nominatim sont priorisés sur les départements 24, 16, 87, 19. Pour corriger un lieu mal placé, ajouter une entrée dans `corrections_geolocalisation.json` ou corriger `lieux_coordinates.json` (le cache passe **avant** les corrections). Voir `docs/CACHE_LOCALISATION.md`.

`communes_coordinates.json` est gitignoré et absent du dépôt ; `main_v2.extract_commune_from_location` le cherche à la racine du projet alors que `Geocoder` le cherche dans `data/`.

## Pièges

- `.gitignore` exclut `*.html` (hors `public/` et `docs/`) et `output/` : les pages générées ne sont jamais versionnées.
- Les fichiers `corrections_*.json` à la racine sont des doublons hérités de `migrate.sh` ; le code lit uniquement ceux de `data/`.
- Plusieurs .md à la racine (`GITHUB_PREP.md`, `PREPARATION_GITHUB.md`, `SUMMARY_GITHUB_PREP.txt`, `SYNTHESE_EVOLUTION.md`…) sont des notes historiques ; README et `docs/` décrivent encore 2 sources alors que le code en gère 4 — se fier au code.
