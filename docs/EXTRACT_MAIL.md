# 📧 Extracteur d'Adresses Email

L'outil `extract_mail.py` est un utilitaire pour extraire automatiquement toutes les adresses email uniques de votre boîte mail et les stocker dans un fichier CSV.

## ✨ Fonctionnalités

- ✅ Connexion sécurisée via IMAP SSL
- ✅ Scrute **tous les répertoires** de la boîte mail
- ✅ Parcourt **tous les emails** de chaque dossier
- ✅ Extrait les adresses email des champs: From, To, Cc, Bcc, Reply-To, Sender
- ✅ Stocke les adresses dans un fichier CSV avec **dédupliquée automatique**
- ✅ Ajoute uniquement les **nouvelles adresses** si le fichier existe déjà
- ✅ Trie les adresses par ordre alphabétique

## 🚀 Utilisation

### Méthode 1: Via le script shell (recommandé)

```bash
./extract_mail.sh
```

### Méthode 2: Directement en Python

```bash
python3 src/extract_mail.py
```

## ⚙️ Configuration

L'outil utilise automatiquement les paramètres du fichier `.env`:

- `EMAIL_ADDRESS`: Votre adresse email
- `EMAIL_PASSWORD`: Votre mot de passe ou token d'application
- `IMAP_SERVER`: Serveur IMAP (défaut: `imap.free.fr`)
- `IMAP_PORT`: Port IMAP (défaut: `993`)
- `PROMPT_FOR_CREDENTIALS`: Si `true`, demande les identifiants au démarrage

Exemple `.env`:
```env
EMAIL_ADDRESS=votre.email@free.fr
EMAIL_PASSWORD=votre_mot_de_passe
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
PROMPT_FOR_CREDENTIALS=false
```

## 📊 Résultat

Le script crée un fichier CSV: `data/adresses_emails.csv`

**Format du fichier CSV:**
```csv
Adresse Email
exemple1@domaine.com
exemple2@domaine.com
exemple3@domaine.com
...
```

Les adresses sont:
- ✅ Uniques (pas de doublons)
- ✅ Triées par ordre alphabétique
- ✅ En minuscules pour éviter les doublons
- ✅ Fusionnées avec les adresses existantes

## 📈 Exemple de sortie

```
🔍 EXTRACTEUR D'ADRESSES EMAIL
==================================================
✓ Connecté à votre.email@free.fr

🔎 Extraction des adresses email en cours...
✓ 34 dossier(s) trouvé(s)

📂 Traitement du dossier: achats
  ✓ 2191 email(s) traité(s)

📂 Traitement du dossier: affaires
  ✓ 265 email(s) traité(s)

...

📊 RÉSUMÉ DE L'EXTRACTION
==================================================
Dossiers traités: 34
Emails traités: 15472
Adresses email uniques trouvées: 1547
==================================================

📁 Sauvegarde des adresses...
✓ 1547 adresse(s) email(s) sauvegardée(s)
  → 45 nouvelle(s) adresse(s) ajoutée(s)

✓ Fichier créé: data/adresses_emails.csv
✓ Connexion fermée
```

## 🔒 Sécurité

- Les identifiants sont lus depuis le fichier `.env`
- Jamais sauvegardés dans le code source
- La connexion utilise SSL/TLS (port 993)
- Les mots de passe ne sont jamais affichés

## 📝 Notes

- L'outil traite **tous les dossiers** sans exception
- Peut prendre **quelques minutes** selon le nombre d'emails
- Les adresses `noreply@` et autres adresses système sont incluses
- Vous pouvez filtrer manuellement le fichier CSV après

## 🛠️ Dépendances

- Python 3.6+
- Bibliothèques standard: `imaplib`, `email`, `csv`, `re`, `os`
- `python-dotenv` (pour la lecture du `.env`)

Elles sont déjà installées avec le projet.

## 💡 Cas d'usage

- Créer une liste de diffusion
- Analyser vos contacts
- Migrer vers un autre système de gestion d'emails
- Fusionner plusieurs boîtes mail
- Créer une sauvegarde structurée de vos contacts
