## @stats_salary
### Interprétation — Expérience / Salaire
- Le jeu contient **30 observations**, 2 variables numériques, **aucune valeur manquante** et aucun doublon : il est directement exploitable.
- L'expérience varie de 1,1 à 10,5 ans (moyenne 5,31 ; écart-type 2,84). Le salaire varie de 37 731 à 122 391 (moyenne 76 003 ; écart-type 27 414).
- La moyenne du salaire (76 003) est supérieure à sa médiane (65 237) et le coefficient d'asymétrie vaut 0,35 : la distribution est **légèrement étalée vers la droite** (quelques salaires élevés tirent la moyenne vers le haut). Elle reste proche d'une distribution symétrique, sans valeur extrême problématique.
- L'écart-type du salaire représente 36 % de sa moyenne : la dispersion est forte, ce qui laisse de la place à une variable explicative comme l'expérience.

## @stats_ins
### Interprétation — Assurance
- **1 338 observations**, 6 variables explicatives (3 numériques : `age`, `bmi`, `children` ; 3 catégorielles : `sex`, `smoker`, `region`) et la cible `charges`. Aucune valeur manquante ; **1 doublon** (supprimé dans la partie 3).
- `age` : de 18 à 64 ans, moyenne 39,2, skewness ≈ 0,06 → distribution quasi uniforme/symétrique.
- `bmi` : moyenne 30,7 (déjà à la limite de l'obésité, seuil 30), skewness 0,28 → proche d'une loi normale, avec quelques valeurs extrêmes (9 valeurs aberrantes selon la règle de l'IQR, maximum 53,1).
- `children` : 0 à 5 enfants, moyenne 1,09, distribution asymétrique (0,94) : la majorité des assurés a 0 ou 1 enfant.
- `charges` (cible) : moyenne 13 270 mais médiane 9 382, maximum 63 770 et **skewness 1,52** : distribution **fortement asymétrique à droite**. Quelques assurés très coûteux tirent la moyenne vers le haut ; cela annonce des erreurs de prédiction élevées pour ces individus avec un modèle linéaire.
- Les modalités sont équilibrées pour `sex` (676 H / 662 F) et `region` (≈ 325 par région), mais **seuls 20,5 % des assurés sont fumeurs** (274).

## @scatter_salary
### Conclusion — nuage de points Expérience / Salaire
Les points sont **alignés autour d'une droite croissante** : le salaire augmente à peu près proportionnellement à l'expérience. Le coefficient de corrélation de Pearson **r = 0,978** confirme une relation linéaire très forte et positive (R² théorique de la régression simple sur toutes les données ≈ 0,957). Il n'y a ni courbure marquée ni point aberrant : **un modèle de régression linéaire simple est parfaitement adapté** à ce jeu de données. (Attention : la corrélation n'implique pas la causalité ; l'expérience résume aussi d'autres facteurs comme la séniorité ou le poste.)

## @matrix
### Interprétation — scatter_matrix du jeu Assurance
- **charges vs age** : on observe trois « bandes » croissantes. L'âge augmente le coût de façon quasi linéaire, mais le niveau de base dépend d'un autre facteur : les **fumeurs (rouge) se situent nettement au-dessus** des non-fumeurs (bleu).
- **charges vs bmi** : pas de tendance claire globalement, mais les **fumeurs avec un IMC > 30 forment un groupe isolé à 35 000–50 000** : il existe une **interaction** fumeur × IMC.
- **charges vs children** : aucune relation visible.
- **age vs bmi** : nuage diffus, les variables explicatives sont peu corrélées entre elles (pas de problème de multicolinéarité).
- Diagonale : `age` ≈ uniforme, `bmi` ≈ cloche, `children` et `charges` asymétriques à droite.

## @eval_salary
### Interprétation de l'évaluation — régression simple
**Modèle appris** : `Salaire = 25 321,58 + 9 423,82 × Expérience`. Chaque année d'expérience supplémentaire augmente le salaire prédit d'environ **9 424** ; un débutant (0 an) démarre à ≈ 25 322.

| Métrique | Entraînement (24 pts) | Test (6 pts) |
|---|---|---|
| MSE | 27 102 250 | 49 830 097 |
| RMSE | 5 206 | 7 059 |
| MAE | 4 221 | 6 286 |
| R² | 0,965 | 0,902 |

- Le **RMSE test de 7 059** correspond à ≈ **9,3 %** du salaire moyen (76 003) : en moyenne, la prédiction se trompe d'environ 7 000 (MAE : 6 286 en moyenne absolue). Le RMSE est plus grand que la MAE car il pénalise davantage les grosses erreurs (ici l'observation à 8,2 ans, sous-estimée de 11 215).
- **R² = 0,90 en test** : le modèle explique 90 % de la variance des salaires non vus pendant l'entraînement.
- L'erreur de test est supérieure à celle d'entraînement, ce qui est normal ; l'écart doit toutefois être relativisé car **le jeu de test ne contient que 6 points** : les métriques sont donc très sensibles au tirage (une validation croisée donnerait une estimation plus stable).
- Avec seulement 6 résidus, aucune structure évidente n'apparaît ; l'hypothèse de linéarité, déjà soutenue par r = 0,978, reste raisonnable. **Conclusion : bon modèle, simple et interprétable.**

