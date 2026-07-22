# Threat model — STRIDE simplifié

Périmètre : navigateur Angular, API Flask, PostgreSQL, outillage de test/CI et future couche IA. Risques qualitatifs proposés, à réévaluer après choix de déploiement. Propriétaires : Backend (BE), Frontend (FE), Test/Security Engineer (TSE), DevOps (DO), AI owner (AI), Supervisor (SUP).

| Threat ID | STRIDE | Actif; scénario | Impact | Prob. / risque | Réduction | Requirement IDs | Security Test IDs | Résiduel | Propriétaire |
|---|---|---|---|---|---|---|---|---|---|
| THR-001 | Tampering/Elevation | DB; injection SQL via login/filtres | Compromission données/droits | M / High | ORM/requêtes paramétrées, validation, moindre privilège | NFR-SEC-001, FR-AUTH-005 | SEC-SQL-001 | Low | BE |
| THR-002 | Denial | Auth; brute force ciblée ou corps/identifiants surdimensionnés | Compte compromis/indisponible | H / High | Flask-Limiter avec stockage partagé obligatoire en production, corps 16 KiB, login 100, password 128, verrou PostgreSQL, seuil 5 et verrouillage 15 minutes | FR-AUTH-014/015 | SEC-AUTH-006 | Medium | BE/TSE |
| THR-003 | Spoofing | Comptes; credential stuffing | Prise de compte | H / High | Rate limit, hash robuste, détection; MFA futur | FR-AUTH-005/014 | SEC-AUTH-009 | Medium | BE/SUP |
| THR-004 | Information disclosure | Auth; messages/temps révèlent existence | Énumération utilisateurs | H / High | Réponse générique et exactement une vérification Argon2id; hash factice pré-calculé pour les chemins non vérifiables | FR-AUTH-006/007/013 | SEC-AUTH-001/002/005 | Low-Med | BE |
| THR-005 | Spoofing/Disclosure | Cookie/session volé | Usurpation | M / High | Identifiant opaque, session PostgreSQL, HttpOnly/Secure/SameSite=Lax, 30 minutes inactive/8 heures absolues, rotation au login | FR-AUTH-010/016, NFR-SEC-001 | SEC-SESSION-001 | Medium | BE/DO |
| THR-006 | Spoofing | Token expiré accepté | Accès indu | M / High | Vérifier `exp` serveur et horloge | FR-AUTH-016 | SEC-AUTH-007 | Low | BE |
| THR-007 | Tampering | Token modifié accepté | Usurpation/élévation | M / Critical | Signature/algorithmes allowlist, clés protégées | FR-AUTH-017 | SEC-AUTH-008 | Low | BE/DO |
| THR-008 | Elevation | Rôle/ID manipulé | Administration non autorisée | M / Critical | RBAC serveur, deny by default, tests horizontaux/verticaux | FR-ADMIN-006 | SEC-ADMIN-003 | Low | BE |
| THR-009 | Elevation | URL privée appelée directement | Fuite/action non autorisée | H / High | Auth/authz sur chaque endpoint; garde UI seulement UX | FR-AUTH-011 | SEC-AUTH-004 | Low | BE/FE |
| THR-010 | Tampering | CSRF sur login/logout/admin | Action au nom victime | M / High | SameSite=Lax + jeton synchronisé comparé en temps constant via `X-CSRFToken` | FR-AUTH-005/010, FR-ADMIN-002..004 | SEC-CSRF-001/002 | Low | BE/FE |
| THR-011 | Tampering/Disclosure | XSS via noms/logins/rapports | Vol session/action | M / High | Échappement Angular, CSP future, pas HTML non fiable | FR-AUTH-009, NFR-SEC-001 | SEC-XSS-001 | Low-Med | FE/BE |
| THR-012 | Disclosure | Configuration expose secrets ou démarre en mode développement | Compromission systèmes | M / Critical | Factory limitée à trois environnements, `AUTH_TEST_AI_ENV` explicite, production fail-closed, rejet heuristique des placeholders/séquences/répétitions, génération aléatoire et rotation | NFR-SECRET-001 | SEC-SECRET-001 | Low | DO |
| THR-013 | Disclosure | Secrets commités dans Git | Secret durable dans historique | M / Critical | `.gitignore`, scan pre-commit/CI futur, rotation | NFR-SECRET-001 | SEC-SECRET-002 | Low | DO/TSE |
| THR-014 | Disclosure | Password dans logs | Compromission compte | M / Critical | Allowlist de champs, filtres/redaction, tests capture logs | FR-AUDIT-001/002, NFR-SECRET-001 | SEC-LOG-001 | Low | BE |
| THR-015 | Disclosure | JWT/cookie/CSRF dans logs | Usurpation | M / Critical | Ne pas logger headers/cookies; redaction centralisée | NFR-SECRET-001 | SEC-LOG-002 | Low | BE/DO |
| THR-016 | Disclosure | Rapport/capture contient PII/secrets | Fuite artefact | M / High | Masquage, capture minimale, ACL/rétention | NFR-REPORT-001, NFR-PRIV-001 | SEC-REPORT-001 | Low-Med | TSE/DO |
| THR-017 | Tampering/Elevation | Dépendance vulnérable | Exécution/fuite | M / High | Audit, lockfiles, revue compatibilité, mises à jour contrôlées | NFR-SEC-001, NFR-REPRO-001 | SEC-DEP-001 | Medium | DO |
| THR-018 | Disclosure | Données sensibles envoyées à IA | Fuite externe/non-conformité | M / Critical | IA off par défaut, redaction locale, allowlist, accord | FR-AI-001/002, NFR-AI-001 | SEC-AI-001 | Low-Med | AI/SUP |
| THR-019 | Tampering | Prompt injection dans logs | Analyse/recommandation manipulée | H / High | Traiter logs comme données, délimiter, filtrer, pas d’outils/actions | FR-AI-002/004 | SEC-AI-002 | Medium | AI/TSE |
| THR-020 | Repudiation/Tampering | Mauvaise recommandation IA suivie | Défaut/régression | H / High | Preuves, confiance, revue humaine, aucune exécution | FR-AI-004/005 | SEC-AI-003 | Medium | TSE |
| THR-021 | Tampering | Scénario IA incorrect officialisé | Faux niveau de confiance | H / High | Brouillon isolé, revue/code review, tests déterministes | FR-AI-001/005 | SEC-AI-004 | Medium | TSE |
| THR-022 | Denial | Fournisseur IA indisponible | Analyse absente | H / Low | Optionnel, timeout/circuit breaker futur, suites indépendantes | FR-AI-002/006 | SEC-AI-005 | Low | AI |
| THR-023 | Repudiation | Flaky test classé défaut produit | Mauvais diagnostic | M / Medium | Historique, rerun diagnostique non masquant, catégorie flaky suspectée | FR-AI-003/006, NFR-REL-001 | SEC-AI-006 | Low-Med | TSE |

## Frontières de confiance

Internet↔Angular, Angular↔Flask, Flask↔PostgreSQL, CI↔secrets/artefacts et AI testing↔provider externe sont des frontières. Toute traversée impose authentification appropriée, validation, chiffrement en transit et minimisation. Les logs et résultats Robot sont des entrées non fiables.

## Vulnérabilités npm modérées observées

L’état de semaine 1 signale **quatre vulnérabilités modérées** dans l’outillage Angular. Elles concernent actuellement des dépendances transitives de développement, pas une dépendance runtime déclarée comme directement exploitable dans l’application livrée. Cette qualification doit être reconfirmée avec `npm audit` et l’arbre de dépendances au moment du traitement.

Aucune correction forcée (`npm audit fix --force`) ne doit être appliquée sans analyse de compatibilité Angular, portée dev/runtime, chemin d’exploitation et tests complets. Le propriétaire DevOps/TSE doit consigner versions, advisories, décision d’acceptation temporaire ou mise à niveau contrôlée. Risque résiduel : **Medium, à confirmer**.
