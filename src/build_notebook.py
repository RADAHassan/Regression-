"""Convertit src/analysis.py (format '# %%') en notebook, puis l'exécute depuis la racine du projet."""
import re, sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parent.parent
src = (root / "src" / "analysis.py").read_text(encoding="utf-8")
interp_path = root / "src" / "interpretations.md"
interp = {}
if interp_path.exists():   # blocs "## @key" -> markdown inséré après la cellule marquée "# @key"
    for key, body in re.findall(r"^## @(\w+)\n(.*?)(?=^## @|\Z)", interp_path.read_text(encoding="utf-8"), flags=re.S | re.M):
        interp[key] = body.strip()

nb = nbformat.v4.new_notebook()
for chunk in re.split(r"^# %%", src, flags=re.M)[1:]:
    is_md = chunk.startswith(" [markdown]")
    body = chunk[len(" [markdown]"):] if is_md else chunk
    body = body.strip("\n")
    if is_md:
        nb.cells.append(nbformat.v4.new_markdown_cell("\n".join(l[2:] if l.startswith("# ") else l.lstrip("#") for l in body.splitlines())))
    else:
        nb.cells.append(nbformat.v4.new_code_cell(body))
        for key in re.findall(r"^# @(\w+)\s*$", body, flags=re.M):
            if key in interp:
                nb.cells.append(nbformat.v4.new_markdown_cell(interp[key]))
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
out = root / "atelier_regression.ipynb"
NotebookClient(nb, timeout=600, resources={"metadata": {"path": str(root)}}).execute()
nbformat.write(nb, out)
print("OK ->", out)
