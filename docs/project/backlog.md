# Backlog semaines 2 à 8

Tous les items sont **Planned**. Les fonctions IA avancées sont Could après le MVP de test. Les critères chiffrés de politique restent soumis à validation.

| Epic / Story ID | Description; acteur | MoSCoW | Critères d’acceptation | Dépendances | Semaine | Risques |
|---|---|---|---|---|---|---|
| Authentication / US-AUTH-001 | Modèle User et accès PostgreSQL; Developer | Must | Migration réversible; login unique; hash seulement; tests contraintes | ADR 0002, modèle validé | 2 | Choix DB/politique password |
| Authentication / US-AUTH-002 | Login/logout/me sécurisé; User | Must | Contrat respecté, cookie sûr, erreurs génériques, tests unit/API | US-AUTH-001, ADR 0003 | 3 | Session/CSRF |
| Authentication / US-AUTH-003 | UI login/accueil/routes; User | Must | Validation accessible, Welcome exact, garde UX + contrôle API, UI tests | US-AUTH-002 | 3 | Flaky navigateur |
| Authentication / US-AUTH-004 | Verrouillage/expiration; User | Should | Horloge injectable, politique configurée, tests limites | Accord encadrant | 4 | Déni de service |
| Administration / US-ADMIN-001 | Lister/créer/activer/désactiver; Admin | Must | RBAC serveur, aucun hash, contrats et tests | Auth, rôles | 4 | Élévation/dernier admin |
| Administration / US-ADMIN-002 | Consulter rôles/tentatives; Admin | Should | Pagination/minimisation, 401/403, tests API/DB | Audit/RBAC | 4 | Confidentialité |
| Automated Testing / US-TEST-001 | Suite Pytest complète; Developer | Must | Unitaires/intégration auth, clock, erreurs, commandes documentées | Auth | 2-4 | Couverture insuffisante |
| Automated Testing / US-TEST-002 | Suites Robot API/DB; Test Engineer | Must | Tags, données isolées, effets DB et rapports | API stable | 4-5 | Couplage données |
| Automated Testing / US-TEST-003 | Suite UI; Test Engineer | Must | `data-testid`, attentes explicites, captures expurgées | UI stable | 5 | Flakiness |
| Automated Testing / US-TEST-004 | Smoke/régression/contrat; Test Engineer | Must | Sélection tags, artefacts cohérents, défauts tracés | Suites | 5 | Durée campagne |
| Security / US-SEC-001 | Cas négatifs STRIDE prioritaires; Security Engineer | Must | Injection, authz, CSRF, XSS, sessions testés sans destruction | Auth/admin | 5 | Faux sentiment sécurité |
| Security / US-SEC-002 | Redaction et scans secrets; DevOps/TSE | Must | Aucun secret dans logs/rapports; scan automatisé futur | Logging/CI | 5-6 | Faux positifs |
| AI-assisted Testing / US-AI-001 | Parser/redactor local; Test Engineer | Could | Parse copie output.xml, allowlist/redaction testée, zéro appel externe | Robot stable | 6 | Fuite données |
| AI-assisted Testing / US-AI-002 | Provider optionnel/analyse; AI Assistant | Could | Désactivé CI, timeout, classification/confiance, verdict immuable | Accord IA, US-AI-001 | 7 | Prompt injection/coût |
| AI-assisted Testing / US-AI-003 | Brouillons/revue humaine; Test Engineer | Could | Brouillon séparé, décision humaine tracée, jamais auto-intégré | US-AI-002 | 7 | Hallucination |
| CI/CD / US-CI-001 | Pipeline GitHub Actions; CI | Should | lint/tests/build, PostgreSQL service, cache sûr, aucun secret exposé | Accord plateforme | 6 | Quotas/versions |
| CI/CD / US-CI-002 | Artefacts et régression; CI | Should | Upload conditionnel, rétention/ACL validées, statut fidèle | US-CI-001 | 6 | Données sensibles |
| Observability / US-OBS-001 | Logs structurés/corrélation; Operator | Should | Événements utiles sans secrets, tests redaction | Auth/audit | 4 | PII logs |
| Observability / US-OBS-002 | Prometheus/Grafana minimal; Operator | Could | Métriques non sensibles, dashboard santé/erreurs | Accord infra | 8 | Scope/maintenance |
| Documentation / US-DOC-001 | Maintenir exigences/ADR/matrice; Team | Must | Toute évolution met à jour liens et validation documentaire | Continu | 2-8 | Désynchronisation |
| Documentation / US-DOC-002 | Guide exécution et preuves finales; Test Engineer | Must | Commandes réelles, résultats, limites et démonstration reproductible | Toutes suites | 8 | Environnement final |

## Ordonnancement

Le MVP est Auth + Pytest + Robot API/UI/DB/security + rapports. IA, observabilité avancée et raffinements de rôles ne bloquent pas ce MVP.
