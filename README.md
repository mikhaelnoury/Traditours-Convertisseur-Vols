# 🛫 Convertisseur d'Itinéraires Aériens - Traditours

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Deploy](https://github.com/mikhaelnoury/Traditours-Convertisseur-Vols/actions/workflows/deploy.yml/badge.svg)](https://github.com/mikhaelnoury/Traditours-Convertisseur-Vols/actions)

**Outil de conversion des données de vol en itinéraire client lisible**  
*Pour agents de voyages et professionnels du secteur aérien*

## 🌟 Fonctionnalités
- **Analyse automatique** des données de vol brutes
- Regroupement des vols par date de départ
- Affichage dynamique des compagnies aériennes détectées
- Mappage des codes aéroports (ex: YUL → Montréal)
- Formatage des dates/heures en français
- Interface responsive et conviviale
- Support multi-plateforme (web/mobile)

## 🚀 Installation
```bash
# Cloner le dépôt
git clone https://github.com/mikhaelnoury/Traditours-Convertisseur-Vols.git
cd Traditours-Convertisseur-Vols

# Préparer les fichiers de configuration
cp airlines.example.csv airlines.csv
cp airports.example.csv airports.csv

🛠 Utilisation
Format d'entrée
AC 818 19AUG 2 YULVCE 1940 0940 20AUG
AC 384 31AUG 7 ZAGFCO 0745 1030 31AUG

📂 Structure des Fichiers
├── app.py               - Script principal
├── templates/           - Fichiers HTML
├── static/              - CSS/JS
├── airlines.csv         - Mapping codes compagnies
├── airports.csv         - Mapping codes aéroports
└── requirements.txt     - Dépendances

## 📄 Licence
Distribué sous licence MIT. Voir LICENSE pour plus d'informations.

Développé avec ❤️ par Mikhaël Noury
Pour toute question : mikhael.noury@gmail.com