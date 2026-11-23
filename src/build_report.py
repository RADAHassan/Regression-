"""Génère report/Rapport_Atelier_Regression.pdf à partir de results.json, figures/ et src/interpretations.md."""
import json, os, re
from pathlib import Path
import pandas as pd
import matplotlib
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image, Table, TableStyle,
                                PageBreak, Preformatted, KeepTogether, NextPageTemplate)

root = Path(__file__).resolve().parent.parent
R = json.loads((root / "results.json").read_text(encoding="utf-8"))
fdir = Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf"
for name, f in [("DV", "DejaVuSans"), ("DV-B", "DejaVuSans-Bold"), ("DV-I", "DejaVuSans-Oblique"), ("DV-BI", "DejaVuSans-BoldOblique"), ("DVM", "DejaVuSansMono")]:
    pdfmetrics.registerFont(TTFont(name, str(fdir / f"{f}.ttf")))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

BLUE, GREY = colors.HexColor("#1f4e8c"), colors.HexColor("#5b6670")
body = ParagraphStyle("body", fontName="DV", fontSize=9, leading=13.2, alignment=TA_JUSTIFY, spaceAfter=5)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=2.5)
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=16, leading=20, textColor=BLUE, spaceBefore=4, spaceAfter=10)
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=11.5, leading=15, textColor=BLUE, spaceBefore=10, spaceAfter=5)
h3 = ParagraphStyle("h3", fontName="DV-B", fontSize=9.5, leading=13, textColor=colors.black, spaceBefore=6, spaceAfter=3)
cap = ParagraphStyle("cap", fontName="DV-I", fontSize=8, leading=10.5, textColor=GREY, alignment=TA_CENTER, spaceAfter=8)
cell = ParagraphStyle("cell", fontName="DV", fontSize=8, leading=10.5)
cellh = ParagraphStyle("cellh", parent=cell, fontName="DV-B", textColor=colors.white)
code = ParagraphStyle("code", fontName="DVM", fontSize=7, leading=9, backColor=colors.HexColor("#f3f5f8"), borderPadding=5, spaceBefore=4, spaceAfter=9, leftIndent=4)
W = A4[0] - 4 * cm


def inline(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r'<font name="DVM" size="8">\1</font>', t)
    t = re.sub(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])", r"<i>\1</i>", t)
    return t


