# ADR 0004 — Robot Framework pour les tests transverses

- Statut : accepté pour la conception
- Date : 2026-07-21

## Contexte
Le livrable central exige des tests API, UI, DB, sécurité, smoke et régression avec rapports lisibles.

## Options étudiées
Robot Framework; Pytest seul; outils distincts Playwright/Postman/scripts.

## Décision
Robot Framework orchestre RequestsLibrary, SeleniumLibrary et DatabaseLibrary; Pytest conserve unitaires et intégration backend.

## Justification
Syntaxe lisible, tags communs et artefacts natifs `output.xml`, `log.html`, `report.html`.

## Conséquences positives
Traçabilité homogène, rapports partagés, réutilisation de ressources.

## Conséquences négatives
Couche keyword à maintenir et UI potentiellement flaky.

## Risques
Duplication avec Pytest, keywords trop abstraits, secrets dans rapports.

## Critères de réévaluation
Limites de navigateur, temps d’exécution, maintenabilité ou impossibilité de respecter sécurité des preuves.
