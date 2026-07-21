# ADR 0003 — Stratégie de session d’authentification

- Statut : proposé — validation encadrant requise
- Date : 2026-07-21

## Contexte
Angular appelle Flask; le navigateur ne doit pas exposer les tokens au JavaScript et logout/expiration/CSRF doivent être testables.

## Options étudiées
1. JWT dans `localStorage` : simple pour API mais accessible en XSS, révocation difficile; rejeté.
2. JWT dans cookie HttpOnly : réduit exposition JavaScript, reste stateless partiel mais exige CSRF, rotation et blocklist/logout.
3. Session serveur avec identifiant opaque en cookie HttpOnly : révocation/logout directs et tests simples, au prix d’un stockage serveur et de l’état distribué.

## Décision
Privilégier une **session serveur avec cookie opaque HttpOnly, Secure en HTTPS et SameSite**, plus protection CSRF des mutations. Si une contrainte impose JWT, utiliser uniquement un cookie HttpOnly avec durée courte et blocklist; jamais Web Storage.

## Justification
Solution cohérente avec une application web Flask/Angular, le logout effectif, la désactivation et une stratégie de test déterministe.

## Conséquences positives
Secret inaccessible au JS, révocation maîtrisée, contrôle central.

## Conséquences négatives
Stockage/cleanup session, CSRF, scalabilité à planifier.

## Risques
Mauvaise configuration cookie/proxy, fixation de session, indisponibilité du store.

## Critères de réévaluation
Architecture multi-clients, besoins stateless, hébergement distribué, décision encadrant ou résultats du threat model.
