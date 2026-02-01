# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

### Étape 1 — Lancer l’API FastAPI

L’API simulant l’application doit être lancée localement avant d’exécuter le pipeline. Ne pas oublier d'installer les dépendances au préalable.

```bash
cd src/moovitamix_fastapi
python -m uvicorn main:app --reload
```

Une fois le serveur démarré, l’API est accessible à l’adresse suivante :

http://127.0.0.1:8000/docs

Cette interface permet de visualiser et tester les endpoints suivants :
- /tracks
- /users
- /listen_history


### Étape 2 — Exécuter le pipeline de données

Le pipeline récupère les données depuis l’API et les stocke localement, par dataset et par date d’exécution (run_date).

Depuis la racine du projet :

```bash
python -m src.main
```

Le pipeline :
1. Récupère les données paginées pour chaque endpoint.
2.	Agrège les résultats.
3.	Écrit les datasets localement dans la structure suivante :
```
data/
└── raw/
    ├── listen_history/
    │   └── run_date=YYYY-MM-DD/
    │       └── listen_history.json
    ├── tracks/
    │   └── run_date=YYYY-MM-DD/
    │       └── tracks.json
    └── users/
        └── run_date=YYYY-MM-DD/
            └── users.json
```

J'ai choisi de sauvegarder les données telles quelles en format .json localement dans le cadre de ce travail. Cependant, les prochaines étapes auraient normalement été de:
 - Charger ces données
 - Valider avec des schémas (BaseModel)
 - Transformer en DataFrames pandas pour la manipuler de données
 - Sauvegarder dans la base de données choisie

Afin de réaliser cette tâche de façon automatisée quotidiennement, il faudrait mettre en place un scheduler qui pourrait déclencher l'exécution du pipeline à une fréquence définie (ex: cron job). On pourrait aussi utiliser une Azure Function entre autres.

### Étape 3 — Exécuter les test unitaires

Les tests unitaires couvrent :
	•	la récupération et la pagination des données (APIDataFetcher)
	•	le stockage local (LocalSaver)
	•	les classes de sortie fournies dans le projet

Commande à faire à partir de la racine du projet: 

```bash
python -m pytest
```

## Questions (étapes 4 à 7)

### Étape 4

Afin de stocker les informations des 3 sources de données, j'opterais pour une solution relationnelle normalisée. Je ferais 8 tables différentes afin d'avoir une normalisation totale. Tout d'abord, les users peuvent avoir plusieurs styles musicaux favoris

### Table: `users`
Stocke les informations d'identité des utilisateurs.
- id : INT (PK)
- first_name : VARCHAR
- last_name : VARCHAR
- email : VARCHAR
- gender : VARCHAR 
- created_at : TIMESTAMP
- updated_AT: TIMESTAMP

### Table: `tracks`
Contient les métadonnées de chaque morceau de musique.
- id : INT (PK)
- name : VARCHAR
- artist : VARCHAR
- album : VARCHAR
- duration_sec : INT 
- created_at : TIMESTAMP
- updated_AT: TIMESTAMP

### Table: `listen_history`
Historique chronologique des écoutes (Lien Users -> Tracks).
- id : INT (PK)
- user_id : INT (FK)
- track_id : INT (FK)
- listened_at: TIMESTAMP

### Table: `track_genres`
Permet d'associer plusieurs genres à une piste (Lien Tracks -> Genres).
- track_id : INT (PK, FK) de (tracks.id)
- genre_id : INT (PK, FK) de (genres.id)

### Table: `genres`
Table de référence pour les styles musicaux.
- id : INT (PK)
- name : VARCHAR

### Table: `user_favorite_genres`
Gère les préférences musicales multiples des utilisateurs (Lien Users --> Genres).
- user_id : INT (PK, FK) de (users.id)
- genre_id : INT (PK, FK) de (genres.id)

### Table: `track_songwriters`
Permet d'associer plusieurs auteurs à une piste (Lien Tracks -> Songwriters).
- track_id : INT (PK, FK) de (tracks.id)
- songwriter_id : INT (PK, FK) de (songwriters.id)

### Table: `songwriters`
Table de référence pour les auteurs/compositeurs.
- id : INT (PK)
- full_name : VARCHAR

Pour ce faire, j'opterais pour POSTGRESQL, car il offre une gestion robuste des relations, les clés étrangères par exemple. L'utilisation d'une base de données relationnelles permet de garantir l'intégrité des données et éviter les doublons.


### Étape 5

Afin de suivre la santé du pipeline dans son exécution quotidienne, on génère des logs structurés montrant par exemple la date d'exécution, le moment du début et la fin du pipeline, le nombre d'éléments récupérés (tracks, users, listen_history). Les métriques clés de santé du pipeline seraient donc : 
- Le status de l'exécution (succès ou échec)
- Le volume de données pour chaque dataset
- La durée d'exécution 
- Les erreurs d'API : timeouts, erreurs réseau ou réponses non valides
- Une anomalie dans les données : dataset vide

Afin de visualer le tout, on pourrait générer des dashboards de monitoring afin d'observer visuellement toutes les métriques disponibles et valider la santé du système.

Finalement, pour la détection de problème quelconque, je mettrais en place des alertes Slack (ou autre plateforme) qui nous permettraient de recevoir une alerte s'il y a échec du pipeline, un dataset vide ou si la durée d'exécution dépasse un certain seuil.

### Étape 6

Pour automatiser le calcul des recommendations, on pourrait utiliser un script dont l'exécution est planifiée, à l'aide d'un cron job pour configurer l'exécution quotidienne. Ce script chargerait les données utilisateurs et leur historique d’écoute depuis la base de données, ainsi que le modèle de recommandation préalablement entraîné (par exemple un fichier .pkl). 

Le modèle serait ensuite utilisé pour générer des recommandations pour l’ensemble des utilisateurs. Les recommandations calculées seraient sauvegardées dans une base de données ou un data lake, de manière à être directement envoyées au bon endroit sans calcul en temps réel. 

Dans une version plus avancée, cette logique pourrait être orchestrée à l’aide d’un outil comme Apache Airflow, permettant de mieux gérer la planification, la surveillance, les dépendances entre tâches et la reprise automatique en cas d’échec. 

### Étape 7

Le réentraînement pourrait s'effectuer automatiquement à l'aide d'un batch planifié également. Son exécution aurait une fréquence adaptée au besoin du produit ou du client (que ce soit hebdomadaire ou mensuel par exemple). 

Le processus commencerait par aller chercher les données les plus récentes de la base de données (PostgreSQL dans notre hypothèse). On prépare les données, que ce soit du feature engineering ou du nettoyage. On prépare les ensembles d'entraînements et de validations afin de réentraîner le modèle. 

Le nouveau modèle serait ensuite évalué à l’aide de métriques comme la précision, le rappel ou autres métriques spécifiques au système de recommandation afin de vérifier qu’il offre de meilleures performances que la version actuellement en production. 

Si le résultat des métriques est satisfaisant, on sauvegarde le nouveau modèle en format .pkl par exemple, puis on le déploie afin qu'il soit utilisé pour les prochaines calculs de recommendations. Comme pour le calcul des recommandations, ce processus pourrait être orchestré à l’aide d’un outil comme Apache Airflow.
