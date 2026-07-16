# AuthTest AI

AuthTest AI est une application web d'authentification sécurisée dont la valeur
principale est une stratégie de test automatisée complète. Pytest vérifie la
logique backend et Robot Framework couvrira les API, l'interface, la base de
données, la sécurité et la régression. L'IA restera une aide complémentaire,
soumise à anonymisation et validation humaine.

## Architecture

- `frontend/` : application Angular standalone avec routing et SCSS ;
- `backend/` : API Flask installable, structurée avec une application factory ;
- `robot-tests/` : suites transverses Robot Framework ;
- `ai-testing/` : future analyse anonymisée des résultats Robot ;
- `docs/` : architecture et décisions ;
- `infra/` : future observabilité et infrastructure.

## Prérequis

- Python 3.11 ou supérieur et pip ;
- Node.js 20.19 ou supérieur et npm ;
- Docker avec le plugin Docker Compose ;
- un navigateur Chromium pour les tests Angular et les futurs tests UI.

## Installation

```bash
cp .env.example .env
make setup-backend
make setup-frontend
```

Le mot de passe d'exemple est exclusivement destiné au développement local.
Choisir une valeur locale dans `.env`, qui est ignoré par Git.

## PostgreSQL

```bash
make db-up
docker compose ps
make db-logs
```

Arrêter le service sans supprimer le volume nommé avec `make db-down`.

## Backend

```bash
cd backend
flask --app auth_test_ai:create_app run
```

L'endpoint `GET http://localhost:5000/api/health` retourne
`{"status":"ok"}`.

## Frontend

```bash
cd frontend
npm start
```

Le serveur de développement Angular écoute par défaut sur
`http://localhost:4200`.

## Validations

```bash
make lint-backend
make test-backend
make test-frontend
make build-frontend
```

Le smoke test Robot peut être exécuté après installation de ses dépendances :

```bash
python3 -m pip install -r robot-tests/requirements.txt
robot robot-tests/smoke
```

## Sécurité des secrets

Ne jamais versionner de mot de passe réel, JWT, cookie, jeton CSRF ou clé API.
Les données envoyées à une future IA externe devront être anonymisées, et ces
appels resteront désactivés par défaut dans la CI.
