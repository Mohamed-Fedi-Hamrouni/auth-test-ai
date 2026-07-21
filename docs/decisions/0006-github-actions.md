# ADR 0006 — GitHub Actions pour la CI future

- Statut : proposé — plateforme à confirmer
- Date : 2026-07-21

## Contexte
Les validations doivent devenir reproductibles avec PostgreSQL et artefacts Robot, sans exposer de secrets.

## Options étudiées
GitHub Actions; CI KPIT interne; exécution locale documentée seule.

## Décision
Proposer GitHub Actions avec jobs lint/test/build, service PostgreSQL et publication contrôlée des rapports. Aucun appel IA externe par défaut.

## Justification
Intégration au dépôt et matrice de jobs accessible; ce choix n’est pas déclaré imposé par KPIT.

## Conséquences positives
Feedback automatique, preuves par commit, environnement déclaratif.

## Conséquences négatives
Quotas, maintenance YAML, gestion des artefacts/secrets.

## Risques
Plateforme non autorisée, dépendances compromises, rapports sensibles.

## Critères de réévaluation
Décision encadrant/KPIT, contraintes de souveraineté, coûts, besoins self-hosted ou autre forge.
