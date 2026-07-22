# Démonstration superviseur — Swagger UI

Swagger UI est un outil manuel de démonstration, pas un remplacement des tests
Pytest ou Robot Framework. Les valeurs `SEED_*_PASSWORD` ci-dessous sont des
variables locales : ne jamais copier de mot de passe dans ce document, une
capture ou un rapport.

Cette procédure suppose le checkout complet du dépôt et l'installation backend
éditable (`make install-backend`). Elle fonctionne depuis le dépôt même si le
répertoire courant change. Un wheel autonome sans le répertoire `docs/` n'est
pas un mode de démonstration supporté, afin de conserver un seul contrat YAML
canonique.

## Préparation

1. Démarrer PostgreSQL sans supprimer son volume :

   ```bash
   make db-up
   docker compose ps
   ```

2. Préparer la base de développement et appliquer les migrations :

   ```bash
   AUTH_TEST_AI_ENV=development make db-upgrade
   ```

3. Définir localement des valeurs synthétiques fortes pour toutes les variables
   `SEED_ADMIN_PASSWORD`, `SEED_USER_ONE_PASSWORD`, `SEED_USER_TWO_PASSWORD`,
   `SEED_INACTIVE_PASSWORD` et `SEED_LOCKOUT_PASSWORD`, puis créer les comptes :

   ```bash
   AUTH_TEST_AI_ENV=development ALLOW_DEV_SEED=true make db-seed
   ```

4. Démarrer Flask avec la documentation explicitement activée :

   ```bash
   cd backend
   AUTH_TEST_AI_ENV=development API_DOCS_ENABLED=true ../.venv/bin/flask --app auth_test_ai:create_app run
   ```

5. Ouvrir `http://localhost:5000/api/docs`. Le chargement initial des assets
   Swagger UI `5.17.14` depuis jsDelivr exige un accès réseau. Le contrat et les
   appels API restent servis par Flask sur la même origine.

## Parcours USER

6. Exécuter `GET /api/health` : attendu `200` et `{"status":"ok"}`.
7. Exécuter `GET /api/auth/csrf` : attendu `200`. Copier le champ `csrfToken`.
8. Sur `POST /api/auth/login`, saisir ce jeton dans `X-CSRFToken`, puis un login
   USER synthétique et `${SEED_USER_ONE_PASSWORD}` dans le corps : attendu `200`.
9. Exécuter à nouveau `GET /api/auth/csrf` : attendu `200`. Le login a régénéré
   l'identifiant de session et l'ancien jeton anonyme est désormais invalide;
   copier le nouveau jeton authentifié.
10. Exécuter `GET /api/auth/me` : attendu `200` avec le rôle `USER`; aucun header
    CSRF n'est nécessaire.
11. Exécuter `GET /api/admin/users` : attendu `403` avec le code `FORBIDDEN`.

## Parcours ADMIN et logout

12. Exécuter `POST /api/auth/logout` avec le jeton authentifié : attendu `204`.
13. Reprendre `GET /api/auth/csrf`, puis `POST /api/auth/login` avec le login
    ADMIN synthétique et `${SEED_ADMIN_PASSWORD}` : attendus `200`, puis rappeler
    `GET /api/auth/csrf` pour obtenir le nouveau jeton authentifié.
14. Exécuter `GET /api/admin/users` : attendu `200` avec pagination et utilisateurs
    publics uniquement.
15. Exécuter `GET /api/admin/auth-attempts` : attendu `200`; aucune IP, cause
    interne ou donnée de session ne doit apparaître.
16. Exécuter `POST /api/auth/logout` avec le dernier `X-CSRFToken` : attendu `204`.
17. Exécuter `GET /api/auth/me` : attendu `401` avec `AUTH_REQUIRED`.

Le cookie `auth_test_ai_session` est opaque et `HttpOnly`. Le navigateur le
reçoit, l'envoie et le supprime automatiquement grâce aux credentials
same-origin. Il ne faut jamais le copier manuellement dans Swagger UI.
