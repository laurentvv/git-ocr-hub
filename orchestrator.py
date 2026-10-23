#!/usr/bin/env python3
"""
git-ocr-hub - Orchestrateur de supervision Git et de Code Review IA locale.
"""

import argparse
import json
import os
import sys
import webbrowser
from typing import Dict, Any, List

from core.git_manager import GitManager
from core.ocr_runner import OcrRunner
from core.reporter import Reporter

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config() -> Dict[str, Any]:
    default_config = {
        "monitored_paths": ["C:\\GIT", "D:\\GIT"],
        "excluded_repos": ["git-ocr-hub"],
        "llm_server": {
            "url": "http://127.0.0.1:8080/v1",
            "provider": "local_llama",
            "model": "Ornith 1.5 9B (C:)"
        },
        "review_settings": {
            "auto_pull_clean": True,
            "review_dirty_worktrees": True
        },
        "reports": {
            "output_dir": "reports"
        }
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return {**default_config, **json.load(f)}
        except Exception:
            pass
    return default_config

def cmd_status(args, cfg):
    git_mgr = GitManager(cfg["monitored_paths"], cfg["excluded_repos"])
    repos = git_mgr.find_repositories()
    print(f"\n🔍 Découverte de {len(repos)} dépôts Git surveillés...\n")

    header = f"{'Dépôt':<30} {'Branche':<25} {'Statut':<18} {'Sync':<15}"
    print(header)
    print("-" * len(header))

    for path in repos:
        st = git_mgr.get_repo_status(path)
        dirty_str = f"⚠️ Dirty ({st['dirty_count']})" if st['is_dirty'] else "✅ Clean"
        
        sync_str = "Local"
        if st['has_remote']:
            if st['behind'] > 0:
                sync_str = f"Retard (-{st['behind']})"
            elif st['ahead'] > 0:
                sync_str = f"Avance (+{st['ahead']})"
            else:
                sync_str = "À jour"

        print(f"{st['name']:<30} {st['branch']:<25} {dirty_str:<18} {sync_str:<15}")

def cmd_sync(args, cfg):
    git_mgr = GitManager(cfg["monitored_paths"], cfg["excluded_repos"])
    repos = git_mgr.find_repositories()
    print(f"\n🔄 Synchronisation de {len(repos)} dépôts...\n")

    updated = []
    skipped_dirty = []
    up_to_date = []

    for path in repos:
        name = os.path.basename(path)
        print(f"-> Fetch {name}...", end=" ", flush=True)
        git_mgr.fetch_all(path)

        st = git_mgr.get_repo_status(path)
        if st['is_dirty']:
            print(f"⚠️ Ignoré (modifications locales : {st['dirty_count']} fichiers)")
            skipped_dirty.append(name)
        elif st['behind'] > 0:
            res = git_mgr.pull_fast_forward(path)
            if res['success']:
                print(f"✅ Mis à jour (+{st['behind']} commits)")
                updated.append(name)
            else:
                print(f"❌ Échec Fast-Forward ({res['output']})")
        else:
            print("✅ À jour")
            up_to_date.append(name)

    print("\n--- Bilan de la synchronisation ---")
    print(f"✅ Mis à jour : {len(updated)}")
    print(f"🛡️ Protégés (modifiés localement) : {len(skipped_dirty)}")
    print(f"ℹ️ Déjà à jour : {len(up_to_date)}")

def cmd_review(args, cfg):
    git_mgr = GitManager(cfg["monitored_paths"], cfg["excluded_repos"])
    ocr = OcrRunner(
        server_url=cfg["llm_server"]["url"],
        provider=cfg["llm_server"]["provider"],
        model=cfg["llm_server"]["model"]
    )
    reporter = Reporter(cfg["reports"]["output_dir"])

    # Vérification du serveur local
    print("🔌 Test de connexion au serveur LLM local (llama-server)...", end=" ")
    if not ocr.is_server_alive():
        print("\n❌ Le serveur local llama-server ne répond pas sur", cfg["llm_server"]["url"])
        print("💡 Astuce : Démarrez-le avec : powershell -File C:\\Modeles_LLM\\start-ocr-local.ps1 -Model Ornith-9B")
        return
    print("✅ En ligne")

    target_repo = args.repo
    repos = [target_repo] if target_repo else git_mgr.find_repositories()

    reviewed_any = False
    for path in repos:
        st = git_mgr.get_repo_status(path)
        name = st['name']

        should_review = False
        if target_repo:
            should_review = True
        elif st['is_dirty']:
            should_review = True

        if not should_review:
            continue

        print(f"\n🔍 Analyse OCR sur {name} ({st['dirty_count']} fichiers modifiés)...")
        if args.preview:
            prev = ocr.preview_review(path)
            print(prev.get("output", "Aucune prévisualisation disponible."))
            continue

        rev_res = ocr.run_review(path, timeout=args.timeout)
        reviewed_any = True
        md_path = reporter.save_markdown_report(name, st, rev_res)
        print(f"📄 Rapport sauvegardé : {md_path}")
        if rev_res.get("raw"):
            print("--- Résumé OCR ---")
            print(rev_res["raw"][:500] + ("..." if len(rev_res["raw"]) > 500 else ""))

    if not reviewed_any and not args.preview:
        print("\n✨ Aucun dépôt ne nécessite de revue actuellement (aucun fichier modifié).")

def cmd_all(args, cfg):
    git_mgr = GitManager(cfg["monitored_paths"], cfg["excluded_repos"])
    ocr = OcrRunner(
        server_url=cfg["llm_server"]["url"],
        provider=cfg["llm_server"]["provider"],
        model=cfg["llm_server"]["model"]
    )
    reporter = Reporter(cfg["reports"]["output_dir"])

    print("\n🚀 Exécution complète : Synchronisation + Vérification OCR + Dashboard")
    repos = git_mgr.find_repositories()

    summary_list = []
    for path in repos:
        name = os.path.basename(path)
        print(f"-> Traitement {name}...", end=" ", flush=True)
        git_mgr.fetch_all(path)
        st = git_mgr.get_repo_status(path)

        # Pull si propre et en retard
        if not st['is_dirty'] and st['behind'] > 0:
            git_mgr.pull_fast_forward(path)
            st = git_mgr.get_repo_status(path)

        st['reviewed'] = False
        st['review_snippet'] = ""

        # Revue si dirty et LLM actif
        if st['is_dirty'] and ocr.is_server_alive() and not args.no_review:
            print("🔬 [OCR Review]...", end=" ", flush=True)
            rev = ocr.run_review(path, timeout=args.timeout)
            reporter.save_markdown_report(name, st, rev)
            st['reviewed'] = True
            st['review_snippet'] = rev.get("raw", "")[:300]

        summary_list.append(st)
        print("Fait.")

    index_html = reporter.generate_html_dashboard(summary_list)
    print(f"\n📊 Dashboard généré avec succès : {index_html}")
    if args.open:
        webbrowser.open(f"file://{os.path.abspath(index_html)}")

def cmd_dashboard(args, cfg):
    output_dir = cfg["reports"]["output_dir"]
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir, "index.html")
    if not os.path.exists(index_path):
        print("⚠️ Dashboard introuvable. Génération en cours...")
        cmd_all(argparse.Namespace(no_review=True, timeout=60, open=True), cfg)
    else:
        print(f"🌐 Ouverture du dashboard : {index_path}")
        webbrowser.open(f"file://{os.path.abspath(index_path)}")

