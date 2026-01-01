# 📊 Media Analytics Dashboard

Application analytique Dash/Plotly pour explorer un corpus de 30 000 articles de presse.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Dash](https://img.shields.io/badge/Dash-2.x-green)
![Plotly](https://img.shields.io/badge/Plotly-5.x-purple)

## 🎯 Fonctionnalités

- **Timeline interactive** : Évolution temporelle du volume d'articles
- **Nuage de mots-clés** : Visualisation des thèmes dominants
- **Top Personnalités & Lieux** : Rankings des entités les plus citées
- **Sunburst hiérarchique** : Exploration Lieux → Organisations
- **Heatmap de corrélation** : Co-occurrence des mots-clés
- **Module IA** : Interface prête pour intégration LLM

## 🚀 Installation

```bash
# Cloner le repository
git clone https://github.com/VOTRE_USERNAME/Media-Analytics-Dashboard.git
cd Media-Analytics-Dashboard

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

## ▶️ Lancement

```bash
python app.py
```

Ouvrir `http://127.0.0.1:8050` dans un navigateur.

## 📁 Structure du Projet

```
├── app.py                 # Point d'entrée
├── requirements.txt       # Dépendances
├── src/
│   ├── data_processing.py # Chargement et filtrage
│   ├── visualizations.py  # Fonctions de graphiques
│   ├── layout.py          # Interface utilisateur
│   └── callbacks.py       # Logique d'interactivité
├── assets/
│   └── custom_styles.css  # Design Dark Mode
└── data/processed/
    └── clean_data.csv     # Données nettoyées
```

## 🛠️ Technologies

- **Dash** : Framework web Python
- **Plotly** : Visualisations interactives
- **Pandas** : Manipulation de données
- **Bootstrap (CYBORG)** : Thème Dark Mode

## 📖 Documentation

Voir [DOCUMENTATION_COMPLETE.md](DOCUMENTATION_COMPLETE.md) pour le guide technique détaillé.

## 📝 Licence

MIT License
