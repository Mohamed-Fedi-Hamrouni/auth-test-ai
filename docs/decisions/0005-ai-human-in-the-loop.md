# ADR 0005 — IA assistive avec validation humaine

- Statut : proposé
- Date : 2026-07-21

## Contexte
L’IA peut aider à rédiger/analyser mais ses sorties sont probabilistes et les preuves peuvent être sensibles.

## Options étudiées
Automatisation autonome; assistance distante avec revue; modèle local; absence d’IA.

## Décision
Couche optionnelle séparée, désactivée en CI par défaut, redaction avant appel et validation humaine obligatoire. Le verdict Robot original est immuable. Provider externe seulement après autorisation; modèle local reste option.

## Justification
Préserve déterminisme, confidentialité et responsabilité humaine.

## Conséquences positives
Assistance exploitable sans rendre le MVP dépendant d’un fournisseur.

## Conséquences négatives
Workflow de revue, métriques/limites et redactor à maintenir.

## Risques
Prompt injection, hallucination, fuite, biais, indisponibilité.

## Critères de réévaluation
Politique KPIT, qualité mesurée, incident de données, coût ou disponibilité d’un modèle local.
