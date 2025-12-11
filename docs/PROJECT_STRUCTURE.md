# 📂 Structure du projet

```
crieurs/
│
├── 📄 README.md                       Main documentation (GitHub homepage)
├── 📄 .env.example                    Configuration template
├── 📄 .gitignore                      Git ignore rules
├── 📄 LICENSE                         MIT License
├── 📄 requirements.txt                Python dependencies
├── 📄 run.sh                          Main launch script
│
├── 📂 src/                            🔧 Python source code
│   ├── main.py                        Main entry point
│   ├── email_reader.py                IMAP reader & parser
│   └── geocoding.py                   Geocoding engine
│
├── 📂 public/                         🎨 Frontend assets
│   ├── style.css                      Main stylesheet
│   ├── script.js                      Menu & interactions
│   └── script_carte.js                Map interactivity
│
├── 📂 data/                           💾 Data & configuration
│   ├── corrections_annonces.json      Manual event corrections
│   ├── corrections_geolocalisation.json Manual location corrections
│   └── communes_coordinates.json      Geocoding cache (auto-generated)
│
├── 📂 output/                         📤 Generated files (DO NOT COMMIT)
│   ├── annonces.html                  Generated events page
│   └── carte_des_annonces.html        Generated interactive map
│
├── 📂 docs/                           📖 Documentation
│   ├── README.md                      Setup & usage guide
│   ├── CONFIGURATION.md               All config parameters
│   ├── DATA_STRUCTURE.md              Data format & corrections
│   ├── CONTRIBUTING.md                Contribution guidelines
│   ├── PROJECT_STRUCTURE.md           This file
│   └── ...                            Other guides
│
├── 📂 tests/                          ✅ Unit tests (future)
│   └── test_*.py                      Test files
│
└── 📂 venv/                           🐍 Virtual environment (local only)
    └── ...                            Python packages
```

---

## 📋 File Descriptions

### Root Level

| File | Purpose |
|------|---------|
| `README.md` | Main documentation - first thing users see on GitHub |
| `.env.example` | Configuration template - copy to `.env` to customize |
| `.gitignore` | Excludes `.env`, credentials, outputs from Git |
| `LICENSE` | MIT License |
| `requirements.txt` | Python dependencies (pip install -r requirements.txt) |
| `run.sh` | Main launch script - user runs this |
| `migrate.sh` | Helper script to organize files (one-time use) |

### src/ - Python Source Code

**Location:** `/src`  
**Purpose:** All Python application code  
**What goes here:** Scripts for email reading, parsing, geocoding

| File | Purpose |
|------|---------|
| `main.py` | Application entry point & orchestration |
| `email_reader.py` | IMAP connection & email parsing |
| `geocoding.py` | Location geocoding (addresses → coordinates) |

**Import pattern in updated code:**
```python
from src.email_reader import EmailReader, HTMLGenerator
from src.geocoding import Geocoder
```

### public/ - Web Assets

**Location:** `/public`  
**Purpose:** Frontend CSS, JavaScript, static assets  
**What goes here:** Styles and interactivity that run in browser

| File | Purpose |
|------|---------|
| `style.css` | Main stylesheet for generated HTML pages |
| `script.js` | Menu burger, tooltips, general interactions |
| `script_carte.js` | Map interactions (zoom, pan, markers) |

**Usage in HTML:**
```html
<link rel="stylesheet" href="../public/style.css">
<script src="../public/script.js"></script>
<script src="../public/script_carte.js"></script>
```

### data/ - Configuration & Cache

**Location:** `/data`  
**Purpose:** Application data, corrections, and geocoding cache  
**What goes here:** JSON files for corrections and caching

| File | Purpose | Auto-generated? |
|------|---------|-----------------|
| `corrections_annonces.json` | Manual fixes for mis-parsed events | No - manual |
| `corrections_geolocalisation.json` | Manual fixes for unlocated places | No - manual |
| `communes_coordinates.json` | Geocoding cache (speeds up re-runs) | **Yes** - by app |

**Example correction:**
```json
{
  "[MALFORMED TITLE": {
    "title": "Actual Title",
    "location": "Correct Location",
    "date": "Corrected Date"
  }
}
```

### output/ - Generated Files

**Location:** `/output`  
**Purpose:** Application output (NOT committed to Git)  
**What goes here:** Generated HTML, maps, temporary files

| File | Purpose |
|------|---------|
| `annonces.html` | Generated event listing page |
| `carte_des_annonces.html` | Generated interactive map with markers |

