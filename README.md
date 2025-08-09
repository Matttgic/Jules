# Algorithme de Paris Sportifs sur le Football

Ce projet est une application web qui recherche et affiche les meilleurs paris sportifs pour les matchs de football du jour, en se basant sur un modèle statistique (Distribution de Poisson) pour identifier les "value bets".

L'application est construite avec **Streamlit** et est conçue pour être déployée sur **Streamlit Cloud**. L'analyse des données est effectuée automatiquement chaque jour via **GitHub Actions**.

## Architecture

Ce projet utilise une architecture moderne en deux parties pour garantir une performance optimale :

1.  **Collecte de Données (via GitHub Actions)** :
    *   Un script (`data_collector.py`) s'exécute automatiquement une fois par jour.
    *   Il contacte l'API de paris sportifs, analyse les matchs, et identifie les "value bets".
    *   Il sauvegarde les résultats dans un fichier `results.json` directement dans ce dépôt Git.

2.  **Interface Utilisateur (via Streamlit Cloud)** :
    *   Une application Streamlit (`streamlit_app.py`) lit le fichier `results.json`.
    *   Elle affiche les résultats dans une interface web claire, rapide et interactive.
    *   L'application elle-même n'effectue aucun calcul lourd, ce qui la rend très rapide à charger.

## Déploiement (de A à Z)

Pour avoir votre propre version de cette application en ligne, suivez ces étapes.

### Étape 1 : Forker le Dépôt

Cliquez sur le bouton **"Fork"** en haut à droite de cette page pour créer votre propre copie de ce projet sur votre compte GitHub.

### Étape 2 : Configurer la Clé API (Secret GitHub)

L'action GitHub a besoin de votre clé API RapidAPI pour fonctionner. Vous devez la configurer comme un "secret" dans votre nouveau dépôt.

1.  Sur la page de **votre dépôt forké**, allez dans **"Settings"** (Paramètres).
2.  Dans le menu de gauche, allez à **"Secrets and variables"** > **"Actions"**.
3.  Cliquez sur le bouton **"New repository secret"**.
    *   **Name** : `API_KEY`
    *   **Secret** : Collez ici votre clé API RapidAPI.
4.  Cliquez sur **"Add secret"**.

### Étape 3 : Activer et Lancer le Workflow GitHub

1.  Allez dans l'onglet **"Actions"** de votre dépôt.
2.  Vous verrez un workflow nommé **"Daily Betting Analysis"**. Cliquez dessus.
3.  Il y aura un message vous demandant d'activer les workflows. Cliquez sur le bouton pour les activer.
4.  Pour peupler les données immédiatement sans attendre le prochain cycle, vous pouvez lancer le workflow manuellement.
    *   Sur la page du workflow, cliquez sur le menu déroulant **"Run workflow"**.
    *   Cliquez sur le bouton vert **"Run workflow"**.
    *   Attendez quelques minutes que l'exécution se termine (le point orange deviendra une coche verte).

### Étape 4 : Déployer sur Streamlit Cloud

1.  Allez sur [share.streamlit.io](https://share.streamlit.io) et connectez-vous avec votre compte GitHub.
2.  Cliquez sur **"New app"**.
3.  **Repository** : Choisissez votre dépôt forké.
4.  **Branch** : `main` (ou le nom de votre branche par défaut).
5.  **Main file path** : `streamlit_app.py`.
6.  Cliquez sur **"Deploy!"**.

Après quelques instants, votre application sera en ligne et accessible à tous !

## Avertissement

-   Ce script est un outil d'analyse statistique et **ne garantit en aucun cas des gains**. Les paris sportifs comportent des risques.
-   La logique de récupération des données est basée sur une structure probable de l'API. Si le fournisseur de l'API modifie sa structure, des ajustements dans le code pourraient être nécessaires.
