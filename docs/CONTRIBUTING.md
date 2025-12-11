# 🤝 Guide de Contribution

Merci de vouloir contribuer à Crieurs ! Ce guide explique comment contribuer.

## Code de conduite

- Soyez respectueux
- Acceptez les critiques constructives
- Concentrez-vous sur ce qui est meilleur pour la communauté

## Comment contribuer

### Signaler un bug

1. **Avant de signaler**, vérifiez que le bug n'existe pas déjà
2. Utilisez le template d'issue GitHub
3. Décrivez :
   - Ce que vous avez essayé
   - Ce que vous attendiez
   - Ce qui s'est réellement passé
   - Votre configuration (`.env`, version Python, OS)

**Exemple :**
```
Titre : La carte n'affiche pas les événements

Configuration :
- OS : Linux Ubuntu 22.04
- Python : 3.10
- EMAIL_LIMIT : 50

Comportement attendu :
La carte devrait afficher 50 marqueurs

Comportement observé :
La carte est vide

Pas d'erreur dans la console
```

### Suggérer une amélioration

1. Ouvrez une issue avec le label `enhancement`
2. Décrivez :
   - Le problème actuel
   - Votre solution proposée
   - Des cas d'usage potentiels

### Soumettre du code

#### Préparation

1. **Forkez** le dépôt
   ```bash
   git clone https://github.com/votre-username/crieurs.git
   cd crieurs
   ```

2. **Créez une branche** de fonctionnalité
   ```bash
   git checkout -b feature/ma-nouvelle-fonction
   ```

3. **Installez les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

#### Développement

1. **Écrivez votre code** en respectant :
   - Les conventions PEP 8
   - Les noms de variables explicites
   - Les docstrings pour les fonctions

2. **Testez votre code**
   ```bash
   python main.py
   ```

3. **Commitez vos changements** avec messages clairs
   ```bash
   git commit -m "Add: support for Outlook IMAP configuration"
   git commit -m "Fix: geocoding cache not persisting"
   ```

4. **Pushez vers votre fork**
   ```bash
   git push origin feature/ma-nouvelle-fonction
   ```

#### Pull Request

1. **Ouvrez une PR** depuis GitHub
2. **Décrivez vos changements** :
   - Quel problème résolvez-vous ?
   - Quels tests avez-vous effectués ?
   - Y a-t-il des changements importants ?

3. **Attendez la review** et répondez aux commentaires

**Exemple de PR :**
```markdown
# Description

Ajoute le support de la configuration pour Outlook 365.

## Type de changement

- [x] Correction de bug
- [x] Nouvelle fonctionnalité
- [ ] Changement cassant

## Comment tester

1. Configurez `.env` avec Outlook
2. Lancez `./run.sh`
3. Vérifiez que les emails sont bien récupérés

## Checklist

- [x] Mon code suit les conventions PEP 8
- [x] J'ai testé manuellement
- [x] J'ai mis à jour la documentation
- [x] Je n'ai pas introduit de dépendances non nécessaires
```

---

## Standards de code

### Python

```python
# ✅ Bon
def extract_phone_number(text: str) -> str:
    """Extrait un numéro de téléphone du texte."""
    pattern = r'0[1-9](?:[\s\.\-]?\d{2}){4}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""

# ❌ Mauvais
def ExtractPhoneNumber(txt):
    # extrait le phone
    p = r'0[1-9](?:[\s\.\-]?\d{2}){4}'
    m = re.findall(p, txt)
    return m[0] if m else ""
```

### JavaScript / CSS

```javascript
// ✅ Bon
function displayEventMarker(event, map) {
    const marker = L.marker([event.lat, event.lng]);
    marker.addTo(map);
    return marker;
}

// ❌ Mauvais
function displayEventMarker(e, m) {
    const marker = L.marker([e.lat, e.lng]);
    marker.addTo(m);
    return marker;
}
```

### Docstrings

```python
def geocode_location(address: str, cache: dict = None) -> Tuple[float, float]:
    """
    Géocode une adresse en coordonnées GPS.
    
    Args:
        address: Adresse à géocoder (ex: "Nontron")
        cache: Cache des coordonnées déjà trouvées
        
    Returns:
        Tuple (latitude, longitude) ou (None, None) si introuvable
        
    Raises:
        ValueError: Si l'adresse est vide
    """
```

---

## Structure des commits

```
Type: Description courte (max 50 caractères)

Description longue optionnelle (max 72 caractères par ligne)
Explique pourquoi et comment, pas le quoi.

Fixes #123
Resolves #456
```

**Types :**
- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation
- `style:` Formatage, pas de changement fonctionnel
- `refactor:` Restructuration sans changement fonctionnel
- `perf:` Optimisation de performance
- `test:` Ajout de tests

**Exemples :**
```bash
git commit -m "feat: add Outlook IMAP support"
git commit -m "fix: geocoding timeout on large dataset"
git commit -m "docs: improve CONFIGURATION.md examples"
```

---

## Processus de review

1. **Vérification automatique** (CI/CD)
   - Lint Python (PEP 8)
   - Tests unitaires

2. **Review manuel**
   - Vérification du code
   - Vérification de la documentation
   - Vérification des cas d'usage

3. **Approbation et merge**
   - Minimum 1 approbation requise
   - Les tests doivent passer

---

## Développement local

### Environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Lancer les tests

```bash
python -m pytest tests/ -v
```

### Build et test local

```bash
./run.sh
# Vérifiez output/annonces.html
# Vérifiez output/carte_des_annonces.html
```

---

## Documentation

### Mettre à jour la documentation

- Modifications au code = mise à jour de la doc correspondante
- READMEs dans `docs/`
- Commentaires inline pour du code complexe
- Docstrings pour chaque fonction publique

### Exemple de doc complète

```python
def apply_correction(event: dict, corrections: dict) -> dict:
    """
    Applique les corrections manuelles à un événement.
    
    Les corrections permettent de corriger les événements mal extraits
    (champs mal parsés, dates invalides, lieux non trouvés).
    
    Example:
        >>> event = {'title': '[MALFORMED', 'location': 'Nontron'}
        >>> corrections = {'[MALFORMED': {'title': 'Atelier'}}
        >>> apply_correction(event, corrections)
        {'title': 'Atelier', 'location': 'Nontron'}
    
    Args:
        event: Événement extrait
        corrections: Dict des corrections (clé = titre malformé)
        
    Returns:
        Événement avec corrections appliquées
    """
```

---

## Besoin d'aide ?

- 💬 **Discussions** : Questions générales
- 🐛 **Issues** : Rapports de bugs
- 📧 **Email** : Pour les sujets sensibles

Merci de contribuer ! 🎉