## @eda
### Conclusions de l'EDA — Assurance
1. **Qualité des données** : pas de valeur manquante, 1 doublon supprimé (1 337 lignes conservées), variables catégorielles propres (encodées en 0/1 et one-hot avec `drop_first` pour la région).
2. **Cible `charges`** : très asymétrique à droite (skewness 1,52). Le passage au logarithme rend la distribution beaucoup plus symétrique ; on garde néanmoins la cible brute pour que les métriques restent exprimées en dollars.
3. **`smoker` est le facteur dominant** : les fumeurs coûtent en moyenne **32 050 contre 8 441** pour les non-fumeurs (×3,8) ; corrélation avec `charges` : **0,79**.
4. **`age`** : relation croissante nette (corrélation 0,30). **`bmi`** : effet visible surtout chez les fumeurs (corrélation globale 0,20).
5. **Variables peu informatives** : `sex` (moyennes 12 570 F / 13 975 H, médianes quasi identiques), `region` (moyennes entre 12 347 et 14 735) et `children` (corrélation 0,07) ont un effet très faible.
6. **Pas de multicolinéarité** : les variables explicatives sont faiblement corrélées entre elles (voir la matrice).
7. **Limite de la linéarité** : le nuage `charges` vs `age` forme plusieurs groupes et l'effet du `bmi` dépend du statut fumeur → un modèle purement additif ne capturera pas tout.

## @selection
### Justification du choix des 3 propriétés
Les quatre méthodes ont été combinées (moyenne des rangs) pour ne pas dépendre d'un seul critère :

| Propriété | Rang moyen |
|---|---|
| **smoker** | **1,25** |
| **age** | **2,00** |
| **bmi** | **3,25** |
| children | 4,50 |
| sex | 5,25 |
| region_southeast | 5,50 |

- **smoker** est 1er ou 2e partout : corrélation 0,79, score F = 2 176, importance de la forêt aléatoire = 62 %.
- **age** : 2e pour la corrélation et le score F, 1er pour l'information mutuelle (1,50) ; importance RF 13 %.
- **bmi** : 3e pour la corrélation et le score F, et 2e pour l'importance RF (21 %, devant `age`), car la forêt aléatoire capte l'interaction avec le tabagisme que les mesures linéaires sous-estiment (son information mutuelle est faible, 0,07).
- Les autres variables ont une importance RF < 2 % et des scores F faibles : elles sont écartées.
- **Vérification a posteriori** (partie 3, §7) : le modèle à 3 variables atteint pratiquement la même performance (RMSE test 5 987) que celui utilisant les 8 variables (5 956). Le choix est donc justifié : un modèle plus simple sans perte notable.

## @scaling
### Justification du choix : standardisation (`StandardScaler`)
- Les propriétés ont des échelles très différentes (`smoker` ∈ {0,1}, `age` ∈ [18 ; 64], `bmi` ∈ [16 ; 53]). La régression linéaire par moindres carrés n'en a pas besoin pour *prédire* (ses prédictions sont invariantes à l'échelle), mais la mise à l'échelle rend les **coefficients comparables** entre variables et conditionne mieux le problème numérique.
- **Standardisation plutôt que normalisation min-max** : `bmi` est quasi gaussienne et contient des valeurs extrêmes (9 aberrations) ; le min-max, qui dépend du minimum et du maximum, serait fortement influencé par ces points, alors que la standardisation (moyenne 0, écart-type 1) y est moins sensible et reste la convention pour les modèles linéaires.
- Le scaler est **ajusté uniquement sur le jeu d'entraînement** (moyenne et écart-type de l'entraînement appliqués au test) pour éviter toute fuite d'information ; on vérifie bien moyenne = 0 et écart-type = 1 après transformation.

## @viz_ins
### Lecture du graphique
- Les points suivent la diagonale (prédiction parfaite) mais **s'en écartent nettement en deux endroits** : les non-fumeurs réellement très coûteux (bleu, sous la diagonale) sont **sous-estimés**, et les fumeurs forment deux groupes dont l'un est **surestimé** et l'autre **sous-estimé**.
- Les résidus ne sont pas répartis aléatoirement : les fumeurs forment deux paquets (≈ +8 000 et ≈ −9 000) et la variance augmente avec la valeur prédite (hétéroscédasticité). La cause est l'interaction fumeur × IMC mise en évidence par l'EDA, qu'un modèle linéaire additif ne peut pas représenter.
- **Coefficients standardisés** : smoker +9 233, age +3 524, bmi +1 844 (par écart-type). En unités d'origine : être fumeur ajoute ≈ **23 000** de charges, chaque année d'âge ≈ **251**, chaque point d'IMC ≈ **302**, toutes choses égales par ailleurs. L'ordonnée à l'origine (13 030) correspond aux charges moyennes d'entraînement (variables centrées).

## @eval_ins
### Interprétation de l'évaluation — régression multiple

