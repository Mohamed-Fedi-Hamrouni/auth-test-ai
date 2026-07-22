# ADR 0002 — Angular, Flask et PostgreSQL

- Statut : Accepted — implementation authorized by the supervisor
- Date : 2026-07-21

## Contexte
Le sujet nécessite une application web, une API testable et une persistance réaliste. L’encadrant a délégué la sélection technique à l’équipe projet.

## Options étudiées
Angular + Flask + PostgreSQL; Angular + Flask + SQLite; framework full-stack unique.

## Décision
Retenir Angular standalone, une application factory Flask, Flask-SQLAlchemy avec SQLAlchemy 2, Flask-Migrate/Alembic et PostgreSQL 17, séparés dans le monorepo.

## Justification
Séparation claire, écosystèmes de test demandés et contraintes SQL réalistes; PostgreSQL permet concurrence/contraintes plus représentatives que SQLite.

## Conséquences positives
Contrats nets, tests Pytest/Robot, parité locale/CI possible.

## Conséquences négatives
Deux toolchains, CORS/CSRF et service DB à administrer.

## Risques
Divergence d’environnements et administration de PostgreSQL local/CI.

## Critères de réévaluation
Exigence technologique officielle, contraintes d’hébergement, calendrier ou incompatibilité pédagogique.
