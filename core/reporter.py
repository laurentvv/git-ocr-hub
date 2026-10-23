import os
import json
import datetime
from typing import Dict, List, Any

class Reporter:
    """Generates Markdown reports and interactive HTML Dashboard."""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_markdown_report(self, repo_name: str, status_data: Dict[str, Any], review_data: Optional[Dict[str, Any]] = None) -> str:
        """Create and save a detailed Markdown report for a specific repository."""
        repo_dir = os.path.join(self.output_dir, repo_name)
        os.makedirs(repo_dir, exist_ok=True)

        now = datetime.datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp_str}.md"
        filepath = os.path.join(repo_dir, filename)

        md_lines = [
            f"# Rapport Code Review : {repo_name}",
            f"- **Date** : {now.strftime('%d/%m/%Y %H:%M:%S')}",
            f"- **Branche** : `{status_data.get('branch', 'unknown')}`",
            f"- **Statut** : {'⚠️ Modifié localement (Dirty)' if status_data.get('is_dirty') else '✅ Propre (Clean)'}",
            f"- **Synchronisation** : {status_data.get('behind', 0)} commit(s) de retard | {status_data.get('ahead', 0)} commit(s) d'avance",
            "",
            "## 1. État Git du Dépôt",
        ]

        if status_data.get("is_dirty"):
            md_lines.append(f"### Fichiers modifiés ({status_data.get('dirty_count', 0)}) :")
            for f in status_data.get("dirty_files", []):
                md_lines.append(f"- `{f}`")
        else:
            md_lines.append("Aucun fichier modifié non commité.")

        last_c = status_data.get("last_commit", {})
        if last_c:
            md_lines.extend([
                "",
                "### Dernier commit :",
                f"- **Hash** : `{last_c.get('hash', '')[:8]}`",
                f"- **Auteur** : {last_c.get('author', '')}",
                f"- **Date** : {last_c.get('date', '')}",
                f"- **Message** : {last_c.get('subject', '')}",
            ])

        md_lines.extend(["", "## 2. Analyse OpenCodeReview (OCR)"])
        if review_data:
            if review_data.get("success"):
                md_lines.append("✅ **Revue effectuée avec succès.**")
            else:
                md_lines.append("⚠️ **Revue partielle ou message :**")

            raw = review_data.get("raw", "")
            if raw:
                md_lines.extend(["", "```text", raw, "```"])
            
            stderr = review_data.get("stderr", "")
            if stderr:
                md_lines.extend(["", "### Détails d'exécution :", "```text", stderr, "```"])
        else:
            md_lines.append("_Aucune revue lancée pour ce passage (dépôt déjà à jour et sans modification)._")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return filepath

    def generate_html_dashboard(self, repos_summary: List[Dict[str, Any]]) -> str:
        """Generate a complete standalone HTML dashboard for all monitored repositories."""
        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        total = len(repos_summary)
        clean = sum(1 for r in repos_summary if not r.get("is_dirty"))
        dirty = sum(1 for r in repos_summary if r.get("is_dirty"))
        behind = sum(1 for r in repos_summary if r.get("behind", 0) > 0)
        ahead = sum(1 for r in repos_summary if r.get("ahead", 0) > 0)
        reviewed = sum(1 for r in repos_summary if r.get("reviewed"))

        cards_html = []
        for r in repos_summary:
            name = r.get("name", "Unknown")
            branch = r.get("branch", "unknown")
            is_dirty = r.get("is_dirty", False)
            dirty_count = r.get("dirty_count", 0)
            behind_cnt = r.get("behind", 0)
            ahead_cnt = r.get("ahead", 0)
            root_path = r.get("path", "")
            reviewed_flag = r.get("reviewed", False)
            review_snippet = r.get("review_snippet", "")
            last_commit = r.get("last_commit", {})

            badge_dirty = '<span class="badge badge-warning">Dirty (' + str(dirty_count) + ')</span>' if is_dirty else '<span class="badge badge-success">Clean</span>'
            badge_sync = ""
            if behind_cnt > 0:
                badge_sync += f'<span class="badge badge-danger">Retard -{behind_cnt}</span> '
            if ahead_cnt > 0:
                badge_sync += f'<span class="badge badge-info">Avance +{ahead_cnt}</span> '
            if not badge_sync:
                badge_sync = '<span class="badge badge-secondary">À jour</span>'

            badge_ocr = '<span class="badge badge-primary">OCR Analysé</span>' if reviewed_flag else '<span class="badge badge-dark">En veille</span>'

            dirty_list_html = ""
            if is_dirty and r.get("dirty_files"):
                dirty_list_html = '<div class="files-box"><strong>Fichiers modifiés :</strong><ul>'
                for df in r.get("dirty_files", [])[:5]:
                    dirty_list_html += f"<li><code>{df}</code></li>"
                if dirty_count > 5:
                    dirty_list_html += f"<li><em>... et {dirty_count - 5} autres fichiers</em></li>"
                dirty_list_html += "</ul></div>"

            review_box = ""
            if review_snippet:
                review_box = f'<div class="review-box"><strong>Rapport OCR :</strong><pre>{review_snippet}</pre></div>'

            commit_info = ""
            if last_commit:
                commit_info = f'<div class="commit-info">Dernier commit: <code>{last_commit.get("hash", "")[:7]}</code> - {last_commit.get("subject", "")} ({last_commit.get("date", "")})</div>'

            card = f"""
            <div class="repo-card" data-dirty="{str(is_dirty).lower()}" data-behind="{behind_cnt}" data-ahead="{ahead_cnt}" data-name="{name.lower()}">
                <div class="card-header">
                    <div class="card-title">
                        <h3>{name}</h3>
                        <span class="branch-tag">{branch}</span>
                    </div>
                    <div class="badges">
                        {badge_dirty}
                        {badge_sync}
                        {badge_ocr}
                    </div>
                </div>
                <div class="card-body">
                    <p class="repo-path"><code>{root_path}</code></p>
                    {commit_info}
                    {dirty_list_html}
                    {review_box}
                </div>
            </div>
            """
            cards_html.append(card)

        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Git OCR Hub - Dashboard</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #334155;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
            --border: #334155;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            padding: 2rem;
            line-height: 1.5;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 2rem;
        }}
        .header h1 {{ font-size: 1.8rem; font-weight: 700; color: var(--primary); }}
        .header p {{ color: var(--text-muted); font-size: 0.9rem; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: var(--surface);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            text-align: center;
        }}
        .stat-card .val {{ font-size: 1.8rem; font-weight: bold; color: var(--text); }}
        .stat-card .label {{ font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }}
        
        .controls {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }}
        .search-box {{
            flex: 1;
            min-width: 250px;
            padding: 0.6rem 1rem;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--text);
            font-size: 0.95rem;
        }}
        .filter-btn {{
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 0.6rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: var(--primary);
            color: #0f172a;
            font-weight: 600;
        }}

        .repos-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 1.25rem;
        }}
        .repo-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            gap: 0.8rem;
            transition: transform 0.15s, border-color 0.15s;
        }}
        .repo-card:hover {{
            border-color: var(--primary);
            transform: translateY(-2px);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.5rem;
        }}
        .card-title h3 {{ font-size: 1.15rem; color: var(--text); word-break: break-all; }}
        .branch-tag {{
            font-size: 0.75rem;
            background: #0f172a;
            color: var(--primary);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: monospace;
            display: inline-block;
            margin-top: 0.2rem;
        }}
        .badges {{ display: flex; gap: 0.4rem; flex-wrap: wrap; justify-content: flex-end; }}
        .badge {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }}
        .badge-success {{ background: rgba(52, 211, 153, 0.2); color: var(--success); }}
        .badge-warning {{ background: rgba(251, 191, 36, 0.2); color: var(--warning); }}
        .badge-danger {{ background: rgba(248, 113, 113, 0.2); color: var(--danger); }}
        .badge-info {{ background: rgba(56, 189, 248, 0.2); color: var(--primary); }}
        .badge-secondary {{ background: rgba(148, 163, 184, 0.2); color: var(--text-muted); }}
        .badge-primary {{ background: #38bdf8; color: #0f172a; }}
        .badge-dark {{ background: #0f172a; color: var(--text-muted); }}

        .repo-path {{ font-size: 0.8rem; color: var(--text-muted); word-break: break-all; }}
        .commit-info {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 0.4rem; }}
        .files-box {{
            background: rgba(15, 23, 42, 0.6);
            padding: 0.6rem;
            border-radius: 6px;
            font-size: 0.8rem;
            margin-top: 0.4rem;
        }}
        .files-box ul {{ list-style: none; margin-top: 0.3rem; padding-left: 0.5rem; }}
        .files-box li {{ color: var(--warning); font-family: monospace; margin-bottom: 0.2rem; }}
        .review-box {{
            background: rgba(15, 23, 42, 0.8);
            border-left: 3px solid var(--primary);
            padding: 0.6rem;
            border-radius: 4px;
            font-size: 0.8rem;
            margin-top: 0.5rem;
            max-height: 150px;
            overflow-y: auto;
        }}
        .review-box pre {{ white-space: pre-wrap; word-break: break-word; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Git OCR Hub - Table de Bord</h1>
            <p>Supervision et Revues de Code Assistées par IA locale (llama.cpp)</p>
        </div>
        <div>
            <p>Dernière mise à jour : <strong>{now_str}</strong></p>
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="val">{total}</div>
            <div class="label">Total Dépôts</div>
        </div>
        <div class="stat-card">
            <div class="val" style="color: var(--success);">{clean}</div>
            <div class="label">Dépôts Propres</div>
        </div>
        <div class="stat-card">
            <div class="val" style="color: var(--warning);">{dirty}</div>
            <div class="label">Avec Modifications</div>
        </div>
        <div class="stat-card">
            <div class="val" style="color: var(--danger);">{behind}</div>
            <div class="label">En Retard (Pull)</div>
        </div>
        <div class="stat-card">
            <div class="val" style="color: var(--primary);">{ahead}</div>
            <div class="label">En Avance (Push)</div>
        </div>
    </div>

    <div class="controls">
        <input type="text" id="search" class="search-box" placeholder="Filtrer par nom de dépôt..." oninput="filterRepos()">
        <button class="filter-btn active" onclick="setFilter('all', this)">Tous ({total})</button>
        <button class="filter-btn" onclick="setFilter('dirty', this)">Modifiés ({dirty})</button>
        <button class="filter-btn" onclick="setFilter('behind', this)">En retard ({behind})</button>
        <button class="filter-btn" onclick="setFilter('clean', this)">Propres ({clean})</button>
    </div>

    <div class="repos-grid" id="reposGrid">
        {"".join(cards_html)}
    </div>

    <script>
        let currentFilter = 'all';

        function setFilter(filter, btn) {{
            currentFilter = filter;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterRepos();
        }}

        function filterRepos() {{
            const search = document.getElementById('search').value.toLowerCase();
            const cards = document.querySelectorAll('.repo-card');

            cards.forEach(card => {{
                const name = card.getAttribute('data-name');
                const isDirty = card.getAttribute('data-dirty') === 'true';
                const behind = parseInt(card.getAttribute('data-behind') || '0');

                const matchesSearch = name.includes(search);
                let matchesFilter = true;

                if (currentFilter === 'dirty') matchesFilter = isDirty;
                else if (currentFilter === 'clean') matchesFilter = !isDirty;
                else if (currentFilter === 'behind') matchesFilter = behind > 0;

                if (matchesSearch && matchesFilter) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
        index_path = os.path.join(self.output_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return index_path
