# 📧 Outils d'Extraction d'Adresses Email

Ce document décrit les deux nouveaux outils ajoutés au projet Crieurs pour extraire et analyser les adresses email de votre boîte mail.

## 🎯 Overview

- **`extract_mail.py`** - Extrait automatiquement toutes les adresses email uniques et les sauvegarde dans un CSV
- **`analyze_emails.py`** - Analyse le fichier CSV pour générer des statistiques et exporter par domaine

## 🔧 extract_mail.py

### Objectif

Scrute **TOUS les répertoires** de votre boîte mail via IMAP, extrait les adresses email des champs From/To/Cc/Bcc de chaque message, et les stocke dans un fichier CSV avec déduplication automatique.

### Utilisation

```bash
# Via le script shell
./extract_mail.sh

# Ou directement en Python
python3 src/extract_mail.py
```

### Configuration (.env)

```env
EMAIL_ADDRESS=votre.email@free.fr
EMAIL_PASSWORD=votre_mot_de_passe
IMAP_SERVER=imap.free.fr
IMAP_PORT=993
PROMPT_FOR_CREDENTIALS=false
```

### Fonctionnalités

✅ Connexion sécurisée via IMAP SSL  
✅ Scrute tous les dossiers (INBOX, Archives, etc.)  
✅ Extrait les adresses de 6 champs d'en-tête (From, To, Cc, Bcc, Reply-To, Sender)  
✅ Déduplique automatiquement  
✅ Ajoute uniquement les nouvelles adresses au fichier CSV existant  
✅ Trie les adresses par ordre alphabétique  
✅ Affiche un résumé détaillé  

### Exemple de sortie

```
🔍 EXTRACTEUR D'ADRESSES EMAIL
==================================================
✓ Connecté à scregut@free.fr

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
Adresses email uniques trouvées: 3247
==================================================

📁 Sauvegarde des adresses...
✓ 3247 adresse(s) email(s) sauvegardée(s)
  → 45 nouvelle(s) adresse(s) ajoutée(s)

✓ Fichier créé: data/adresses_emails.csv
✓ Connexion fermée
```

### Fichier de sortie

**`data/adresses_emails.csv`**

```csv
Adresse Email
exemple1@domaine.com
exemple2@domaine.com
exemple3@domaine.com
...
```

**Caractéristiques:**
- Une adresse par ligne
- Format standard CSV avec en-tête
- Adresses triées alphabétiquement
- Sans doublons
- En minuscules

---

## 📊 analyze_emails.py

### Objectif

Analyse le fichier CSV généré par `extract_mail.py` pour fournir des statistiques et exporter les adresses par domaine.

### Utilisation

```bash
python3 src/analyze_emails.py
```

### Fonctionnalités

✅ Charge le CSV généré  
✅ Compte les adresses par domaine  
✅ Affiche les 10 domaines les plus fréquents  
✅ Filtre les adresses noreply  
✅ Exporte les adresses groupées par domaine  

### Exemple de sortie

```
📧 Analyseur d'adresses email
==================================================

📂 Chargement de data/adresses_emails.csv...

📊 Statistiques:
--------------------------------------------------
Total d'adresses: 3247
Adresses uniques: 3247
Nombre de domaines: 1223
Adresses noreply: 325

🏆 Top 10 domaines:
--------------------------------------------------
 1. gmail.com                                ( 607)
 2. hotmail.fr                               ( 111)
 3. orange.fr                                (  95)
 4. yahoo.fr                                 (  78)
 5. free.fr                                  (  68)
 6. hotmail.com                              (  54)
 7. laposte.net                              (  47)
 8. wanadoo.fr                               (  42)
 9. amazon.fr                                (  28)
10. marketplace.amazon.fr                    (  27)

🔍 Exemples de filtrage:
--------------------------------------------------
Adresses Gmail: 607
Adresses valides (sans noreply): 2922

💾 Export par domaine:
--------------------------------------------------
✓ 607 adresse(s) exportée(s) vers data/emails_by_domain/gmail.com.txt
✓ 111 adresse(s) exportée(s) vers data/emails_by_domain/hotmail.fr.txt
...
✓ Analyse terminée!
```

