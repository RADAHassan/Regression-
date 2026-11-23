# %% [markdown]
# # Atelier 1 — Régression (Machine Learning, LSI S3, 2024/2025)
# **Université Abdelmalek Essaadi — FST Tanger — Département Génie Informatique**
#
# Objectif : pratiquer la régression linéaire simple, multiple et polynomiale sur trois jeux de données
# (Expérience/Salaire, Assurance, China GDP) avec Python, Pandas, Scikit-learn et Matplotlib.

# %%
import os, json, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import scatter_matrix

from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

warnings.filterwarnings("ignore")
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": .3,
                     "axes.spines.top": False, "axes.spines.right": False})
os.makedirs("figures", exist_ok=True)
SEED = 42
RESULTS = {}          # métriques sauvegardées dans results.json (utilisées par le rapport)


def save(fig, name):
    fig.tight_layout(rect=(0, 0, 1, 0.97) if fig._suptitle else None)
    fig.savefig(f"figures/{name}.png", dpi=150)
    plt.show()


def evaluate(y_true, y_pred):
    """MSE, RMSE, MAE (+ R² en complément)."""
    mse = mean_squared_error(y_true, y_pred)
    return {"MSE": float(mse), "RMSE": float(np.sqrt(mse)),
            "MAE": float(mean_absolute_error(y_true, y_pred)), "R2": float(r2_score(y_true, y_pred))}

# %% [markdown]
# ---
# # Partie 1 — Data Visualisation
# ## 1. Exploration des données avec pandas

# %%
salary = pd.read_csv("data/salary.csv")
insurance = pd.read_csv("data/insurance.csv")
gdp = pd.read_csv("data/china_gdp.csv")

print("=== Expérience / Salaire ===", salary.shape)
display(salary.head())
salary.info()
print("\nValeurs manquantes :\n", salary.isna().sum().to_string())
print("Doublons :", salary.duplicated().sum())

# %%
print("=== Assurance ===", insurance.shape)
display(insurance.head())
insurance.info()
print("\nValeurs manquantes :\n", insurance.isna().sum().to_string())
print("Doublons :", insurance.duplicated().sum())
for c in ["sex", "smoker", "region"]:
    print(f"\n{c} ->", insurance[c].value_counts().to_dict())

# %% [markdown]
# ## 2. Résumé statistique

# %%
print("=== Expérience / Salaire ===")
display(salary.describe().T)
print("Coefficient d'asymétrie (skew) :", salary.skew().round(3).to_dict())
# @stats_salary

# %%
print("=== Assurance (variables numériques) ===")
display(insurance.describe().T)
print("=== Assurance (variables catégorielles) ===")
display(insurance.describe(include="object").T)
print("Skewness :", insurance.select_dtypes("number").skew().round(3).to_dict())
# @stats_ins

# %% [markdown]
# ## 3. Nuage de points Expérience / Salaire

# %%
fig, ax = plt.subplots(figsize=(7, 4.5))
salary.plot.scatter(x="YearsExperience", y="Salary", ax=ax, color="#1f6feb", s=45, edgecolor="white")
ax.set_title("Salaire en fonction des années d'expérience")
ax.set_xlabel("Années d'expérience"); ax.set_ylabel("Salaire")
save(fig, "p1_scatter_salary")
r_sal = salary["YearsExperience"].corr(salary["Salary"])
RESULTS["salary_pearson_r"] = float(r_sal)
print(f"Corrélation de Pearson r = {r_sal:.4f}")
# @scatter_salary

# %% [markdown]
# ## 4. Nuages de points du jeu Assurance (`scatter_matrix`)

# %%
num_cols = ["age", "bmi", "children", "charges"]
colors = insurance["smoker"].map({"yes": "#d62728", "no": "#1f77b4"})
axes = scatter_matrix(insurance[num_cols], figsize=(9, 8), diagonal="hist", alpha=.6, s=12, c=colors, hist_kwds={"bins": 30})
plt.suptitle("scatter_matrix — assurance (rouge = fumeur, bleu = non-fumeur)")
save(plt.gcf(), "p1_scatter_matrix_insurance")
# @matrix

# %% [markdown]
# ---
# # Partie 2 — Régression linéaire simple (Expérience → Salaire)

# %%
X = salary[["YearsExperience"]]
y = salary["Salary"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED)
print("Train :", X_train.shape, " Test :", X_test.shape)