**In `.gitignore:**
```
output/
*.html
```

### docs/ - Documentation

**Location:** `/docs`  
**Purpose:** Complete documentation for users and developers  
**What goes here:** Guides, READMEs, howtos

| File | Purpose |
|------|---------|
| `README.md` | Setup & quick start |
| `CONFIGURATION.md` | All environment variables explained |
| `DATA_STRUCTURE.md` | Event format & correction files |
| `PROJECT_STRUCTURE.md` | This file |
| `CONTRIBUTING.md` | How to contribute code |
| `GEOCODING.md` | Detailed geocoding guide |

### tests/ - Unit Tests

**Location:** `/tests`  
**Purpose:** Automated testing (future)  
**What goes here:** pytest test files

```
tests/
├── test_email_reader.py
├── test_geocoding.py
├── test_parsing.py
└── conftest.py
```

---

## 🔄 Migration Path

### From Old Structure to New

**Before (current):**
```
crieurs/
├── main.py
├── email_reader.py
├── geocoding.py
├── style.css
├── script.js
├── script_carte.js
├── corrections_*.json
├── annonces.html
└── README.md
```

**After (organized):**
```
crieurs/
├── src/
│   ├── main.py
│   ├── email_reader.py
│   └── geocoding.py
├── public/
│   ├── style.css
│   ├── script.js
│   └── script_carte.js
├── data/
│   ├── corrections_annonces.json
│   ├── corrections_geolocalisation.json
│   └── communes_coordinates.json
├── output/
│   ├── annonces.html
│   └── carte_des_annonces.html
├── docs/
│   ├── README.md
│   ├── CONFIGURATION.md
│   └── ...
└── README.md (main)
```

### Steps to Migrate

1. **Run migration script:**
   ```bash
   chmod +x migrate.sh
   ./migrate.sh
   ```

2. **Update imports in code:**
   ```python
   # Old
   from email_reader import EmailReader, HTMLGenerator
   
   # New
   from src.email_reader import EmailReader, HTMLGenerator
   from src.geocoding import Geocoder
   ```

3. **Update run.sh:**
   ```bash
   python src/main.py
   ```

4. **Test everything:**
   ```bash
   ./run.sh
   ```

5. **Verify output:**
   - Check `output/annonces.html`
   - Check `output/carte_des_annonces.html`

6. **Delete old files:**
   ```bash
   rm main.py email_reader.py geocoding.py
   rm style.css script.js script_carte.js
   ```

7. **Commit to git:**
   ```bash
   git add .
   git commit -m "refactor: organize project structure for GitHub"
   ```

---

## 📌 Key Principles

### 1. Separation of Concerns
- **src/** = Logic only
- **public/** = UI/Frontend only
- **data/** = Configuration/Cache
- **output/** = Temporary generated files
- **docs/** = Documentation

### 2. Git Principles
- ✅ Commit: Source code, documentation, configuration templates
- ❌ Don't commit: `.env`, `output/`, `venv/`, `*.pyc`, cache files

### 3. Organization
- One purpose per directory
- Clear naming conventions
- Consistent structure

### 4. Scalability
- Easy to add new modules in `src/`
- Easy to add new assets in `public/`
- Easy to add new docs in `docs/`

---

## 🚀 Development Workflow

### Adding a New Feature

1. **Create file in appropriate directory:**
   - Logic → `src/new_module.py`
   - Styling → `public/new_feature.css`
   - Docs → `docs/NEW_FEATURE.md`

2. **Update imports in main.py:**
   ```python
   from src.new_module import NewClass
   ```

3. **Test locally:**
   ```bash
   ./run.sh
   ```

4. **Commit with clear message:**
   ```bash
   git commit -m "feat: add new_module for geocoding improvements"
   ```

---

## 📚 Documentation Structure

```
docs/
├── README.md              ← Getting started
├── CONFIGURATION.md       ← All settings explained
├── DATA_STRUCTURE.md      ← Data formats & corrections
├── PROJECT_STRUCTURE.md   ← This file (developer guide)
├── CONTRIBUTING.md        ← How to contribute code
├── GEOCODING.md           ← Detailed geocoding guide
└── TROUBLESHOOTING.md     ← Common issues & solutions
```

Each doc is independent and linked to others via references.

---

## 🔗 File Dependencies

```
main.py (entry point)
├── src/email_reader.py
│   └── public/style.css (generates HTML with refs)
├── src/geocoding.py
│   └── data/corrections_*.json
└── output/ (generates files here)
    ├── annonces.html (uses public/*.css/js)
    └── carte_des_annonces.html (uses public/*.js)
```

---

## ✅ Pre-GitHub Checklist

- [ ] All Python code in `src/`
- [ ] All CSS/JS in `public/`
- [ ] `.env` removed from Git (in `.gitignore`)
- [ ] `.env.example` in root
- [ ] `output/` in `.gitignore`
- [ ] Documentation complete in `docs/`
- [ ] `requirements.txt` up to date
- [ ] `run.sh` points to correct paths
- [ ] `LICENSE` file present
- [ ] `.gitignore` correct
- [ ] README.md comprehensive

---
