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

Une fois l'installation et la configuration terminées, lancez le script principal depuis le dossier racine du projet :

```bash
python main.py
```

Le script va :
1.  Récupérer les matchs du jour.
2.  Analyser chaque match un par un.
3.  Afficher dans la console les "value bets" trouvés, avec le marché, le pari, la probabilité calculée par le modèle et la cote du bookmaker.

## Avertissement

-   Ce script est un outil d'analyse statistique et **ne garantit en aucun cas des gains**. Les paris sportifs comportent des risques.
-   La logique de récupération des données (statistiques, cotes) est basée sur une structure probable de l'API. Si le fournisseur de l'API modifie sa structure, des ajustements dans le code (notamment dans `src/model.py` et `src/value_finder.py`) pourraient être nécessaires.
