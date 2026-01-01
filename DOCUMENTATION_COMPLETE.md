# 📊 Media Analytics Dashboard - Guide Complet

## Table des Matières

1. [Vue d'Ensemble du Projet](#vue-densemble-du-projet)
2. [Technologies et Bibliothèques](#technologies-et-bibliothèques)
3. [Structure du Projet](#structure-du-projet)
4. [Architecture de l'Application](#architecture-de-lapplication)
5. [Traitement des Données](#traitement-des-données)
6. [Les Visualisations Expliquées](#les-visualisations-expliquées)
7. [Système de Filtrage](#système-de-filtrage)
8. [Design et CSS](#design-et-css)
9. [Comment Lancer le Projet](#comment-lancer-le-projet)

---

## Vue d'Ensemble du Projet

Ce projet est une **application web analytique** permettant d'explorer un corpus de 30 000 articles de presse (Sputnik, etc.). L'objectif est de visualiser des tendances, identifier des corrélations entre entités (personnes, lieux, organisations), et permettre une exploration interactive des données.

### Fonctionnalités Principales

- **4 KPIs dynamiques** : Total articles, Top mot-clé, Top personnalité, Top organisation
- **Timeline interactive** : Évolution du volume d'articles avec zoom temporel
- **Nuage de mots-clés** : Visualisation des thèmes dominants
- **Graphiques Top N** : Personnalités et lieux les plus cités
- **Sunburst hiérarchique** : Exploration Lieux → Organisations
- **Heatmap de corrélation** : Co-occurrence des mots-clés
- **Module IA** : Interface prête pour intégration LLM

---

## Technologies et Bibliothèques

### Backend Python

| Bibliothèque                | Version | Rôle                                           |
| --------------------------- | ------- | ---------------------------------------------- |
| `dash`                      | 2.x     | Framework web principal (basé sur Flask/React) |
| `dash-bootstrap-components` | 1.x     | Composants UI Bootstrap pour Dash              |
| `plotly`                    | 5.x     | Moteur de graphiques interactifs               |
| `pandas`                    | 2.x     | Manipulation et analyse de données             |

### Concepts Clés

- **Dash** : Framework Python qui génère du HTML/CSS/JavaScript automatiquement. On écrit du Python, Dash le transforme en application web.
- **Callbacks** : Mécanisme réactif de Dash. Quand un input change (clic, sélection), une fonction Python s'exécute et met à jour l'interface.
- **Plotly** : Bibliothèque de visualisation qui crée des graphiques SVG/WebGL interactifs.

---

## Structure du Projet

```
Projet_Dashboard_Media/
│
├── app.py                    # Point d'entrée de l'application
├── requirements.txt          # Dépendances Python
├── preprocessing.py          # Script ETL (nettoyage initial)
│
├── data/
│   └── processed/
│       └── clean_data.csv    # Données nettoyées (30K articles)
│
├── src/
│   ├── __init__.py           # Module Python
│   ├── data_processing.py    # Chargement et filtrage des données
│   ├── visualizations.py     # Fonctions de création de graphiques
│   ├── layout.py             # Structure HTML/composants de l'interface
│   └── callbacks.py          # Logique d'interactivité (réactions aux clics)
│
└── assets/
    └── custom_styles.css     # Styles CSS personnalisés (Dark Mode)
```

### Rôle de Chaque Fichier

#### `app.py`

```python
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.layout = create_layout()  # Charge la structure HTML
app.run(debug=True)           # Lance le serveur
```

- Initialise l'application Dash
- Applique le thème Bootstrap "CYBORG" (dark mode)
- Importe et exécute les callbacks

#### `src/data_processing.py`

- `load_data()` : Charge le CSV et parse les listes (mots-clés, lieux, etc.)
- `filter_data()` : Filtre les articles par date, mots-clés, lieux
- `explode_entities()` : Transforme les listes en lignes individuelles pour le comptage
- `compute_cooccurrence_matrix()` : Calcule les co-apparitions de mots-clés

#### `src/layout.py`

- `create_sidebar()` : Barre latérale avec filtres (DatePicker, Dropdowns)
- `create_kpi_cards()` : Les 4 cartes KPI en haut
- `create_tabs_content()` : Les onglets (Vue d'ensemble, Entités, Corrélation, IA)
- `create_layout()` : Assemble le tout

#### `src/visualizations.py`

- `create_timeline()` : Graphique temporel
- `create_sunburst()` : Hiérarchie Lieux/Organisations
- `create_cooccurrence_heatmap()` : Matrice de corrélation
- `create_top_persons_bar()` : Top personnalités
- `create_top_locations_bar()` : Top lieux
- `create_wordcloud_scatter()` : Nuage de mots

#### `src/callbacks.py`

- `initialize_filters()` : Remplit les dropdowns au chargement
- `update_all_charts()` : Met à jour TOUS les graphiques quand un filtre change
- `reset_filters()` : Réinitialise les sélections
- `ai_analyst_response()` : Gère le module IA

---

## Architecture de l'Application

```
┌─────────────────────────────────────────────────────────┐
│                      NAVIGATEUR                          │
│  ┌──────────┐  ┌─────────────────────────────────────┐  │
│  │ SIDEBAR  │  │            CONTENT AREA              │  │
│  │ Filtres  │  │  ┌─────┬─────┬─────┬─────┐          │  │
│  │ - Date   │  │  │ KPI │ KPI │ KPI │ KPI │          │  │
│  │ - Mots   │  │  └─────┴─────┴─────┴─────┘          │  │
│  │ - Lieux  │  │  ┌─────────────────────────┐        │  │
│  │          │  │  │        TABS             │        │  │
│  └──────────┘  │  │  - Vue d'ensemble       │        │  │
│                │  │  - Exploration Entités  │        │  │
│                │  │  - Corrélation          │        │  │
│                │  │  - AI Analyst           │        │  │
│                │  └─────────────────────────┘        │  │
│                └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         │                    ▲
         │  Callbacks         │  Mise à jour
         ▼                    │
┌─────────────────────────────────────────────────────────┐
│                    SERVEUR DASH                          │
│  ┌───────────────┐  ┌─────────────────────────────────┐ │
│  │ data_processing│  │      visualizations.py         │ │
│  │  - load_data() │  │  - create_timeline()           │ │
│  │  - filter()    │  │  - create_sunburst()           │ │
│  └───────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Traitement des Données

### Format des Données (clean_data.csv)

| Colonne   | Type          | Description                                  |
| --------- | ------------- | -------------------------------------------- |
| `date`    | datetime      | Date de publication                          |
| `title`   | string        | Titre de l'article                           |
| `kws`     | list (string) | Mots-clés : `['Politique', 'Santé', 'Tech']` |
| `loc`     | list (string) | Lieux : `['Paris', 'Moscou']`                |
| `org`     | list (string) | Organisations : `['ONU', 'UE']`              |
| `per`     | list (string) | Personnes : `['Macron', 'Biden']`            |
| `content` | string        | Texte complet de l'article                   |

### Parsing des Listes (Problème Clé)

Les colonnes `kws`, `loc`, `org`, `per` sont stockées comme **chaînes de caractères** dans le CSV :

```
"['Politique', 'Santé']"  ← C'est une STRING, pas une liste Python !
```

**Solution** : On utilise `ast.literal_eval()` pour convertir en vraie liste :

```python
df['kws'] = df['kws'].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
```

### Caching avec `@lru_cache`

```python
@lru_cache(maxsize=1)
def load_data():
    ...
```

Cette décoration garde les données en mémoire. L'app ne relit pas le CSV à chaque requête.

---

## Les Visualisations Expliquées

### 1. Timeline (Évolution Temporelle)

**Fichier** : `visualizations.py` → `create_timeline()`

**Principe** :

1. Grouper les articles par jour : `df.groupby(df['date'].dt.date).size()`
2. Créer un graphique "Area" (aire remplie sous la courbe)
3. Ajouter un RangeSlider pour zoomer

**Code clé** :

```python
fig = px.area(daily_counts, x='date', y='count')
fig.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
```

**Utilité** : Identifier les pics d'activité (élections, crises, etc.)

---

### 2. Nuage de Mots-Clés (Word Cloud)

**Fichier** : `visualizations.py` → `create_wordcloud_scatter()`

**Principe** :

1. Compter la fréquence de chaque mot-clé
2. Assigner une taille proportionnelle à la fréquence
3. Placer les mots aléatoirement sur un graphique scatter

**Code clé** :

```python
sizes = min_size + (kw_counts / max_count) * (max_size - min_size)
fig.add_trace(go.Scatter(mode='text', text=[word], textfont=dict(size=size)))
```

**Astuce** : On utilise `random.seed(42)` pour avoir le même placement à chaque refresh.

---

### 3. Top Personnalités / Lieux (Bar Charts Horizontaux)

**Fichiers** : `create_top_persons_bar()`, `create_top_locations_bar()`

**Principe** :

1. "Exploser" les listes : `df['per'].explode()` transforme `['A', 'B']` en 2 lignes
2. Compter : `value_counts().head(20)`
3. Trier en ascendant pour que le plus grand soit en haut

**Code clé** :

```python
all_persons = df['per'].explode().dropna()
top_persons = all_persons.value_counts().head(20)
fig = px.bar(top_persons, orientation='h')
```

---

### 4. Sunburst (Hiérarchie Lieux → Organisations)

**Fichier** : `visualizations.py` → `create_sunburst()`

**Principe** :

1. Pour chaque article, créer des paires (Lieu, Organisation)
2. Ex: Article avec `loc=['Paris']` et `org=['ONU', 'UE']` → paires `(Paris, ONU)` et `(Paris, UE)`
3. Compter les paires
4. Créer un Sunburst avec 3 niveaux : Monde → Lieu → Organisation

**Code clé** :

```python
for l in locs:
    for o in orgs:
        pairs.append({'World': 'Monde', 'Location': l, 'Organization': o})

fig = px.sunburst(grouped, path=['World', 'Location', 'Organization'], values='count')
```

**Lecture** : Le centre = "Monde", cliquer sur un lieu montre les organisations associées.

---

### 5. Heatmap de Co-occurrence

**Fichier** : `visualizations.py` → `create_cooccurrence_heatmap()`

**Principe de la Co-occurrence** :
_"Quels mots-clés apparaissent souvent ensemble ?"_

1. Pour chaque article, prendre les paires de mots-clés
2. Ex: `['Politique', 'Économie', 'France']` → paires : (Politique, Économie), (Politique, France), (Économie, France)
3. Compter combien de fois chaque paire apparaît
4. Créer une matrice symétrique

**Code clé** :

```python
cooc_mat = pd.DataFrame(0, index=all_entities, columns=all_entities)
for doc in filtered_docs:
    for i in range(len(doc)):
        for j in range(i + 1, len(doc)):
            cooc_mat.loc[doc[i], doc[j]] += 1
            cooc_mat.loc[doc[j], doc[i]] += 1  # Symétrie
```

**Lecture de la Heatmap** :

- Couleur intense = forte corrélation
- Diagonale vide (un mot ne co-occur pas avec lui-même)

---

## Système de Filtrage

### Comment ça marche

```
Utilisateur sélectionne "Politique" dans le dropdown
         │
         ▼
Dash détecte le changement (Input)
         │
         ▼
Callback `update_all_charts()` s'exécute
         │
         ▼
`filter_data()` filtre le DataFrame
         │
         ▼
Tous les graphiques sont recréés avec les données filtrées
         │
         ▼
Interface mise à jour (Outputs)
```

### Logique de Filtrage

```python
def filter_data(df, start_date, end_date, keywords, locations):
    # Filtre par date
    dff = dff[(dff['date'] >= start_date) & (dff['date'] <= end_date)]

    # Filtre par mot-clé (OR logic : si AU MOINS un match)
    if keywords:
        kws_set = set(keywords)
        dff = dff[dff['kws'].apply(lambda x: not kws_set.isdisjoint(x))]
```

**Explication `isdisjoint`** :

- `{A, B}.isdisjoint({C, D})` = True (aucun élément en commun)
- `{A, B}.isdisjoint({A, C})` = False (A est en commun)
- On utilise `not isdisjoint` pour garder les articles avec au moins un match

---

## Design et CSS

### Thème CYBORG

Bootstrap theme sombre avec couleurs cyan/vert.

### Glassmorphism

Effet "verre dépoli" :

```css
.glass-card {
  background: rgba(20, 20, 20, 0.4);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

### Gradient Background

```css
body {
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}
```

### Couleurs principales

- `#00bc8c` : Cyan/Teal (accent principal)
- `#007bff` : Bleu (gradients)
- `#e0e0e0` : Gris clair (texte)

---

## Comment Lancer le Projet

### Installation

```bash
cd Projet_Dashboard_Media
pip install -r requirements.txt
```

### Lancement

```bash
python app.py
```

### Accès

Ouvrir `http://127.0.0.1:8050` dans un navigateur.

---

## Résumé pour la Présentation

> "Ce projet est une application Dash/Plotly qui analyse 30 000 articles de presse. L'architecture sépare les données (`data_processing`), les visualisations (`visualizations`), l'interface (`layout`) et l'interactivité (`callbacks`). Les données passent par un pipeline de parsing (listes stringifiées → vraies listes Python), puis sont filtrées dynamiquement via des callbacks réactifs. Les visualisations incluent une timeline temporelle, des bar charts de ranking, un sunburst hiérarchique pour explorer les relations Lieux-Organisations, et une heatmap de co-occurrence pour identifier les corrélations entre mots-clés. Le tout dans un design Dark Mode professionnel avec effets glassmorphism."
