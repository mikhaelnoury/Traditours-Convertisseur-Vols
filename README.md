# 🛫 Convertisseur d'Itinéraires Aériens - Traditours

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-lightgrey.svg)](https://flask.palletsprojects.com/)

**Outil professionnel de conversion des données de vol en itinéraire client lisible**  
*Pour agents de voyages et compagnies aériennes*

## 🌟 Fonctionnalités Clés

### ✈️ Traitement des Données
- Analyse automatique des formats Amadeus et simplifiés
- Détection intelligente des compagnies aériennes et codes de vol
- Mappage automatique des codes IATA/ICAO (ex: YUL → Montréal-Trudeau)
- Conversion des dates/heures en format lisible (français/anglais)

### 📊 Génération d'Itinéraires
- Regroupement des vols par date et direction (aller/retour)
- Calcul automatique des décalages horaires
- Génération de PDF prêt pour l'impression
- Support des notes personnalisées et mentions spéciales

### 🖥 Interface Utilisateur
- Interface web moderne et responsive
- Prévisualisation en temps réel
- Gestion des configurations d'hébergement
- Compatibilité mobile/tablette

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.9+
- Pipenv (recommandé)

### Installation
git clone https://github.com/mikhaelnoury/Traditours-Convertisseur-Vols.git
cd Traditours-Convertisseur-Vols

# Configuration initiale
cp airlines.example.csv airlines.csv
cp airports.example.csv airports.csv

# Installation des dépendances
python -m pip install -r requirements.txt

Lancement
bash
flask run --host=0.0.0.0 --port=5000
Ouvrez http://localhost:5000 dans votre navigateur

📖 Formats Supportés
Entrée Amadeus
2 AC 311 K 07MAR 5 YULYVR HK1 1815 2047 07MAR E AC/3LGXCO

Entrée Simplifiée
QF 003 13OCT 3 SYDAKL 1010 1505 13OCT

Sortie Générée
Départ de Sydney (SYD) à 10h10 / 
Arrivée à Auckland (AKL) à 15h05 
(vol QF 003) le jeudi 13 octobre

🗂 Structure du Projet
.
├── app.py                 # Point d'entrée principal
├── data/
│   ├── airlines.csv       # Mappage codes compagnies aériennes
│   └── airports.csv       # Mappage codes aéroports
├── templates/             # Templates HTML
├── static/                # Assets (CSS/JS/images)
│   ├── css/
│   │   └── style.css      # Styles principaux
│   └── js/
│       └── app.js         # Logique front-end
├── requirements.txt       # Dépendances Python
└── README.md              # Documentation

🛠 Développement

Workflow Recommandé
# Création de l'environnement virtuel
python -m venv venv
source venv/bin/activate

# Installation des dépendances de développement
pip install -r requirements-dev.txt

# Exécution des tests
python -m pytest tests/

📄 Licence & Contact
Distribué sous licence MIT - Voir LICENSE pour plus de détails.

Développé avec ❤️ par Mikhaël Noury
📧 mikhael.noury@gmail.com
