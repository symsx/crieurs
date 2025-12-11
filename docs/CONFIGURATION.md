# 🔧 Guide de Configuration Complet

## Variables d'environnement

### Authentification

#### `EMAIL_ADDRESS`
L'adresse email de votre boîte aux lettres.

**Exemple :**
```env
EMAIL_ADDRESS=mon.email@free.fr
```

**Laisser vide :** Vous sera demandé au démarrage (si `PROMPT_FOR_CREDENTIALS=false`)

---

#### `EMAIL_PASSWORD`
Mot de passe ou token d'application.

**Exemple :**
```env
EMAIL_PASSWORD=MonMotDePasse123
```

**⚠️ Important :** 
- Pour Gmail, utiliser un **mot de passe d'application** (non le mot de passe du compte)
- Pour Outlook, génère un mot de passe d'application dans les paramètres de compte
- Laisser vide demande au démarrage

**Laisser vide :** Vous sera demandé au démarrage (demande sécurisée sans affichage)

---

### Configuration IMAP

#### `IMAP_SERVER`
Serveur IMAP du fournisseur d'email.

**Valeurs usuelles :**
- `imap.free.fr` - Free (Zimbra)
- `imap.gmail.com` - Gmail
- `outlook.office365.com` - Outlook / Microsoft 365
- `imap.yahoo.com` - Yahoo Mail
- `imap.aol.com` - AOL

**Par défaut :** `imap.free.fr`

**Exemple :**
```env
IMAP_SERVER=imap.gmail.com
```

---

#### `IMAP_PORT`
Port de connexion IMAP.

**Valeurs usuelles :**
- `993` - SSL/TLS (recommandé)
- `143` - STARTTLS (moins sécurisé)

**Par défaut :** `993`

**Exemple :**
```env
IMAP_PORT=993
```

---

### Filtrage et récupération

#### `MAIL_FOLDER`
Nom du dossier email à lire.

**Valeurs courantes :**
- `INBOX` - Boîte de réception (défaut général)
- `CE` - Dossier personnalisé (Free/Zimbra)
- `[Gmail]/All Mail` - Tous les emails (Gmail)
- `[Gmail]/Important` - Emails importants (Gmail)

**Par défaut :** `CE`

**Exemple :**
```env
MAIL_FOLDER=INBOX
```

---

#### `EMAIL_LIMIT`
Nombre maximum d'emails à traiter lors de l'exécution.

**Valeurs recommandées :**
- `10` - Rapide, test
- `50` - Normal (par défaut)
- `100` - Large
- `500` - Complet

**Par défaut :** `50`

**Exemple :**
```env
EMAIL_LIMIT=100
```

---

#### `DOMAIN_FILTER`
Filtrer les emails par domaine d'expédition uniquement.

**Utilité :** Récupérer uniquement les annonces d'un domaine spécifique.

**Valeurs :**
- Vide ou non défini = accepte tous les domaines
- `gco.ouvaton.net` = accepte uniquement ce domaine

**Exemple :**
```env
DOMAIN_FILTER=gco.ouvaton.net
```

---

### Modes d'utilisation

#### `PROMPT_FOR_CREDENTIALS`
Demande interactivement les identifiants au démarrage.

**Valeurs :**
- `false` - Utilise uniquement le `.env` (par défaut)
- `true` - Toujours demander interactivement (ignore le `.env`)

**Cas d'usage :**
- `true` = Vous ne stockez pas les identifiants dans `.env` (plus sécurisé)
- `false` = Les identifiants sont dans `.env` (plus commode)

**Exemple :**
```env
PROMPT_FOR_CREDENTIALS=true
```

**Comportement :**
- Si vide et `false` → erreur
- Si vide et `true` → demande saisie
- Si rempli et `false` → utilise la valeur
- Si rempli et `true` → propose la valeur, permet modification

---

## Fichiers de configuration

### `.env` (fichier de configuration local)
Fichier contenant vos identifiants **localement** (ne pas commiter sur GitHub).

**À ne JAMAIS partager ou commiter !**

