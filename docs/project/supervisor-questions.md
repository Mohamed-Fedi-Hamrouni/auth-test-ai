# Questions pour l’encadrant

## Décisions closes le 21 juillet 2026

L’encadrant a délégué la sélection technique à l’équipe. Flask, PostgreSQL 17, SQLAlchemy 2/Flask-SQLAlchemy, Flask-Migrate, session serveur PostgreSQL par cookie opaque, Argon2id, rôles USER/ADMIN, verrouillage 5 échecs/15 minutes et session 30 minutes/8 heures sont retenus. Les questions correspondantes ci-dessous sont archivées comme résolues et ne bloquent plus l’implémentation.

## Critical before implementation

| Question | Impact projet |
|---|---|
| Quelle est la durée exacte du stage et quelles sont les dates de début/fin ? | Fixe capacité, jalons et profondeur des bonus. |
| Quel niveau d’administration est attendu ? | Détermine création, liste, activation, audit, pagination et UI. |
| Quelles exigences de mot de passe (longueur, compromis, rotation) ? | Fixe validation, hash et tests négatifs. |
| Quelles exigences de performance et charge ? | Permet des objectifs mesurables et un environnement de référence. |
| Quels navigateurs/versions doivent être supportés ? | Définit matrice UI et CI. |
| Quel niveau de tests de sécurité est attendu ? | Cadre outils, autorisations et preuves acceptables. |
| Quels critères d’évaluation du stage et livrables/formats sont requis ? | Aligne priorités, preuves et soutenance. |

## Important before AI integration

| Question | Impact projet |
|---|---|
| Une API IA externe est-elle autorisée ? | Détermine si un provider distant peut exister. |
| Quelles contraintes de confidentialité KPIT s’appliquent ? | Fixe classification, redaction, localisation et rétention. |
| Un modèle local est-il possible ou préféré ? | Affecte infrastructure, performance et confidentialité. |
| Quelles données exactes sont autorisées dans les prompts ? | Définit allowlist et cas de blocage du redactor. |
| Quels fournisseur/modèle/budget sont autorisés ? | Stabilise adapter, quotas et reproductibilité. |
| Quelle preuve de validation humaine est attendue ? | Définit workflow et audit des sorties IA. |

## Optional improvements

| Question | Impact projet |
|---|---|
| Quelle plateforme CI est autorisée et GitHub Actions peut-il être utilisé ? | Valide ADR 0006 et gestion des secrets/artefacts. |
| Quelle fréquence de démonstrations et revues ? | Fixe cadence des incréments et feedback. |
| Le dépôt GitHub peut-il être présenté, et sous quelles règles de visibilité ? | Affecte démonstration, confidentialité et nettoyage. |
| Prometheus/Grafana sont-ils attendus ou bonus ? | Empêche l’observabilité de déplacer le MVP test. |
| Faut-il tester plusieurs OS/browsers ou l’exécution parallèle ? | Dimensionne CI et isolation. |
| Quelle rétention pour audits, captures et rapports ? | Fixe coûts, confidentialité et suppression. |
