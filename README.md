# Git OCR Hub 🔍🚀

> **Supervision multi-dépôts Git et Orchestrateur de Revues de Code automatisées par IA locale (llama.cpp & OpenCodeReview).**

`git-ocr-hub` surveille l'ensemble de vos répertoires Git (sur `C:\GIT` et `D:\GIT`), synchronise en toute sécurité les modifications distantes sans écraser votre travail, et déclenche des revues de code complètes assistées par votre modèle LLM local.

---

## ✨ Fonctionnalités Principales

1. **Découverte et Supervision Multi-Dépôts** :
   - Détection automatique de tous les dépôts Git dans `C:\GIT` et `D:\GIT`.
   - Contrôle d'état en temps réel : branche active, modifications locales non commitées (*dirty*), avance (*ahead*), retard (*behind*).

2. **Synchronisation Sécurisée Automatique** :
   - Exécution de `git fetch` sur tous les dépôts avec dépôts distants (*origin*).
   - `git pull --ff-only` exclusivement sur les branches propres sans modifications en cours.
   - **Protection absolue de votre travail** : les répertoires contenant des modifications non enregistrées sont automatiquement protégés et signalés.

3. **Revue de Code IA Locale (OpenCodeReview - OCR)** :
   - Déclenchement automatique de l'analyse sur les nouveaux commits ou sur les modifications locales.
   - Intégration directe avec `llama-server` (modèles `Ornith-1.5-9B`, `Qwen-27B`, etc.) via l'endpoint OpenAI local `http://127.0.0.1:8080/v1`.
   - Prise en charge du **Tool Calling** (appels de fonctions `code_comment`, `task_done`) grâce au moteur Jinja.

4. **Tableau de Bord & Rapports Complets** :
   - Génération automatique de rapports détaillés en Markdown (`reports/<repo>/<timestamp>.md`).
   - Tableau de bord web interactif (`reports/index.html`) avec statistiques globales, filtres rapides (*Modifiés*, *En retard*, *Propres*) et recherche instantanée.

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
powershell -File C:\Modeles_LLM\start-ocr-local.ps1 -Model Ornith-9B
# ou avec Qwen 27B :
powershell -File C:\Modeles_LLM\start-ocr-local.ps1 -Model Qwen-27B
```

### 2. Lancer le Hub via PowerShell

Le script interactif [`run-hub.ps1`](run-hub.ps1) vous permet de tout piloter :
```powershell
# Ouvrir le menu interactif
.\run-hub.ps1

# Ou lancer directement une action :
.\run-hub.ps1 status        # Afficher l'état de tous les dépôts
.\run-hub.ps1 sync          # Synchroniser les dépôts distants propres
.\run-hub.ps1 review        # Lancer la revue OCR sur les dépôts modifiés
.\run-hub.ps1 all -OpenDashboard # Sync + Review + Ouverture du Dashboard
.\run-hub.ps1 dashboard     # Ouvrir le Dashboard HTML dans le navigateur
```

### 3. Utilisation en CLI Python
```powershell
python orchestrator.py status
python orchestrator.py sync
python orchestrator.py review --repo "C:\GIT\mon-projet"
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