### Dossier de sortie

**`data/emails_by_domain/`**

Crée un fichier texte par domaine:

```
emails_by_domain/
├── gmail.com.txt
├── hotmail.fr.txt
├── orange.fr.txt
├── yahoo.fr.txt
├── free.fr.txt
...
```

Chaque fichier contient les adresses du domaine (une par ligne), triées alphabétiquement.

---

## 🔄 Workflow complet

### Étape 1: Extraction
```bash
./extract_mail.sh
```
→ Crée `data/adresses_emails.csv`

### Étape 2: Analyse
```bash
python3 src/analyze_emails.py
```
→ Crée `data/emails_by_domain/` avec fichiers par domaine

### Étape 3: Utilisation des données

Vous pouvez maintenant:
- 📊 Analyser les domaines les plus courants
- 🔤 Créer des listes de diffusion
- 🔍 Identifier les patterns de communication
- 💾 Fusionner avec d'autres sources de contacts
- 🎯 Segmenter les adresses par domaine professionnel/personnel

---

## 🔒 Sécurité

✅ Les identifiants restent dans `.env` (jamais dans le code)  
✅ Connexion SSL/TLS (port 993)  
✅ Aucun stockage du mot de passe en mémoire après connexion  
✅ Pas de transmission à des tiers  
✅ CSV stocké localement uniquement  

---

## 📁 Structure des fichiers

```
crieurs/
├── src/
│   ├── extract_mail.py          ← Outil principal d'extraction
│   ├── analyze_emails.py        ← Outil d'analyse
│   ├── email_reader.py          (réutilisé)
│   └── ...
├── data/
│   ├── adresses_emails.csv      ← Sortie principale
│   └── emails_by_domain/        ← Emails groupés par domaine
├── extract_mail.sh              ← Script de lancement
├── .env                         ← Configuration (à compléter)
├── docs/
│   └── EXTRACT_MAIL.md          ← Documentation détaillée
└── ...
```

---

## 💡 Cas d'usage

### 1. Créer une liste de diffusion
```bash
# Extraire les adresses Gmail
grep -h "@gmail.com$" data/emails_by_domain/gmail.com.txt > newsletter_gmail.txt
```

### 2. Identifier les contacts professionnels
```bash
# Voir les adresses d'entreprises
ls -la data/emails_by_domain/ | grep -E "\.com|\.fr" | head -20
```

### 3. Analyser la distribution des fournisseurs
```bash
# Voir quel fournisseur d'email est dominant
wc -l data/emails_by_domain/*.txt | tail -1
```

### 4. Fusionner avec CRM
```bash
# Importer dans un système de gestion de contacts
cat data/adresses_emails.csv | head -100
```

---

## 🛠️ Dépendances

- Python 3.6+
- `python-dotenv` - Gestion des variables d'environnement
- Modules standards: `imaplib`, `email`, `csv`, `re`, `os`, `pathlib`

Toutes les dépendances sont dans `requirements.txt`

---

## ❓ FAQ

**Q: Combien de temps prend l'extraction?**  
R: De 2 à 10 minutes selon le nombre d'emails (15 000 emails = ~5 min)

**Q: Comment réexécuter sans dupliquer?**  
R: Le script détecte les adresses existantes et n'ajoute que les nouvelles

**Q: Puis-je limiter à un seul dossier?**  
R: Oui, en modifiant `extract_all_emails()` ou créez une variante du script

**Q: Est-ce que cela supprime les doublons?**  
R: Oui, dédupliquées automatiquement (minuscules)

**Q: Puis-je exporter en JSON?**  
R: Oui, il suffit de modifier `save_to_csv()` pour JSON

---

## 📝 Historique

- **v1.0** (2026-01-05) - Création initiale avec extraction et analyse
  - Extraction depuis tous les dossiers IMAP
  - Déduplication automatique
  - Analyse statistique
  - Export par domaine

---

## 📞 Support

Pour des questions ou améliorations, consultez la documentation complète dans [docs/EXTRACT_MAIL.md](../docs/EXTRACT_MAIL.md)
