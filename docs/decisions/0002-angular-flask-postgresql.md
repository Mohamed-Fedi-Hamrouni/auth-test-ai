# ADR 0002 — Angular, Flask et PostgreSQL

- Statut : proposé
- Date : 2026-07-21

## Contexte
Le sujet nécessite une application web, une API testable et une persistance réaliste. L’obligation exacte de Flask/SQLite/PostgreSQL doit être confirmée.

## Options étudiées
Angular + Flask + PostgreSQL; Angular + Flask + SQLite; framework full-stack unique.

## Décision
Proposer Angular standalone, Flask application factory et PostgreSQL, séparés dans le monorepo. Cette décision n’est pas présentée comme imposée par KPIT.

## Justification
Séparation claire, écosystèmes de test demandés et contraintes SQL réalistes; PostgreSQL permet concurrence/contraintes plus représentatives que SQLite.

## Conséquences positives
Contrats nets, tests Pytest/Robot, parité locale/CI possible.

## Conséquences négatives
Deux toolchains, CORS/CSRF et service DB à administrer.

## Risques
Divergence d’environnements et refus de PostgreSQL par l’encadrant.

## Critères de réévaluation
Exigence technologique officielle, contraintes d’hébergement, calendrier ou incompatibilité pédagogique.
