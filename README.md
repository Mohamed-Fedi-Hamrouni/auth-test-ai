# AuthTest AI

AuthTest AI est une application web d'authentification sécurisée dont la valeur
principale est une stratégie de test automatisée complète. Pytest vérifie la
logique backend et Robot Framework couvrira les API, l'interface, la base de
données, la sécurité et la régression. L'IA restera une aide complémentaire,
soumise à anonymisation et validation humaine.

## Architecture

- `frontend/` : application Angular standalone avec routing et SCSS ;
- `backend/` : API Flask, SQLAlchemy 2, migrations Alembic et sessions PostgreSQL ;
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
AUTH_TEST_AI_ENV=development flask --app auth_test_ai:create_app run
```

L'endpoint `GET http://localhost:5000/api/health` retourne
`{"status":"ok"}`.

## Documentation API

En développement et en test, Swagger UI est disponible sur
`http://localhost:5000/api/docs` et le contrat OpenAPI 3.1 canonique sur
`http://localhost:5000/api/openapi.yaml`. L'interface est un outil manuel de
démonstration, pas un remplacement des suites Pytest et Robot Framework. Elle
est servie par la même origine Flask et envoie les cookies avec les requêtes;
ses ressources Swagger UI sont toutefois chargées depuis jsDelivr à la version
figée `5.17.14`, donc l'affichage initial exige un accès réseau.

Le navigateur gère seul le cookie de session opaque `HttpOnly`. Pour une
mutation, appeler d'abord `GET /api/auth/csrf`, copier `csrfToken` dans
`X-CSRFToken`, puis exécuter la requête. Après un login réussi, la rotation de
session invalide le jeton anonyme : rappeler immédiatement l'endpoint CSRF et
utiliser le nouveau jeton pour logout et les mutations admin. Les GET sûrs
n'exigent pas ce header. La documentation est désactivée par défaut en
production et exige `API_DOCS_ENABLED=true` pour une activation explicite.

Préparer la base de test dédiée et appliquer les migrations :

```bash
make test-db-prepare
AUTH_TEST_AI_ENV=testing make db-upgrade
make test-backend-unit
make test-backend-integration
```

`TEST_DATABASE_URL` doit cibler exclusivement `auth_test_ai_test`. Les tests d’intégration refusent une autre base. Le cookie navigateur est opaque et `HttpOnly`; les données de session restent dans PostgreSQL.

`AUTH_TEST_AI_ENV` est obligatoire (`development`, `testing` ou `production`). La production refuse les secrets publics/faibles et `memory://` pour le rate limiting; elle attend un stockage partagé compatible Flask-Limiter. Les corps JSON sont limités à 16 KiB.
La factory publique accepte uniquement ces trois noms (ou `None`, résolu par la variable); les classes et dictionnaires de configuration sont refusés. Avant toute extension, le mode test vérifie que `TEST_DATABASE_URL` est une URL PostgreSQL ciblant exactement `auth_test_ai_test`.

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

## Documentation

- [Architecture](docs/architecture.md)
- [Exigences fonctionnelles](docs/requirements/functional-requirements.md)
- [Exigences non fonctionnelles](docs/requirements/non-functional-requirements.md)
- [Cas d’utilisation](docs/design/use-cases.md)
- [Modèle de données](docs/design/data-model.md)
- [Contrat API](docs/design/api-contract.md)
- [OpenAPI 3.1](docs/openapi/auth-test-ai.openapi.yaml)
- [Démonstration Swagger](docs/demo/swagger-demo.md)
- [Threat model](docs/security/threat-model.md)
- [Stratégie de test](docs/testing/test-strategy.md)
- [Matrice de traçabilité](docs/testing/traceability-matrix.md)
- [Backlog](docs/project/backlog.md)
- [Questions pour l’encadrant](docs/project/supervisor-questions.md)
- ADR : [0001](docs/decisions/0001-monorepo.md), [0002](docs/decisions/0002-angular-flask-postgresql.md), [0003](docs/decisions/0003-authentication-session-strategy.md), [0004](docs/decisions/0004-robot-framework.md), [0005](docs/decisions/0005-ai-human-in-the-loop.md), [0006](docs/decisions/0006-github-actions.md)
