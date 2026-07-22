# AuthTest AI backend

API Flask sécurisée utilisant PostgreSQL 17, Flask-SQLAlchemy/SQLAlchemy 2, Flask-Migrate, Flask-Session et Argon2id.

## Configuration

Les classes `DevelopmentConfig`, `TestingConfig` et `ProductionConfig` héritent de `BaseConfig`. La factory publique accepte uniquement `None`, `development`, `testing` ou `production`; classes et dictionnaires sont refusés. `None` exige `AUTH_TEST_AI_ENV`, sans repli implicite. Le développement HTTP local et les tests utilisent `SESSION_COOKIE_SECURE=false`. Avant d'initialiser les extensions, la production impose `Secure`, une URL `postgresql+psycopg` avec un nom de base, et un stockage de rate limit Redis partagé (`redis://` ou `rediss://`). Le déploiement doit fournir ce service et le client Python Redis compatible; aucun service Redis local n'est ajouté par ce projet.

La `SECRET_KEY` de production devrait être générée avec `python -c 'import secrets; print(secrets.token_urlsafe(32))'` dans un canal sûr. Sa longueur acceptée est comprise entre 32 et 256 caractères; cette borne supérieure limite aussi le coût de l'analyse. La validation rejette les placeholders publics et plusieurs formes courantes prévisibles (séquences, répétitions, valeurs numériques/hexadécimales); ces heuristiques ne prouvent pas mathématiquement l’entropie d’une valeur.

`DATABASE_URL` cible la base applicative. `TEST_DATABASE_URL` doit être PostgreSQL et cibler exactement `auth_test_ai_test`; la factory le vérifie avant SQLAlchemy, Flask-Session et toute connexion. La fixture répète ce contrôle avant tout nettoyage ciblé.

## Installation et exécution

```bash
make install-backend
make db-upgrade
cd backend
AUTH_TEST_AI_ENV=development ../.venv/bin/flask --app auth_test_ai:create_app run
```

## Sessions et CSRF

Flask-Session est borné à la série revue `>=0.8,<0.9` et conserve la session dans `server_sessions`. La version 0.8.x vérifie/crée cette table avec `checkfirst=True`; la migration Alembic reste la définition versionnée et le test de dérive compare types, tailles, nullabilité, clés et index PostgreSQL. Cette création automatique non destructive est acceptée jusqu’à ce que la bibliothèque fournisse un mode sans création, sans monkey patch local. Le cookie ne contient qu’un identifiant opaque, avec `HttpOnly`, `SameSite=Lax` et `Secure` en production, y compris lors de sa suppression. Les mutations utilisent un jeton synchronisé obtenu par `GET /api/auth/csrf` dans `X-CSRFToken`; sa durée de vie est celle de la session serveur. Une connexion réussie régénère le SID et invalide le jeton CSRF anonyme pré-login; le client doit en demander un nouveau. Les sessions expirent après 30 minutes d’inactivité ou 8 heures absolues. Les corps JSON sont limités à 16 KiB, les logins à 100 caractères et les mots de passe à 128.

## Migrations et tests

```bash
make test-db-prepare
AUTH_TEST_AI_ENV=testing make db-upgrade
make test-backend-unit
make test-backend-integration
make test-backend
```

Les tests d’intégration utilisent PostgreSQL réel et tronquent uniquement les tables de `auth_test_ai_test`. Ils ne suppriment aucun volume.

Le verrouillage concurrent repose sur une lecture `SELECT ... FOR UPDATE` et une transaction unique englobant compteur et audit. Le test déterministe compile la requête avec le dialecte PostgreSQL et vérifie `FOR UPDATE`; un test de contention réellement simultané reste à ajouter dans une suite de charge isolée, afin de ne pas introduire un test CI dépendant de l’ordonnancement des threads.

## Seed local

`flask seed-dev-users` crée idempotemment USER, ADMIN et cinq comptes synthétiques. Il refuse toujours la production et exige `ALLOW_DEV_SEED=true`. Chaque mot de passe provient d’une variable `SEED_*_PASSWORD`; si elle manque, seul son nom est affiché. `make db-seed` active explicitement ce garde-fou pour le développement.
