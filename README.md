# Municipal Asset Management System

Plateforme de gestion des actifs municipaux géolocalisés (bornes d'incendie, bâtiments, segments de rue) : cartographie, inspections et interventions terrain pour les équipes techniques d'une municipalité.

## Contexte

Une municipalité dispose de plusieurs sources de données géographiques mais d'aucun outil centralisé permettant de localiser ses actifs, suivre leur état, planifier les inspections, ouvrir des interventions et analyser les infrastructures voisines. Ce projet construit ce système de bout en bout : de l'ingestion des données brutes jusqu'à une API géospatiale exploitable par une application cartographique.

## Stack technique

**Backend**
- Django 5 + Django REST Framework
- GeoDjango (modèles et requêtes spatiales)
- PostgreSQL + PostGIS

**Frontend** (à venir)
- React + Leaflet

**Infrastructure**
- Docker / Docker Compose
- GitHub Actions (CI/CD, à venir)

## Architecture

Le backend est organisé en apps Django par domaine fonctionnel :

| App | Rôle |
|---|---|
| `accounts` | Comptes utilisateurs et permissions |
| `assets` | Actifs géospatiaux (bornes, bâtiments, segments de rue) et leur pipeline d'import |
| `inspections` | Contrôles terrain (à venir) |
| `interventions` | Travaux et anomalies (à venir) |
| `common` | Utilitaires transverses (gestion d'erreurs API, etc.) |

## Démarrage local

Prérequis : Docker et Docker Compose.

```bash
docker compose up -d db
docker compose build backend
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py createsuperuser
docker compose up -d backend
```

L'API est alors accessible sur `http://localhost:8000/`, l'admin Django sur `http://localhost:8000/admin/`.

## Données

Les jeux de données bruts (`data/raw/`) sont trois fichiers GeoJSON fournis par la municipalité : bornes d'incendie, bâtiments et segments de rue, en coordonnées WGS84 (EPSG:4326).

Ces données contiennent des problèmes de qualité réels et volontairement conservés tels quels pour être traités par le pipeline plutôt que masqués : identifiants de bornes dupliqués, dates d'entretien et pressions manquantes, bâtiments sans nom, et une différence de couverture géographique entre les bornes et les deux autres jeux de données.

Le pipeline d'import (`assets/import_pipeline/`) lit, valide, transforme et charge ces données en base via la commande :

```bash
docker compose run --rm backend python manage.py importer_donnees
```

Les lignes rejetées sont écrites dans `data/rejected/` (en GeoJSON, avec le motif de rejet inclus dans les propriétés de chaque entité) plutôt que simplement supprimées, et un rapport résume le nombre de lignes chargées, rejetées et les valeurs manquantes par champ.

## API

Endpoints actuellement disponibles, tous paginés (50 résultats par page) et retournant du GeoJSON pour les géométries :

| Endpoint | Méthodes | Filtres |
|---|---|---|
| `/api/bornes/` | GET, POST, PATCH | `identifiant_source`, `municipalite`, `entretien_manquant`, `pression_min`, `pression_max` |
| `/api/batiments/` | GET | `usage`, `adresse` |
| `/api/segments-rue/` | GET | `nom`, `limite_vitesse`, `statut`, `autobus_autorise` |
| `/api/health/` | GET | — |

Recherche texte (`?search=`) et tri (`?ordering=`) disponibles sur chaque endpoint de liste. Les erreurs suivent un format normalisé : `{"code": ..., "message": ...}`.

## Statut du projet

Fonctionnel à ce stade : bootstrap Django/GeoDjango/PostGIS, modèles spatiaux, pipeline d'import des trois jeux de données, API REST des actifs.

En cours : authentification et permissions par rôle (administrateur, gestionnaire, inspecteur, lecteur).

À venir : recherches géospatiales avancées (proximité, zones), inspections, interventions, interface cartographique React/Leaflet, tests automatisés, déploiement.
