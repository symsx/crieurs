# 📧 Email Announcement Reader - Crieurs

Outil pour lire vos emails d'annonces d'événements et les afficher sous forme de page HTML avec date, lieu et sujet de l'événement.

**✅ Adapté pour Zimbra Free** avec extraction depuis le dossier "CE"

## 🚀 Installation rapide

### 1. Installez les dépendances

```bash
cd /home/sylvain/Documents/crieurs
pip install -r requirements.txt
```

### 2. Configurez votre email

Éditez le fichier `.env`:

```bash
nano .env
```

Remplissez avec vos identifiants:

```env
EMAIL_ADDRESS=scregut@free.fr
EMAIL_PASSWORD=votre_mot_de_passe
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
MAIL_FOLDER=CE
EMAIL_LIMIT=50
```

### 3. Lancez le programme

```bash
./run.sh
```

Le fichier `events.html` sera généré et contendra tous vos événements !

## 📋 Configuration par fournisseur

### Free (Zimbra) - **VOTRE CONFIGURATION**
```env
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
MAIL_FOLDER=CE
```

### Gmail
```env
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
EMAIL_PASSWORD=(token d'application uniquement)
```

### Outlook/Hotmail
```env
IMAP_SERVER=imap-mail.outlook.com
IMAP_PORT=993
```

### Orange
```env
IMAP_SERVER=imap.orange.fr
IMAP_PORT=993
```

### SFR
```env
IMAP_SERVER=imap.sfr.fr
IMAP_PORT=993
```

## 📖 Modes d'utilisation

### Mode 1: Lire depuis votre boîte mail (IMAP)

```bash
./run.sh
```

ou

```bash
source venv/bin/activate
python3 main.py
```

**Recommandé pour une utilisation régulière!**

### Mode 2: Tester avec des fichiers .eml

Utile pour déboguer l'extraction sans connexion:

```bash
./run_eml.sh
```

Cela lit tous les fichiers `.eml` dans le dossier `./CE`

## 🎯 Fonctionnalités

✅ **Extraction automatique**
- Dates d'événements (multiples formats)
- Lieux/Adresses
- Sujets des annonces

✅ **Formats supportés**
- Emails Zimbra (digests avec plusieurs événements)
- HTML et texte brut
- Encodages QUOTED-PRINTABLE
- Mailing lists

✅ **Interface**
- Design responsive et moderne
- Cartes visuelles avec gradient
- Affichage clair des infos
- Compatible mobile

## 📁 Structure du projet

```
crieurs/
├── main.py              # Script principal (IMAP)
├── main_eml.py          # Script test (fichiers .eml)
├── email_reader.py      # Classes d'extraction
├── requirements.txt     # Dépendances
├── .env                 # Config (À REMPLIR - voir .env.example)
├── .env.example         # Exemple de config
├── run.sh               # Lancement mode IMAP
├── run_eml.sh           # Lancement mode .eml
├── CE/                  # Dossier test avec exemples
│   ├── mail1.eml
│   └── mail2.eml
└── events.html          # Page générée
```

## 🔧 Personnalisation

### Modifier le nombre d'emails à lire

Dans `.env`, changez:
```env
EMAIL_LIMIT=50  # Augmentez/diminuez ce nombre
```

### Modifier le dossier source

Dans `.env`, changez:
```env
MAIL_FOLDER=CE  # Ou INBOX, [Gmail]/All Mail, etc.
```

### Améliorer la détection des dates/lieux

Éditez `email_reader.py`, classe `EventExtractor`:

```python
self.date_patterns = [
    r"votre_pattern_regex_personnalisé"
]

self.location_patterns = [
    r"votre_pattern_regex_personnalisé"  
]
```

## ⚠️ Sécurité

- **IMPORTANT**: Ne partagez/commitez JAMAIS le fichier `.env`!
- Utilisez un mot de passe d'application si possible
- Sur Gmail: utilisez un [token d'application](https://support.google.com/accounts/answer/185833)
- Le fichier `.env` est dans `.gitignore` par défaut

## 🐛 Dépannage

### "Erreur de connexion IMAP"

```bash
✗ Erreur de connexion: [AUTHENTICATIONFAILED]
```

**Solutions:**
- ✓ Vérifiez EMAIL_ADDRESS et EMAIL_PASSWORD dans `.env`
- ✓ Vérifiez IMAP_SERVER et IMAP_PORT
- ✓ Assurez-vous que IMAP est activé sur votre compte
- ✓ Pour Free: allez dans Paramètres > Sécurité > IMAP

### "Aucun email trouvé"

```bash
❌ Aucun email trouvé dans le dossier 'CE'
```

**Solutions:**
- ✓ Vérifiez que le dossier existe dans Zimbra
- ✓ Essayez avec `MAIL_FOLDER=INBOX`
- ✓ Modifiez EMAIL_LIMIT si vous n'avez peu d'emails

### "Dates/lieux mal extraits"

**Solutions:**
- ✓ Testez d'abord avec `./run_eml.sh` pour analyser le format
- ✓ Ajoutez des patterns personnalisés dans `EventExtractor`
- ✓ Vérifiez le format du contenu des emails

## 📊 Formats d'emails reconnus

### Digests Zimbra (Free)
```
* 1 - [Dossier] [Ville] - Titre événement

Quand : du samedi 13 décembre 2025 à 19:05...
Où : Ville
```

### Format standard
```
Date: 14 décembre 2025
Lieu: Montbron
Sujet: Titre
```

### Format personnalisé
Ajoutez vos patterns dans `EventExtractor`

## 💡 Astuces

1. **Tester votre extraction**: Placez des fichiers `.eml` dans `./CE` et lancez `./run_eml.sh`
2. **Déboguer les patterns**: Modifiez `email_reader.py` pour afficher les captures
3. **Automatiser**: Créez une tâche cron pour lancer `main.py` régulièrement

## 📚 Ressources

- [Documentation IMAP](https://tools.ietf.org/html/rfc3501)
- [Regex Cheat Sheet](https://www.regular-expressions.info/characters.html)
- [Free Zimbra Help](https://support.free.fr/)

## 📄 Licence

Libre d'utilisation et de modification.

---

**Besoin d'aide?** Vérifiez d'abord que `.env` est correctement configuré et testez avec `./run_eml.sh`.