| Métrique | Entraînement (1 069) | Test (268) | 8 variables (test) | Référence : moyenne (test) |
|---|---|---|---|---|
| MSE | 37 485 489 | 35 841 575 | 35 478 021 | 185 298 142 |
| RMSE | 6 123 | 5 987 | 5 956 | 13 612 |
| MAE | 4 228 | 4 192 | 4 177 | 9 862 |
| R² | 0,726 | 0,805 | 0,807 | −0,008 |

- Le modèle explique **≈ 80 % de la variance** des charges sur le jeu de test et **divise l'erreur par 2,3** par rapport à une prédiction naïve par la moyenne (RMSE 5 987 contre 13 612).
- Erreur typique : **MAE ≈ 4 192**, soit ≈ 32 % des charges moyennes (13 270). Le RMSE (5 987) est nettement supérieur à la MAE à cause de quelques gros écarts sur des assurés très coûteux.
- L'écart train/test est faible et **dans le sens inverse du sur-apprentissage** (R² test 0,805 > train 0,726) : il n'y a pas de sur-apprentissage, ce résultat vient d'un jeu de test contenant moins de cas atypiques ; il serait confirmé par une validation croisée.
- Le modèle à **3 variables est quasiment aussi bon que celui à 8** (RMSE 5 987 vs 5 956 ; MAE 4 192 vs 4 177) : les 5 variables écartées n'apportent presque rien, ce qui valide la sélection.
- **Limites et pistes d'amélioration** : la structure des résidus montre une non-linéarité. Il est probable qu'une variable d'interaction `smoker × bmi`, un terme quadratique en `age`, ou une cible transformée par le logarithme, améliorerait sensiblement le modèle (pistes non testées dans cet atelier).

## @degree
### Choix du degré du polynôme
L'erreur de validation croisée chute fortement de 1,75 (degré 1) à 0,25 (degré 4) puis se stabilise : au-delà du degré 4–5, le gain n'est plus significatif devant l'écart-type entre plis. Le minimum « brut » est au degré 7 (0,1998), mais en appliquant la **règle de l'écart-type (1-SE)** on retient le **plus petit degré dont l'erreur est dans un écart-type du minimum, soit le degré 5** : modèle plus simple, statistiquement équivalent, moins exposé au sur-apprentissage (un degré 7 produisait d'ailleurs des extrapolations absurdes, PIB négatif).

## @viz_gdp
### Lecture du graphique
- Le PIB de la Chine suit une courbe **quasi exponentielle** : presque plat jusqu'à la fin des années 1980, puis croissance de plus en plus rapide à partir des années 2000 (10,4 trillions USD en 2014).
- La **droite** ne peut pas épouser cette forme : elle surestime systématiquement entre 1975 et 2007 et sous-estime fortement après 2008. Elle prédit même un **PIB négatif avant 1975** (−0,96 en 1965), ce qui est absurde.
- La **courbe polynomiale de degré 5** suit fidèlement les données sur toute la période, aussi bien pour les points d'entraînement que pour ceux du jeu de test.
- Remarque : la régression polynomiale reste une régression linéaire *multiple* : le modèle est linéaire dans ses paramètres, avec les variables t, t², t³, t⁴, t⁵ construites par `PolynomialFeatures`.

## @eval_gdp
### Interprétation de l'évaluation — linéaire vs polynomiale (unités : trillions USD)

| Métrique | Linéaire (train) | Linéaire (test) | Polynomiale d°5 (train) | Polynomiale d°5 (test) |
|---|---|---|---|---|
| MSE | 2,928 | 2,910 | 0,0264 | 0,0214 |
| RMSE | 1,711 | 1,706 | 0,1624 | 0,1463 |
| MAE | 1,284 | 1,341 | 0,1025 | 0,0818 |
| R² | 0,513 | 0,558 | 0,9956 | 0,9967 |

- **Modèle linéaire : sous-apprentissage (underfitting).** Erreur élevée à la fois en entraînement et en test (RMSE ≈ 1,7 trillion pour un PIB moyen de 1,44) et R² ≈ 0,5 : le modèle est trop simple pour la forme exponentielle des données. Les erreurs train et test étant proches, ce n'est pas un problème de généralisation mais de **biais**.
- **Modèle polynomial : excellent ajustement.** Le RMSE est **≈ 11,7 fois plus faible** (0,146 contre 1,706), R² ≈ 0,997. Les erreurs de test et d'entraînement sont du même ordre (0,146 vs 0,162) : pas de sur-apprentissage visible sur ce découpage.
- **Précaution — interpolation vs extrapolation.** Un polynôme est fiable *dans* la plage 1960–2014 mais **diverge en dehors** : pour 2030, la droite prédit 6,2 et le polynôme 72,8 trillions USD, deux valeurs peu réalistes (le PIB de 2014 est de 10,4). Ces modèles servent à décrire le passé, pas à prévoir l'avenir ; un modèle exponentiel (régression sur log(PIB)) ou logistique serait plus approprié pour de la prévision.
- Le jeu de test ne comptant que 11 points, les métriques restent sensibles au tirage ; le **ordre de grandeur de l'écart** entre les deux modèles est néanmoins très net.
