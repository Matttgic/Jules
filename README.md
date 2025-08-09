# Algorithme de Paris Sportifs sur le Football

Ce projet est un script Python qui recherche les meilleurs paris sportifs pour les matchs de football du jour en se basant sur un modèle statistique (Distribution de Poisson) pour identifier les "value bets".

## Fonctionnalités

- **Analyse Quotidienne** : Récupère automatiquement les matchs de football du jour.
- **Modèle Statistique (Poisson)** : Calcule la probabilité de chaque score possible pour un match.
- **Calcul de Probabilités** : Détermine les probabilités pour les marchés de paris populaires :
    - Résultat du Match (1X2)
    - Plus/Moins de 2.5 Buts (Over/Under 2.5)
    - Les Deux Équipes Marquent (BTTS)
- **Identification de "Value Bets"** : Compare les probabilités du modèle avec les cotes des bookmakers pour trouver des paris où les chances de gagner sont potentiellement sous-estimées.

## Installation

1.  **Clonez le projet** (si vous l'utilisez via git) ou téléchargez les fichiers dans un dossier.

2.  **Créez un environnement virtuel** (recommandé) :
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows: venv\Scripts\activate
    ```

3.  **Installez les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Le script a besoin d'une clé API pour accéder aux données des matchs et des cotes via RapidAPI.

1.  **Obtenez votre clé API** :
    -   Abonnez-vous à l'API [API-Football sur RapidAPI](https://rapidapi.com/api-sports/api/api-football).
    -   Allez dans la section "Endpoints" et vous trouverez votre clé `X-RapidAPI-Key` dans les exemples de code.

2.  **Créez le fichier de configuration** :
    -   Dans le dossier racine du projet, créez un fichier nommé `.env`.
    -   Ouvrez ce fichier et ajoutez votre clé API comme suit :
    ```
    API_KEY=votre_cle_api_ici_123456789
    ```
    -   Remplacez `votre_cle_api_ici_123456789` par votre véritable clé RapidAPI.

## Utilisation

Ce projet a deux modes d'utilisation : un script de collecte de données et une application web pour visualiser les résultats.

### 1. Collecte des Données

Le script `data_collector.py` est conçu pour être exécuté périodiquement (par exemple, une fois par jour via une tâche planifiée) pour peupler la base de données.

```bash
python data_collector.py
```

### 2. Application Web

L'application web, basée sur FastAPI, sert à visualiser les données collectées.

#### Lancer localement

1.  Assurez-vous d'avoir installé les dépendances (`pip install -r requirements.txt`).
2.  Lancez le serveur de développement Uvicorn depuis le dossier racine :
    ```bash
    uvicorn webapp.main:app --reload
    ```
3.  Ouvrez votre navigateur et allez à l'adresse `http://127.0.0.1:8000`.

#### Déploiement sur PythonAnywhere

1.  **Uploadez votre code** sur votre compte PythonAnywhere.
2.  **Configuration de l'Application Web** :
    -   Allez dans l'onglet "Web".
    -   Créez une nouvelle application web. Choisissez "Manual configuration" et la version de Python correspondante.
    -   Dans la section "Code", spécifiez le chemin vers votre fichier `wsgi.py`.
    -   Modifiez le fichier `wsgi.py` pour y mettre le chemin correct vers votre projet sur PythonAnywhere.
3.  **Variables d'Environnement** :
    -   Dans la configuration de l'application web, allez à la section "Environment variables".
    -   Ajoutez votre clé API : `API_KEY=votre_nouvelle_cle_securisee`.
4.  **Tâche Planifiée (Scheduled Task)** :
    -   Allez dans l'onglet "Tasks".
    -   Créez une nouvelle tâche pour exécuter le collecteur de données une fois par jour. La commande sera similaire à :
      ```bash
      python /home/YourUserName/path/to/your/project/data_collector.py
      ```
5.  **Rechargez l'application web** depuis l'onglet "Web" et visitez votre URL `votrenomdutilisateur.pythonanywhere.com`.

## Avertissement

-   Ce script est un outil d'analyse statistique et **ne garantit en aucun cas des gains**. Les paris sportifs comportent des risques.
-   La logique de récupération des données (statistiques, cotes) est basée sur une structure probable de l'API. Si le fournisseur de l'API modifie sa structure, des ajustements dans le code (notamment dans `src/model.py` et `src/value_finder.py`) pourraient être nécessaires.
