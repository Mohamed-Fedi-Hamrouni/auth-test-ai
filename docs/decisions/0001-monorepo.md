# ADR 0001 — Utiliser un monorepo

- Statut : accepté
- Date : 2026-07-16

## Contexte

Le projet réunit une application Angular, une API Flask, plusieurs catégories
de tests Robot Framework, des outils d'analyse et la configuration locale.

## Décision

Tous les composants sont versionnés dans un monorepo avec des répertoires aux
responsabilités explicites.

## Conséquences

Une modification fonctionnelle et ses tests peuvent être relus dans un même
diff. Les commandes racine homogénéisent les validations. Chaque composant doit
cependant conserver des dépendances et une configuration clairement isolées.