# 1. Entraînement
lin = LinearRegression().fit(X_train, y_train)
print(f"Salaire = {lin.intercept_:.2f} + {lin.coef_[0]:.2f} x Expérience")

# 2. Prédiction sur le jeu de test
y_pred = lin.predict(X_test)
display(pd.DataFrame({"Expérience": X_test["YearsExperience"].values, "Salaire réel": y_test.values,
                      "Salaire prédit": y_pred.round(2), "Erreur": (y_test.values - y_pred).round(2)}))

# %%
# 3. Visualisation
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
grid = pd.DataFrame({"YearsExperience": np.linspace(X["YearsExperience"].min(), X["YearsExperience"].max(), 100)})
for ax, (Xs, ys, lab, col) in zip(axes, [(X_train, y_train, "Entraînement", "#1f6feb"), (X_test, y_test, "Test", "#d62728")]):
    ax.scatter(Xs, ys, color=col, s=45, edgecolor="white", label=f"Données ({lab})")
    ax.plot(grid, lin.predict(grid), color="black", lw=2, label="Droite de régression")
    ax.set_title(f"Régression linéaire simple — {lab}"); ax.set_xlabel("Années d'expérience"); ax.set_ylabel("Salaire"); ax.legend()
save(fig, "p2_regression_salary")

# %%
# 4. Évaluation
m_train = evaluate(y_train, lin.predict(X_train))
m_test = evaluate(y_test, y_pred)
RESULTS["salary"] = {"intercept": float(lin.intercept_), "coef": float(lin.coef_[0]),
                     "n_train": len(X_train), "n_test": len(X_test), "train": m_train, "test": m_test,
                     "mean_salary": float(y.mean()), "std_salary": float(y.std())}
display(pd.DataFrame({"Train": m_train, "Test": m_test}).round(4))
print(f"RMSE test / salaire moyen = {m_test['RMSE'] / y.mean():.1%}")

# %%
res = y_test - y_pred
fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(y_pred, res, color="#1f6feb", s=45, edgecolor="white"); ax.axhline(0, color="k", lw=1)
ax.set_title("Résidus (jeu de test)"); ax.set_xlabel("Salaire prédit"); ax.set_ylabel("Résidu")
save(fig, "p2_residuals_salary")
# @eval_salary

# %% [markdown]
# ---
# # Partie 3 — Régression linéaire multiple (Assurance)
# ## 1. Analyse exploratoire (EDA)

# %%
ins = insurance.drop_duplicates().reset_index(drop=True)
print("Après suppression des doublons :", ins.shape)

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
sns.histplot(ins["charges"], bins=40, kde=True, ax=axes[0, 0], color="#1f6feb"); axes[0, 0].set_title("Distribution de charges")
sns.histplot(np.log(ins["charges"]), bins=40, kde=True, ax=axes[0, 1], color="#2ca02c"); axes[0, 1].set_title("Distribution de log(charges)")
sns.histplot(ins["bmi"], bins=30, kde=True, ax=axes[0, 2], color="#9467bd"); axes[0, 2].set_title("Distribution de bmi")
sns.boxplot(data=ins, x="smoker", y="charges", ax=axes[1, 0], palette=["#1f77b4", "#d62728"]); axes[1, 0].set_title("charges selon smoker")
sns.boxplot(data=ins, x="region", y="charges", ax=axes[1, 1]); axes[1, 1].set_title("charges selon region")
sns.scatterplot(data=ins, x="age", y="charges", hue="smoker", ax=axes[1, 2], s=18, palette=["#1f77b4", "#d62728"]); axes[1, 2].set_title("charges selon age (et smoker)")
save(fig, "p3_eda")

# %%
print(ins.groupby("smoker")["charges"].agg(["count", "mean", "median"]).round(1))
print(ins.groupby("sex")["charges"].agg(["count", "mean", "median"]).round(1))
print(ins.groupby("region")["charges"].agg(["count", "mean", "median"]).round(1))
print(ins.groupby("children")["charges"].agg(["count", "mean"]).round(1))
print("Valeurs aberrantes (IQR) sur bmi :", int(((ins.bmi < ins.bmi.quantile(.25) - 1.5 * (ins.bmi.quantile(.75) - ins.bmi.quantile(.25))) |
                                              (ins.bmi > ins.bmi.quantile(.75) + 1.5 * (ins.bmi.quantile(.75) - ins.bmi.quantile(.25)))).sum()))

