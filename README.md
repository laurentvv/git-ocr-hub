# Git OCR Hub 🔍🚀

> **Supervision multi-dépôts Git et Orchestrateur de Revues de Code automatisées par IA locale (llama.cpp & OpenCodeReview).**

`git-ocr-hub` surveille l'ensemble de vos répertoires Git (sur `C:\GIT` et `D:\GIT`), synchronise en toute sécurité les modifications distantes sans écraser votre travail, et déclenche des revues de code complètes assistées par votre modèle LLM local.

---

## ✨ Fonctionnalités Principales

1. **Découverte et Supervision Multi-Dépôts** :
   - Détection automatique de tous les dépôts Git dans `C:\GIT` et `D:\GIT` (53 dépôts analysés).
   - Contrôle d'état en temps réel : branche active, modifications locales non commitées (*dirty*), avance (*ahead*), retard (*behind*).

2. **Synchronisation Sécurisée Automatique** :
   - Exécution de `git fetch` sur tous les dépôts avec dépôts distants (*origin*).
   - `git pull --ff-only` exclusivement sur les branches propres sans modifications en cours.
   - **Protection absolue de votre travail** : les répertoires contenant des modifications non enregistrées sont automatiquement protégés et signalés.

3. **Revue Diff & Audit Complet par IA Locale (OpenCodeReview - OCR)** :
   - **Mode Diff (`review`)** : analyse du travail en cours (fichiers modifiés) ou de commits spécifiques (`--commit <hash>`).
   - **Mode Audit Complet (`scan`)** : analyse approfondie de l'intégralité d'un dépôt sans aucun diff requis, détectant les failles de sécurité, bugs de récursion, erreurs de flux I/O et problèmes de maintenabilité.
   - Intégration directe avec `llama-server` (Qwen 27B, Ornith 9B) via l'endpoint OpenAI local `http://127.0.0.1:8080/v1`.
   - Prise en charge native du **Tool Calling** (appels de fonctions `file_find`, `code_search`, `code_comment`, `task_done`) grâce au moteur Jinja.

4. **Tableau de Bord & Rapports HTML Dédiés par Dépôt** :
   - **Rapport HTML individuel par dépôt** (`reports/<nom_depot>.html`) avec badges de statut, fichiers modifiés, détails de commits et mise en forme des findings avec navigation vers le dashboard.
   - **Tableau de bord interactif** (`reports/index.html`) avec statistiques globales, filtres dynamiques (*Modifiés*, *En retard*, *Propres*), barre de recherche instantanée et bouton direct vers le rapport individuel de chaque dépôt.
   - Archivage automatique en Markdown (`reports/<repo>/<timestamp>.md`).
   - Accompagné du **WebUI Viewer officiel OCR** (`ocr viewer`) sur `http://localhost:5483`.

---

## 🛠️ Prérequis

- **OpenCodeReview CLI (OCR)** :
  ```powershell
  npm install -g @alibaba-group/open-code-review@latest
  ```
- **Python 3.10+** (aucune dépendance externe requise, utilise la bibliothèque standard).
- **Serveur LLM local** (démarré avec `start-ocr-local.ps1`).

---

## 🚀 Utilisation Rapide

### 1. Démarrer le serveur local LLM
Dans un terminal PowerShell :
```powershell
# Démarrage avec Qwen 27B (32K Contexte, VRAM 14.9 Go / 16 Go, Tool Calling activé) :
powershell -File C:\Modeles_LLM\start-ocr-local.ps1 -Model Qwen-27B

# Ou avec Ornith 9B (modèle léger) :
powershell -File C:\Modeles_LLM\start-ocr-local.ps1 -Model Ornith-9B
```

### 2. Lancer le Hub via PowerShell

Le script interactif [`run-hub.ps1`](run-hub.ps1) vous permet de tout piloter :
```powershell
# Ouvrir le menu interactif
.\run-hub.ps1

# Ou lancer directement une action :
.\run-hub.ps1 status        # Afficher l'état de tous les dépôts
.\run-hub.ps1 sync          # Synchroniser les dépôts distants propres
.\run-hub.ps1 review        # Lancer la revue OCR diff sur les dépôts modifiés
.\run-hub.ps1 scan -Repo "C:\GIT\size-directory" -OpenDashboard # Audit complet d'un dépôt
.\run-hub.ps1 all -OpenDashboard # Sync + Review + Ouverture du Dashboard
.\run-hub.ps1 dashboard     # Ouvrir le Dashboard HTML dans le navigateur
```

### 3. Utilisation en CLI Python
```powershell
# État et synchronisation
python orchestrator.py status
python orchestrator.py sync

# Revue diff
python orchestrator.py review --repo "C:\GIT\cuty-ssh" --commit "b38e60a" --open

# Audit complet (aucun diff requis)
python orchestrator.py scan --repo "C:\GIT\size-directory" --open
python orchestrator.py scan --repo "C:\GIT\mon-projet" --path "src/api" --open

# Synchronisation globale + Dashboard
python orchestrator.py all --open
```

---

## ⚙️ Configuration (`config.json`)

Le fichier `config.json` permet de personnaliser les répertoires et le comportement :
```json
{
  "monitored_paths": [
    "C:\\GIT",
    "D:\\GIT"
  ],
  "excluded_repos": [
    "git-ocr-hub"
  ],
  "llm_server": {
    "url": "http://127.0.0.1:8080/v1",
    "provider": "local_llama",
    "model": "Ornith 1.5 9B (C:)"
  },
  "review_settings": {
    "auto_pull_clean": true,
    "review_dirty_worktrees": true
  },
  "reports": {
    "output_dir": "reports"
  }
}
```

---

## 📂 Structure du Répertoire

```text
D:\GIT\git-ocr-hub\
├── .gitignore
├── config.json              # Chemins surveillés et options OCR
├── orchestrator.py          # Moteur principal en Python
├── run-hub.ps1              # Lanceur PowerShell ergonomique
├── requirements.txt
├── core/
│   ├── git_manager.py       # Découverte, status et pull FF
│   ├── ocr_runner.py        # Connecteur OpenCodeReview CLI & LLM
│   └── reporter.py          # Générateur Markdown et Dashboard HTML
└── reports/
    ├── index.html           # Tableau de bord interactif autonome
    └── <repo_name>/         # Rapports d'analyse archivés
```
