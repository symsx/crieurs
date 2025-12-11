# 📤 Guide FTP Upload

## Configuration de l'upload FTP

### 1. Activer l'upload FTP

Éditez le fichier `.env` et modifiez les paramètres :

```env
# Activer l'upload FTP (true pour activer, false pour désactiver)
ENABLE_FTP_UPLOAD=true

# Serveur FTP
FTP_HOST=ftp.monsite.com

# Port FTP (21 par défaut)
FTP_PORT=21

# Identifiants FTP
FTP_USER=monusername
FTP_PASSWORD=monmotdepasse

# Chemin distant où uploader les fichiers (ex: /public_html/crieurs/)
FTP_REMOTE_PATH=/public_html/crieurs/

# Utiliser FTPS (FTP sécurisé) au lieu de FTP standard (true/false)
FTP_USE_TLS=false
```

### 2. Paramètres FTP Détaillés

| Paramètre | Description | Exemple |
|-----------|-------------|---------|
| `ENABLE_FTP_UPLOAD` | Activer/désactiver l'upload | `true` ou `false` |
| `FTP_HOST` | Serveur FTP | `ftp.example.com` |
| `FTP_PORT` | Port FTP | `21` (FTP) ou `990` (FTPS) |
| `FTP_USER` | Nom d'utilisateur | `username` |
| `FTP_PASSWORD` | Mot de passe | `password123` |
| `FTP_REMOTE_PATH` | Chemin destination | `/public_html/crieurs/` |
| `FTP_USE_TLS` | Mode FTPS sécurisé | `true` ou `false` |

### 3. FTP vs FTPS

**FTP Standard (Non sécurisé)**
```env
FTP_PORT=21
FTP_USE_TLS=false
```

**FTPS (FTP sécurisé - Recommandé)**
```env
FTP_PORT=990
FTP_USE_TLS=true
```

### 4. Trouver les paramètres FTP

Consultez votre hébergeur pour obtenir :
- ✓ Serveur FTP (ex: ftp.monsite.com)
- ✓ Port (généralement 21 ou 990)
- ✓ Identifiants (email de compte ou username)
- ✓ Chemin public_html ou répertoire web

### 5. Fonctionnement

Quand `ENABLE_FTP_UPLOAD=true` :

```bash
./run.sh
```

Le script va :
1. ✓ Extraire les emails
2. ✓ Générer `annonces.html`
3. ✓ Générer `carte_des_annonces.html`
4. **📤 Uploader les fichiers par FTP**

Résultat :
```
📤 Upload FTP vers le serveur...
  ✓ Connecté à ftp.monsite.com
  📁 Uploading vers /public_html/crieurs/...
  ✓ annonces.html uploadé
  ✓ carte_des_annonces.html uploadé
  ✓ 2 fichier(s) uploadé(s)

✅ Succès!
   • Upload FTP: ✓
```

### 6. Sécurité

**⚠️ Important:**
- Ne commitez **JAMAIS** le fichier `.env` contenant vos identifiants FTP
- Le `.env` est dans `.gitignore` (protection automatique)
- Gardez vos identifiants FTP confidentiels

### 7. Dépannage

**Erreur: "Paramètres FTP incomplets"**
→ Vérifiez que FTP_HOST, FTP_USER et FTP_PASSWORD sont remplis

**Erreur: "Erreur de connexion FTP"**
→ Vérifiez :
  - Serveur FTP correct
  - Port FTP correct (21 ou 990)
  - Identifiants corrects
  - Pare-feu peut bloquer FTP

**Erreur: "Répertoire non créé"**
→ Le script crée automatiquement le répertoire s'il n'existe pas

**Upload réussit mais fichiers ne s'affichent pas**
→ Vérifiez les permissions du répertoire distant (755 ou 775)

### 8. Exemple de configuration complète

```env
# Email
EMAIL_ADDRESS=votre.email@free.fr
EMAIL_PASSWORD=votremotdepasse
MAIL_FOLDER=CE

# FTP
ENABLE_FTP_UPLOAD=true
FTP_HOST=ftp.votre-site.fr
FTP_PORT=21
FTP_USER=utilisateur
FTP_PASSWORD=votremdp
FTP_REMOTE_PATH=/www/crieurs/
FTP_USE_TLS=false
```

### 9. Désactiver l'upload temporairement

Pour désactiver l'upload sans perdre la configuration :

```env
ENABLE_FTP_UPLOAD=false
```

Les fichiers HTML seront toujours générés dans `output/`, juste pas uploadés.

---

**Questions ?** Consultez la documentation du projet ou votre hébergeur pour les paramètres FTP.