# Encodage des variables catégorielles
enc = ins.copy()
enc["sex"] = (enc["sex"] == "male").astype(int)
enc["smoker"] = (enc["smoker"] == "yes").astype(int)
enc = pd.get_dummies(enc, columns=["region"], drop_first=True, dtype=int)
display(enc.head())

fig, ax = plt.subplots(figsize=(8, 6.5))
sns.heatmap(enc.corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Matrice de corrélation (variables encodées)")
save(fig, "p3_corr_heatmap")
# @eda

# %% [markdown]
# ## 2. Sélection des 3 propriétés les plus importantes
# Quatre techniques complémentaires sont appliquées, puis leurs rangs sont agrégés :
# corrélation de Pearson, test F (`f_regression`), information mutuelle et importance par forêt aléatoire.

# %%
features = [c for c in enc.columns if c != "charges"]
Xa, ya = enc[features], enc["charges"]

corr = Xa.corrwith(ya).abs()
f_scores, _ = f_regression(Xa, ya)
mi = mutual_info_regression(Xa, ya, random_state=SEED)
rf = RandomForestRegressor(n_estimators=300, random_state=SEED).fit(Xa, ya)

sel = pd.DataFrame({"|corr| (Pearson)": corr, "Score F": f_scores, "Info. mutuelle": mi, "Importance RF": rf.feature_importances_}, index=features)
ranks = sel.rank(ascending=False)
sel["Rang moyen"] = ranks.mean(axis=1)
sel = sel.sort_values("Rang moyen")
display(sel.round(4))
top3 = list(sel.index[:3])
print("Les 3 propriétés retenues :", top3)
RESULTS["selection"] = {"table": sel.round(5).reset_index().rename(columns={"index": "feature"}).to_dict("records"), "top3": top3}

fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, col in zip(axes, ["|corr| (Pearson)", "Score F", "Info. mutuelle", "Importance RF"]):
    s = sel[col].sort_values()
    ax.barh(s.index, s.values, color=["#d62728" if i in top3 else "#9aa5b1" for i in s.index]); ax.set_title(col)
save(fig, "p3_feature_selection")
# @selection

# %% [markdown]
# ## 3. Standardisation des propriétés retenues
# On utilise `StandardScaler` (z = (x − μ) / σ). Le scaler est **ajusté sur le jeu d'entraînement uniquement**
# afin d'éviter toute fuite de données (data leakage) vers le jeu de test.

# %%
print(enc[top3].describe().loc[["mean", "std", "min", "max"]].round(2))
X3, y3 = enc[top3], enc["charges"]
X3_train, X3_test, y3_train, y3_test = train_test_split(X3, y3, test_size=0.2, random_state=SEED)
scaler = StandardScaler().fit(X3_train)
X3_train_s = pd.DataFrame(scaler.transform(X3_train), columns=top3, index=X3_train.index)
X3_test_s = pd.DataFrame(scaler.transform(X3_test), columns=top3, index=X3_test.index)
print("\nAprès standardisation (train) :")
print(X3_train_s.describe().loc[["mean", "std"]].round(3))
# @scaling

# %% [markdown]
# ## 4–5. Entraînement et prédiction

# %%
mlr = LinearRegression().fit(X3_train_s, y3_train)
coefs = pd.Series(mlr.coef_, index=top3)
print(f"charges = {mlr.intercept_:.2f} + " + " + ".join(f"({v:.2f} x {k}_std)" for k, v in coefs.items()))
y3_pred = mlr.predict(X3_test_s)
display(pd.DataFrame({"charges réelles": y3_test.values, "charges prédites": y3_pred.round(2)}, index=y3_test.index).head(10))

# %% [markdown]
# ## 6. Visualisation

# %%
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sm = X3_test["smoker"].map({1: "#d62728", 0: "#1f77b4"})
axes[0].scatter(y3_test, y3_pred, c=sm, s=20, alpha=.75)
lim = [0, max(y3_test.max(), y3_pred.max()) * 1.03]
axes[0].plot(lim, lim, "k--", lw=1.5, label="Prédiction parfaite (y = x)")
axes[0].set_xlabel("charges réelles"); axes[0].set_ylabel("charges prédites"); axes[0].set_title("Valeurs réelles vs prédites (rouge = fumeur)"); axes[0].legend()
axes[1].scatter(y3_pred, y3_test - y3_pred, c=sm, s=20, alpha=.75); axes[1].axhline(0, color="k", lw=1)
axes[1].set_xlabel("charges prédites"); axes[1].set_ylabel("Résidu"); axes[1].set_title("Résidus (jeu de test)")
save(fig, "p3_regression_insurance")

fig, ax = plt.subplots(figsize=(6, 3.5))
coefs.sort_values().plot.barh(ax=ax, color="#1f6feb"); ax.set_title("Coefficients (variables standardisées)")
save(fig, "p3_coefficients")
# @viz_ins

# %% [markdown]
# ## 7. Évaluation

# %%
m3_train = evaluate(y3_train, mlr.predict(X3_train_s))
m3_test = evaluate(y3_test, y3_pred)
# Référence : modèle avec toutes les variables
sc_all = StandardScaler().fit(Xa.loc[X3_train.index])
mlr_all = LinearRegression().fit(sc_all.transform(Xa.loc[X3_train.index]), y3_train)
m3_all = evaluate(y3_test, mlr_all.predict(sc_all.transform(Xa.loc[X3_test.index])))
# Référence : prédire toujours la moyenne
m3_base = evaluate(y3_test, np.full(len(y3_test), y3_train.mean()))
RESULTS["insurance"] = {"intercept": float(mlr.intercept_), "coefs": coefs.round(2).to_dict(), "n_train": len(X3_train), "n_test": len(X3_test),
                        "train": m3_train, "test": m3_test, "all_features_test": m3_all, "baseline_test": m3_base,
                        "mean_charges": float(ins.charges.mean()), "std_charges": float(ins.charges.std())}
display(pd.DataFrame({"Train": m3_train, "Test": m3_test, "Toutes variables (test)": m3_all, "Référence : moyenne (test)": m3_base}).round(4))
# @eval_ins

# %% [markdown]
# ---
# # Partie 4 — Régression linéaire vs polynomiale (China GDP)

# %%
display(gdp.head()); display(gdp.describe().T)
gdp["GDP_Tn"] = gdp["Value"] / 1e12            # PIB en milliers de milliards (trillions) de dollars
gdp["t"] = gdp["Year"] - gdp["Year"].min()     # années écoulées depuis 1960 (meilleur conditionnement numérique)

fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.scatter(gdp["Year"], gdp["GDP_Tn"], color="#1f6feb", s=30, edgecolor="white")
ax.set_title("PIB de la Chine (1960-2014)"); ax.set_xlabel("Année"); ax.set_ylabel("PIB (trillions USD)")
save(fig, "p4_gdp_raw")

# %%
Xg, yg = gdp[["t"]], gdp["GDP_Tn"]
Xg_train, Xg_test, yg_train, yg_test = train_test_split(Xg, yg, test_size=0.2, random_state=SEED)

# Choix du degré par validation croisée (5 plis) sur le jeu d'entraînement uniquement
kf = KFold(5, shuffle=True, random_state=SEED)
rows = []
for d in range(1, 8):
    pipe = make_pipeline(PolynomialFeatures(d, include_bias=False), StandardScaler(), LinearRegression())
    cv = -cross_val_score(pipe, Xg_train, yg_train, cv=kf, scoring="neg_root_mean_squared_error")
    rows.append({"degré": d, "RMSE CV (moy.)": cv.mean(), "RMSE CV (écart-type)": cv.std()})
cvdf = pd.DataFrame(rows).set_index("degré")
display(cvdf.round(4))
# Règle de l'écart-type (1-SE) : on retient le plus petit degré dont l'erreur reste dans 1 écart-type du minimum
# (modèle le plus simple statistiquement équivalent au meilleur -> limite le sur-apprentissage).
imin = cvdf["RMSE CV (moy.)"].idxmin()
seuil = cvdf.loc[imin, "RMSE CV (moy.)"] + cvdf.loc[imin, "RMSE CV (écart-type)"]
best_deg = int(cvdf[cvdf["RMSE CV (moy.)"] <= seuil].index.min())
print(f"Minimum de la RMSE CV au degré {imin} ; seuil 1-SE = {seuil:.4f} ; degré retenu : {best_deg}")

fig, ax = plt.subplots(figsize=(6.5, 4))
ax.errorbar(cvdf.index, cvdf["RMSE CV (moy.)"], yerr=cvdf["RMSE CV (écart-type)"], marker="o", color="#1f6feb", capsize=3)
ax.axhline(seuil, color="#9aa5b1", ls=":", label="seuil 1-SE"); ax.axvline(best_deg, color="#d62728", ls="--", label=f"degré retenu = {best_deg}"); ax.set_yscale("log")
ax.set_xlabel("Degré du polynôme"); ax.set_ylabel("RMSE (validation croisée, trillions USD)"); ax.set_title("Sélection du degré"); ax.legend()
save(fig, "p4_degree_selection")
# @degree

# %% [markdown]
# ## 1–2. Entraînement et prédiction des deux modèles

# %%
lin_g = LinearRegression().fit(Xg_train, yg_train)
poly_g = make_pipeline(PolynomialFeatures(best_deg, include_bias=False), StandardScaler(), LinearRegression()).fit(Xg_train, yg_train)
pred_lin, pred_poly = lin_g.predict(Xg_test), poly_g.predict(Xg_test)
display(pd.DataFrame({"Année": gdp.loc[Xg_test.index, "Year"].values, "PIB réel": yg_test.values.round(3),
                      "Prédit (linéaire)": pred_lin.round(3), f"Prédit (poly. deg {best_deg})": pred_poly.round(3)}).sort_values("Année"))

# %% [markdown]
# ## 3. Visualisation des deux modèles

# %%
tt = pd.DataFrame({"t": np.linspace(0, 54, 300)})
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.scatter(gdp.loc[Xg_train.index, "Year"], yg_train, color="#9aa5b1", s=32, label="Entraînement")
ax.scatter(gdp.loc[Xg_test.index, "Year"], yg_test, color="#d62728", s=48, edgecolor="k", zorder=3, label="Test")
ax.plot(tt["t"] + 1960, lin_g.predict(tt), color="#2ca02c", lw=2.2, label="Régression linéaire")
ax.plot(tt["t"] + 1960, poly_g.predict(tt), color="#1f6feb", lw=2.2, label=f"Régression polynomiale (degré {best_deg})")
ax.set_xlabel("Année"); ax.set_ylabel("PIB (trillions USD)"); ax.set_title("China GDP — linéaire vs polynomiale"); ax.legend()
save(fig, "p4_regression_gdp")
# @viz_gdp

# %% [markdown]
# ## 4. Évaluation des deux modèles

# %%
g = {"linear": {"train": evaluate(yg_train, lin_g.predict(Xg_train)), "test": evaluate(yg_test, pred_lin)},
     "poly": {"train": evaluate(yg_train, poly_g.predict(Xg_train)), "test": evaluate(yg_test, pred_poly)}}
g.update({"degree": best_deg, "cv_min_degree": int(imin), "n_train": len(Xg_train), "n_test": len(Xg_test), "cv": cvdf.round(5).reset_index().to_dict("records"),
          "mean_gdp": float(yg.mean()), "extrap_2030_linear": float(lin_g.predict(pd.DataFrame({"t": [70]}))[0]),
          "extrap_2030_poly": float(poly_g.predict(pd.DataFrame({"t": [70]}))[0])})
RESULTS["gdp"] = g
display(pd.DataFrame({"Linéaire - Train": g["linear"]["train"], "Linéaire - Test": g["linear"]["test"],
                      "Polynomiale - Train": g["poly"]["train"], "Polynomiale - Test": g["poly"]["test"]}).round(4))
print("Extrapolation 2030 (trillions USD) : linéaire =", round(g["extrap_2030_linear"], 2), "| polynomiale =", round(g["extrap_2030_poly"], 2))

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, (m, pr, col, t) in zip(axes, [(lin_g, pred_lin, "#2ca02c", "Linéaire"), (poly_g, pred_poly, "#1f6feb", f"Polynomiale (deg {best_deg})")]):
    ax.scatter(yg_test, pr, color=col, s=40, edgecolor="white"); lim = [0, yg_test.max() * 1.05]
    ax.plot(lim, lim, "k--"); ax.set_title(f"{t} — réel vs prédit (test)"); ax.set_xlabel("PIB réel"); ax.set_ylabel("PIB prédit")
save(fig, "p4_pred_vs_real")
# @eval_gdp

# %%
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(RESULTS, f, indent=2, ensure_ascii=False)
print("results.json sauvegardé")