```env
EMAIL_ADDRESS=mon.email@free.fr
EMAIL_PASSWORD=MonMotDePasse123
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
MAIL_FOLDER=CE
EMAIL_LIMIT=50
DOMAIN_FILTER=gco.ouvaton.net
PROMPT_FOR_CREDENTIALS=false
```

---

### `.env.example` (modèle de configuration)
Modèle vierge partagé sur GitHub.

```env
EMAIL_ADDRESS=
EMAIL_PASSWORD=
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
MAIL_FOLDER=CE
EMAIL_LIMIT=50
DOMAIN_FILTER=gco.ouvaton.net
PROMPT_FOR_CREDENTIALS=false
```

**Action utilisateur :** Copier en `.env` et remplir ses identifiants.

---

## Fichiers de données

### `data/corrections_annonces.json`
Corrections manuelles pour les annonces mal extraites.

**Exemple :**
```json
{
  "[LES RENDEZ-VOUS DE LA BOUTIQUE": {
    "title": "Les rendez-vous de la boutique",
    "location": "Nontron",
    "date": "décembre 2025 (toute la période)"
  }
}
```

---

### `data/corrections_geolocalisation.json`
Corrections manuelles pour les lieux introuvables par géocodage.

**Exemple :**
```json
{
  "Place de l'Église Nontron": {
    "lat": 45.5233,
    "lng": 0.7667
  }
}
```

---

### `data/communes_coordinates.json`
Cache auto-généré des coordonnées géocodées (régénéré à chaque exécution).

---

## Scénarios de configuration

### Scénario 1 : Stockage sécurisé (recommandé pour production)
```env
EMAIL_ADDRESS=
EMAIL_PASSWORD=
PROMPT_FOR_CREDENTIALS=true
```

**Utilisation :** Les identifiants sont demandés à chaque exécution (saisie sécurisée).

---

### Scénario 2 : Usage local commode
```env
EMAIL_ADDRESS=mon.email@free.fr
EMAIL_PASSWORD=MonMotDePasse123
PROMPT_FOR_CREDENTIALS=false
```

**Utilisation :** Les identifiants sont lus du fichier (attention : ne pas commiter !).

---

### Scénario 3 : Multiples utilisateurs
```env
EMAIL_ADDRESS=
EMAIL_PASSWORD=
PROMPT_FOR_CREDENTIALS=true
IMAP_SERVER=imap.free.fr
MAIL_FOLDER=CE
```

**Utilisation :** Chaque utilisateur saisit ses identifiants. Configuration partagée.

---

### Scénario 4 : Filtrage par domaine
```env
EMAIL_ADDRESS=admin@free.fr
EMAIL_PASSWORD=MotDePasse
DOMAIN_FILTER=gco.ouvaton.net
EMAIL_LIMIT=100
```

**Utilisation :** Récupère les 100 derniers emails de `gco.ouvaton.net` uniquement.

---

## Dépannage

### Problème : "❌ Erreur: Email et mot de passe requis"

**Cause :** Email ou mot de passe manquant

**Solution :**
1. Vérifiez le `.env` est rempli
2. Ou définissez `PROMPT_FOR_CREDENTIALS=true` pour saisir interactivement

---

### Problème : "✗ Erreur de connexion: login failed"

**Cause :** Identifiants incorrects ou serveur incompatible

**Solution :**
1. Vérifiez email et mot de passe
2. Vérifiez `IMAP_SERVER` est correct
3. Pour Gmail : utilisez un **mot de passe d'application**

---

### Problème : "✗ Erreur lors de la recherche dans [dossier]"

**Cause :** Le dossier n'existe pas

**Solution :**
1. Vérifiez le nom exact du dossier dans votre boîte aux lettres
2. Pour Free : utiliser `CE`
3. Pour Gmail : utiliser `INBOX` ou `[Gmail]/All Mail`

---

### Problème : Peu ou pas d'emails récupérés

**Cause :** Filtre trop strict

**Solution :**
1. Augmentez `EMAIL_LIMIT`
2. Supprimez ou videz `DOMAIN_FILTER`
3. Vérifiez le `MAIL_FOLDER` ne soit pas vide

---
