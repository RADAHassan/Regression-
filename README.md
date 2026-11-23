# Atelier 1 — Régression (Machine Learning, LSI S3, FST Tanger, 2024/2025)

Régression linéaire simple, multiple et polynomiale avec Python, pandas, scikit-learn et matplotlib.

| Partie | Jeu de données | Modèle | Résultat (test) |
|---|---|---|---|
| 1 | Expérience/Salaire + Assurance | Exploration, statistiques, nuages de points, `scatter_matrix` | — |
| 2 | Expérience / Salaire | Régression linéaire simple | RMSE ≈ 7 059, MAE ≈ 6 286, R² ≈ 0,90 |
| 3 | Assurance (`smoker`, `age`, `bmi`, standardisées) | Régression linéaire multiple | RMSE ≈ 5 987, MAE ≈ 4 192, R² ≈ 0,80 |
| 4 | China GDP | Linéaire vs polynomiale (degré 5, choisi par validation croisée) | RMSE ≈ 1,706 vs 0,146 (trillions USD) |

## Contenu

- `atelier_regression.ipynb` — notebook exécuté (code, sorties, graphiques et interprétations)
- `report/Rapport_Atelier_Regression.pdf` — rapport détaillé à imprimer
- `src/analysis.py` — code source de l'analyse (format `# %%`)
- `src/interpretations.md` — interprétations insérées dans le notebook et le rapport
- `src/build_notebook.py`, `src/build_report.py` — génération du notebook et du rapport
- `data/` — jeux de données CSV · `figures/` — graphiques · `results.json` — métriques

## Reproduire

```bash
pip install pandas scikit-learn matplotlib seaborn nbformat nbclient ipykernel reportlab pillow
python src/build_notebook.py   # exécute l'analyse -> notebook, figures/, results.json
python src/build_report.py     # génère le rapport PDF
```

## Sources des données

- Expérience/Salaire : <https://www.kaggle.com/rohankayan/years-of-experience-and-salary-dataset> (copie publique des mêmes 30 lignes)
- Assurance : <https://www.kaggle.com/sinaasappel/tutorial-multiple-regression/data> (jeu « insurance », 1 338 lignes)
- China GDP : IBM Cognitive Class, `china_gdp.csv`