def main():
    parser = argparse.ArgumentParser(description="Git OCR Hub - Gestionnaire de synchronisation et de Code Review IA locale")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = subparsers.add_parser("status", help="Afficher l'état de tous les dépôts")
    
    # sync
    p_sync = subparsers.add_parser("sync", help="Synchroniser (git fetch + pull FF) en mode sécurisé")
    
    # review
    p_rev = subparsers.add_parser("review", help="Lancer la revue OCR sur un dépôt ou tous les dépôts modifiés")
    p_rev.add_argument("--repo", help="Chemin vers un dépôt spécifique")
    p_rev.add_argument("--preview", action="store_true", help="Afficher uniquement les fichiers qui seraient analysés")
    p_rev.add_argument("--timeout", type=int, default=300, help="Délai maximum d'analyse par dépôt (secondes)")

    # all
    p_all = subparsers.add_parser("all", help="Synchroniser, analyser et générer le tableau de bord HTML")
    p_all.add_argument("--no-review", action="store_true", help="Ignorer l'analyse IA OCR (synchronisation et dashboard uniquement)")
    p_all.add_argument("--timeout", type=int, default=300, help="Délai maximum par revue")
    p_all.add_argument("--open", action="store_true", help="Ouvrir automatiquement le navigateur après génération")

    # dashboard
    p_dash = subparsers.add_parser("dashboard", help="Ouvrir le tableau de bord HTML dans le navigateur")

    args = parser.parse_args()
    cfg = load_config()

    commands = {
        "status": cmd_status,
        "sync": cmd_sync,
        "review": cmd_review,
        "all": cmd_all,
        "dashboard": cmd_dashboard,
    }

    cmd_fn = commands.get(args.command)
    if cmd_fn:
        cmd_fn(args, cfg)

if __name__ == "__main__":
    main()