def table(rows, widths=None, header=True):
    data = [[Paragraph(inline(str(c)), cellh if (header and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    widths = widths or [W / len(rows[0])] * len(rows[0])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#c5ccd4")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), BLUE)] + [("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f3f6fa")) for i in range(2, len(rows), 2)]
    t.setStyle(TableStyle(st))
    return t


def md(text):
    """Mini-convertisseur Markdown -> flowables (titres ###, puces, tableaux, paragraphes)."""
    out, lines, i = [], text.strip().splitlines(), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.startswith("### "):
            out.append(Paragraph(inline(ln[4:]), h3))
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[\s\-|:]+\|$", lines[i]):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out += [table(rows), Spacer(1, 6)]
            continue
        elif ln.startswith("- "):
            out.append(Paragraph(inline(ln[2:]), bullet, bulletText="•"))
        elif re.match(r"^\d+\. ", ln):
            n, t = ln.split(". ", 1)
            out.append(Paragraph(inline(t), bullet, bulletText=n + "."))
        elif ln:
            out.append(Paragraph(inline(ln), body))
        i += 1
    return out


raw = (root / "src" / "interpretations.md").read_text(encoding="utf-8")
I = {k: b.strip() for k, b in re.findall(r"^## @(\w+)\n(.*?)(?=^## @|\Z)", raw, flags=re.S | re.M)}


def fig(name, caption, width=W):
    p = root / "figures" / f"{name}.png"
    w, h = PILImage.open(p).size
    width = min(width, W)
    return KeepTogether([Image(str(p), width=width, height=width * h / w), Paragraph(caption, cap)])


def codeblock(s):
    return Preformatted(s.strip("\n"), code)


# ------------------------------------------------------------------ documents
def on_page(c, d):
    c.saveState()
    c.setFont("DV", 7.5); c.setFillColor(GREY)
    c.drawString(2 * cm, A4[1] - 1.2 * cm, "FST Tanger — LSI S3 — Machine Learning — Atelier 1 « Régression » — 2024/2025")
    c.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {d.page}")
    c.setStrokeColor(colors.HexColor("#c5ccd4")); c.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
    c.restoreState()


doc = BaseDocTemplate(str(root / "report" / "Rapport_Atelier_Regression.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                      topMargin=2 * cm, bottomMargin=1.8 * cm, title="Rapport — Atelier 1 Régression", author="LSI S3 — FST Tanger")
frame = Frame(doc.leftMargin, doc.bottomMargin, W, A4[1] - doc.topMargin - doc.bottomMargin, id="f")
doc.addPageTemplates([PageTemplate(id="cover", frames=[frame]), PageTemplate(id="main", frames=[frame], onPage=on_page)])

S = []
# ---------------------------------------------------------------- couverture
ctr = lambda sz, f="DV", col=colors.black, sp=6: ParagraphStyle("c", fontName=f, fontSize=sz, leading=sz * 1.3, alignment=TA_CENTER, textColor=col, spaceAfter=sp)
S += [Spacer(1, 1.2 * cm), Paragraph("Université Abdelmalek Essaadi", ctr(14, "DV-B")), Paragraph("Faculté des Sciences et Techniques de Tanger", ctr(12, "DV-B")),
      Paragraph("Département Génie Informatique", ctr(12, "DV-B")), Paragraph("Cycle Ingénieur : LSI S3 — Module : Machine Learning", ctr(10, sp=2)),
      Paragraph("Pr. EL AACHAK Lotfi — Année universitaire 2024/2025", ctr(10, sp=70)),
      Paragraph("RAPPORT D'ATELIER 1", ctr(13, "DV-B", GREY, 8)), Paragraph("Régression linéaire simple, multiple et polynomiale", ctr(22, "DV-B", BLUE, 14)),
      Paragraph("Expérience / Salaire · Assurance · China GDP", ctr(12, "DV", GREY, 90)),
      Paragraph("Outils : Python 3.12 · pandas · scikit-learn · matplotlib · seaborn", ctr(9.5, sp=40)),
      Paragraph("Réalisé par : ______________________________________", ctr(10.5, sp=8)),
      Paragraph("Notebook et code source : github.com/RADAHassan/Regression-", ctr(9, "DV", GREY)),
      NextPageTemplate("main"), PageBreak()]

# ---------------------------------------------------------------- sommaire
S += [Paragraph("Sommaire", h1)]
for t in ["1. Introduction, objectifs et méthodologie", "2. Partie 1 — Visualisation des données", "3. Partie 2 — Régression linéaire simple (Expérience / Salaire)",
          "4. Partie 3 — Régression linéaire multiple (Assurance)", "5. Partie 4 — Régression linéaire vs polynomiale (China GDP)",
          "6. Conclusion générale", "Annexe — Reproduire les résultats"]:
    S.append(Paragraph(t, ParagraphStyle("toc", parent=body, fontSize=10.5, leading=20, alignment=0)))
S.append(PageBreak())

# ---------------------------------------------------------------- 1 intro
sal, ins, gdp = (pd.read_csv(root / "data" / f) for f in ["salary.csv", "insurance.csv", "china_gdp.csv"])
S += [Paragraph("1. Introduction, objectifs et méthodologie", h1),
      Paragraph("Cet atelier a pour objectif de pratiquer les deux grandes formes de la régression linéaire — <b>simple</b> (une variable explicative) et "
                "<b>multiple</b> (plusieurs variables explicatives) — puis son extension <b>polynomiale</b>, sur trois jeux de données réels. "
                "Pour chaque jeu, nous explorons les données, entraînons un modèle avec <i>scikit-learn</i>, prédisons sur un jeu de test, "
                "visualisons le résultat et évaluons le modèle avec trois métriques (MSE, RMSE, MAE), complétées par le coefficient de détermination R².", body),
      Paragraph("1.1 Jeux de données", h2),
      table([["Jeu de données", "Source", "Lignes", "Variables", "Cible"],
             ["Expérience / Salaire", "Kaggle (rohankayan)", len(sal), "YearsExperience", "Salary"],
             ["Assurance", "Kaggle (sinaasappel) — « insurance »", len(ins), "age, sex, bmi, children, smoker, region", "charges"],
             ["China GDP", "IBM Cognitive Class (china_gdp.csv)", len(gdp), "Year", "Value (PIB en USD)"]],
            [3.3 * cm, 4.7 * cm, 1.5 * cm, 4.5 * cm, 3 * cm]),
      Spacer(1, 4),
      Paragraph("Les fichiers CSV sont stockés dans le dossier <font name='DVM'>data/</font> du dépôt (les liens Kaggle exigent une connexion ; une copie publique "
                "des mêmes jeux de données a été utilisée).", body),
      Paragraph("1.2 Méthodologie commune", h2)]
S += md("""- **Séparation train/test** : 80 % / 20 % avec `train_test_split(random_state=42)` pour garantir la reproductibilité.
- **Entraînement** : `LinearRegression` (moindres carrés ordinaires) de scikit-learn.
- **Évaluation** sur le jeu de test (et sur le jeu d'entraînement pour détecter le sur/sous-apprentissage) :
- **MSE** = moyenne des erreurs au carré, (1/n) Σ (yᵢ − ŷᵢ)². Pénalise fortement les grosses erreurs ; son unité est celle de y au carré.
- **RMSE** = √MSE. Même unité que la cible : erreur « typique », sensible aux valeurs extrêmes.
- **MAE** = moyenne des erreurs absolues, (1/n) Σ |yᵢ − ŷᵢ|. Erreur moyenne, plus robuste aux valeurs extrêmes.
- **R²** (en complément) = part de variance expliquée ; 1 = modèle parfait, 0 = équivalent à prédire la moyenne.
- **Prétraitement** sans fuite de données : les transformations (standardisation, expansion polynomiale) sont ajustées sur l'entraînement uniquement.""")

# ---------------------------------------------------------------- partie 1
S += [PageBreak(), Paragraph("2. Partie 1 — Visualisation des données", h1), Paragraph("2.1 Exploration avec pandas", h2),
      Paragraph("Les méthodes <font name='DVM'>head()</font>, <font name='DVM'>info()</font>, <font name='DVM'>isna()</font>, <font name='DVM'>duplicated()</font> "
                "et <font name='DVM'>value_counts()</font> ont été utilisées. Les trois jeux sont propres : aucune valeur manquante ; un seul doublon dans le jeu Assurance.", body),
      Paragraph("2.2 Résumé statistique", h2)]


def describe_table(df, cols):
    d = df[cols].describe().T
    rows = [["Variable", "n", "moy.", "σ", "min", "25 %", "50 %", "75 %", "max"]]
    for c, r in d.iterrows():
        rows.append([c] + [f"{r['count']:.0f}"] + [(f"{r[k]:,.0f}" if abs(r[k]) >= 1000 else f"{r[k]:.2f}").replace(",", " ") for k in ["mean", "std", "min", "25%", "50%", "75%", "max"]])
    return table(rows, [2.9 * cm] + [1.3 * cm] + [1.8 * cm] * 7)


S += [Paragraph("Jeu Expérience / Salaire", h3), describe_table(sal, ["YearsExperience", "Salary"]), Spacer(1, 4)] + md(I["stats_salary"])
S += [Paragraph("Jeu Assurance (variables numériques)", h3), describe_table(ins, ["age", "bmi", "children", "charges"]), Spacer(1, 4)] + md(I["stats_ins"])
S += [Paragraph("2.3 Nuage de points Expérience / Salaire", h2), fig("p1_scatter_salary", "Figure 1 — Salaire en fonction des années d'expérience", W * .7)] + md(I["scatter_salary"])
S += [Paragraph("2.4 Nuages de points du jeu Assurance (scatter_matrix)", h2), codeblock("""
from pandas.plotting import scatter_matrix
colors = insurance["smoker"].map({"yes": "#d62728", "no": "#1f77b4"})
scatter_matrix(insurance[["age", "bmi", "children", "charges"]], diagonal="hist", c=colors, alpha=.6)"""),
      fig("p1_scatter_matrix_insurance", "Figure 2 — scatter_matrix du jeu Assurance (rouge : fumeur, bleu : non-fumeur)", W * .85)] + md(I["matrix"])

# ---------------------------------------------------------------- partie 2
s = R["salary"]
S += [PageBreak(), Paragraph("3. Partie 2 — Régression linéaire simple (Expérience / Salaire)", h1),
      Paragraph(f"Modèle : <i>Salaire = β₀ + β₁ × Expérience</i>. Le jeu est découpé en {s['n_train']} observations d'entraînement et {s['n_test']} de test.", body),
      codeblock("""
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
lin = LinearRegression().fit(X_train, y_train)       # 1. entraînement
y_pred = lin.predict(X_test)                         # 2. prédiction sur le jeu de test"""),
      Paragraph(f"Coefficients appris : <b>β₀ = {s['intercept']:,.2f}</b> (ordonnée à l'origine) et <b>β₁ = {s['coef']:,.2f}</b> (pente).".replace(",", " "), body),
      fig("p2_regression_salary", "Figure 3 — Droite de régression sur les jeux d'entraînement (gauche) et de test (droite)"),
      fig("p2_residuals_salary", "Figure 4 — Résidus sur le jeu de test", W * .55),
      Paragraph("Évaluation (MSE, RMSE, MAE)", h2)] + md(I["eval_salary"])

# ---------------------------------------------------------------- partie 3
S += [PageBreak(), Paragraph("4. Partie 3 — Régression linéaire multiple (Assurance)", h1), Paragraph("4.1 Analyse exploratoire (EDA)", h2),
      fig("p3_eda", "Figure 5 — Distribution de la cible et relation avec les variables explicatives"),
      fig("p3_corr_heatmap", "Figure 6 — Matrice de corrélation (variables encodées)", W * .7)] + md(I["eda"])
sel = pd.DataFrame(R["selection"]["table"])
S += [Paragraph("4.2 Sélection des 3 propriétés les plus importantes", h2),
      Paragraph("Quatre techniques complémentaires ont été appliquées sur les variables encodées (<i>smoker</i> et <i>sex</i> en 0/1, <i>region</i> en variables indicatrices) : "
                "corrélation de Pearson avec la cible, test F univarié (<font name='DVM'>f_regression</font>), information mutuelle "
                "(<font name='DVM'>mutual_info_regression</font>) et importance des variables d'une forêt aléatoire (<font name='DVM'>RandomForestRegressor</font>).", body),
      table([["Propriété", "|corr|", "Score F", "Info. mutuelle", "Importance RF", "Rang moyen"]] +
            [[r["feature"], f"{r['|corr| (Pearson)']:.3f}", f"{r['Score F']:.1f}", f"{r['Info. mutuelle']:.3f}", f"{r['Importance RF']:.3f}", f"{r['Rang moyen']:.2f}"] for _, r in sel.iterrows()],
            [4 * cm, 2.3 * cm, 2.6 * cm, 2.8 * cm, 2.8 * cm, 2.5 * cm]), Spacer(1, 6),
      fig("p3_feature_selection", "Figure 7 — Scores d'importance selon les quatre méthodes (en rouge : variables retenues)")] + md(I["selection"])
S += [Paragraph("4.3 Standardisation des propriétés retenues", h2), codeblock("""
X = enc[["smoker", "age", "bmi"]];  y = enc["charges"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler().fit(X_train)       # ajusté sur l'entraînement uniquement
X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)""")] + md(I["scaling"])
im = R["insurance"]
S += [Paragraph("4.4 – 4.6 Entraînement, prédiction et visualisation", h2),
      Paragraph(f"Le jeu est découpé en {im['n_train']} observations d'entraînement et {im['n_test']} de test. Modèle appris (variables standardisées) :", body),
      Paragraph(f"<i>charges</i> = {im['intercept']:,.2f} + {im['coefs']['smoker']:,.2f} × <i>smoker</i> + {im['coefs']['age']:,.2f} × <i>age</i> + {im['coefs']['bmi']:,.2f} × <i>bmi</i>".replace(",", " "),
                ParagraphStyle("eq", parent=body, alignment=TA_CENTER, textColor=BLUE)),
      fig("p3_regression_insurance", "Figure 8 — Valeurs réelles vs prédites (gauche) et résidus (droite) sur le jeu de test"),
      fig("p3_coefficients", "Figure 9 — Coefficients du modèle (variables standardisées)", W * .5)] + md(I["viz_ins"])
S += [Paragraph("4.7 Évaluation (MSE, RMSE, MAE)", h2)] + md(I["eval_ins"])

# ---------------------------------------------------------------- partie 4
g = R["gdp"]
S += [PageBreak(), Paragraph("5. Partie 4 — Régression linéaire vs polynomiale (China GDP)", h1),
      Paragraph(f"Le jeu contient le PIB annuel de la Chine de 1960 à 2014 ({g['n_train'] + g['n_test']} observations ; {g['n_train']} pour l'entraînement et {g['n_test']} pour le test). "
                "Le PIB est exprimé en <b>trillions de dollars</b> (10¹² USD) et l'année est remplacée par le nombre d'années écoulées depuis 1960 pour un meilleur conditionnement numérique.", body),
      fig("p4_gdp_raw", "Figure 10 — PIB de la Chine, 1960-2014", W * .62),
      Paragraph("5.1 Deux modèles", h2),
      Paragraph("<b>Modèle 1 — régression linéaire</b> : <i>PIB = β₀ + β₁·t</i>. <b>Modèle 2 — régression polynomiale</b> : <i>PIB = β₀ + β₁·t + β₂·t² + … + β_d·t<super>d</super></i>, "
                "obtenue en transformant t avec <font name='DVM'>PolynomialFeatures</font> puis en appliquant la régression linéaire sur ces nouvelles variables : "
                "c'est donc une régression linéaire <i>multiple</i> (linéaire par rapport aux paramètres).", body),
      codeblock("""
lin_g  = LinearRegression().fit(X_train, y_train)
poly_g = make_pipeline(PolynomialFeatures(degree, include_bias=False),
                       StandardScaler(), LinearRegression()).fit(X_train, y_train)
pred_lin, pred_poly = lin_g.predict(X_test), poly_g.predict(X_test)"""),
      Paragraph("5.2 Choix du degré par validation croisée", h2),
      table([["Degré", "RMSE CV (moyenne)", "RMSE CV (écart-type)"]] + [[r["degré"], f"{r['RMSE CV (moy.)']:.4f}", f"{r['RMSE CV (écart-type)']:.4f}"] for r in g["cv"]], [3 * cm, 5 * cm, 5 * cm]),
      Spacer(1, 6), fig("p4_degree_selection", "Figure 11 — RMSE de validation croisée (5 plis) selon le degré", W * .55)] + md(I["degree"])
S += [Paragraph("5.3 Prédictions et visualisation", h2), fig("p4_regression_gdp", "Figure 12 — Régression linéaire et polynomiale sur le PIB de la Chine")] + md(I["viz_gdp"])
S += [Paragraph("5.4 Évaluation (MSE, RMSE, MAE)", h2), fig("p4_pred_vs_real", "Figure 13 — Valeurs réelles vs prédites sur le jeu de test, pour les deux modèles", W * .85)] + md(I["eval_gdp"])

# ---------------------------------------------------------------- conclusion
st, it, gl, gp = R["salary"]["test"], R["insurance"]["test"], g["linear"]["test"], g["poly"]["test"]
S += [PageBreak(), Paragraph("6. Conclusion générale", h1),
      table([["Modèle", "Données", "MSE (test)", "RMSE (test)", "MAE (test)", "R² (test)"],
             ["Régression linéaire simple", "Expérience → Salaire", f"{st['MSE']:,.0f}".replace(",", " "), f"{st['RMSE']:,.0f}".replace(",", " "), f"{st['MAE']:,.0f}".replace(",", " "), f"{st['R2']:.3f}"],
             ["Régression linéaire multiple (3 var.)", "Assurance", f"{it['MSE']:,.0f}".replace(",", " "), f"{it['RMSE']:,.0f}".replace(",", " "), f"{it['MAE']:,.0f}".replace(",", " "), f"{it['R2']:.3f}"],
             ["Régression linéaire", "China GDP (Tn USD)", f"{gl['MSE']:.3f}", f"{gl['RMSE']:.3f}", f"{gl['MAE']:.3f}", f"{gl['R2']:.3f}"],
             [f"Régression polynomiale (degré {g['degree']})", "China GDP (Tn USD)", f"{gp['MSE']:.4f}", f"{gp['RMSE']:.4f}", f"{gp['MAE']:.4f}", f"{gp['R2']:.3f}"]],
            [4.6 * cm, 3.4 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2.1 * cm]), Spacer(1, 8)]
S += md("""- **Expérience / Salaire** : relation presque parfaitement linéaire (r = 0,98) ; la régression simple suffit et fournit un modèle interprétable (≈ +9 424 par année d'expérience).
- **Assurance** : le tabagisme est de loin le facteur le plus déterminant, devant l'âge et l'IMC. Trois variables suffisent pour atteindre les performances du modèle à huit variables (R² ≈ 0,80), mais les résidus révèlent une interaction fumeur × IMC non captée par un modèle additif.
- **China GDP** : la croissance est non linéaire ; la droite sous-apprend (R² ≈ 0,56) tandis que la régression polynomiale de degré 5 épouse la courbe (R² ≈ 0,997). Ce modèle n'est valable que dans la plage d'années observée.
- **Enseignements généraux** : (1) toujours visualiser les données avant de choisir le modèle ; (2) évaluer sur des données non vues et comparer à une référence simple ; (3) le choix de la complexité (degré, nombre de variables) se justifie par validation croisée ; (4) un jeu de test très petit (6 et 11 points) rend les métriques sensibles au tirage aléatoire.""")

# ---------------------------------------------------------------- annexe
S += [Paragraph("Annexe — Reproduire les résultats", h1)] + md("""Le dépôt contient : `data/` (jeux de données), `src/analysis.py` (code source commenté de toute l'analyse), `atelier_regression.ipynb` (notebook exécuté avec les sorties), `figures/` (graphiques), `results.json` (métriques) et `report/` (ce rapport).""")
S += [codeblock("""
pip install pandas scikit-learn matplotlib seaborn nbformat nbclient ipykernel reportlab pillow
python src/build_notebook.py      # exécute l'analyse -> atelier_regression.ipynb, figures/, results.json
python src/build_report.py        # génère report/Rapport_Atelier_Regression.pdf""")]

doc.build(S)
print("OK ->", doc.filename)
