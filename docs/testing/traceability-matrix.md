# Matrice de traçabilité

Statuts autorisés : Planned, Designed, Implemented, Executed, Passed, Failed, Blocked. Aucun test futur n’est marqué Passed. `UT-PLATFORM-001` (health Pytest) et `REG-SMOKE-001` (smoke technique Robot) sont les seuls tests actuellement **Implemented**; ils valident le socle, pas une exigence métier.

| Requirement ID | Résumé | Test Case ID | Niveau | Outil | Automatisation | Priorité | Statut | Chemin futur | Preuve future | Remarque |
|---|---|---|---|---|---|---|---|---|---|---|
| NFR-REL-001 | Health API | UT-PLATFORM-001 | Unit/API | Pytest | Oui | Must | Implemented | `backend/tests/test_health.py` | pytest output | Technique uniquement |
| NFR-REPRO-001 | Workspace Robot | REG-SMOKE-001 | Smoke | Robot | Oui | Must | Implemented | `robot-tests/smoke/workspace_smoke.robot` | output/log/report | Technique uniquement |
| FR-AUTH-001 | Page login | UI-AUTH-001 | UI | SeleniumLibrary | Future | Must | Designed | `robot-tests/ui/login.robot` | Robot artifacts | — |
| FR-AUTH-002 | Champs | UI-AUTH-002 | UI | SeleniumLibrary | Future | Must | Designed | `robot-tests/ui/login.robot` | screenshot expurgée | — |
| FR-AUTH-003 | Login requis | UT-AUTH-001 | Unit | Angular/Jasmine | Future | Must | Planned | `frontend/src/app/auth/` | test output | — |
| FR-AUTH-004 | Password requis | UT-AUTH-002 | Unit | Angular/Jasmine | Future | Must | Planned | `frontend/src/app/auth/` | test output | — |
| FR-AUTH-005 | Succès | API-AUTH-001 | API | Robot RequestsLibrary | Future | Must | Designed | `robot-tests/api/auth.robot` | Robot artifacts | DB aussi |
| FR-AUTH-006 | Inconnu | SEC-AUTH-001 | Security/API | Robot | Future | Must | Designed | `robot-tests/security/auth.robot` | Robot artifacts | Erreur générique |
| FR-AUTH-007 | Mauvais password | SEC-AUTH-002 | Security/API | Robot | Future | Must | Designed | `robot-tests/security/auth.robot` | Robot artifacts | Erreur générique |
| FR-AUTH-008 | Casse | API-AUTH-004 | API | Robot RequestsLibrary | Future | Must | Planned | `robot-tests/api/auth.robot` | output.xml | Politique à confirmer |
| FR-AUTH-009 | Welcome | UI-AUTH-005 | UI | SeleniumLibrary | Future | Must | Designed | `robot-tests/ui/auth.robot` | screenshot expurgée | — |
| FR-AUTH-010 | Logout | API-AUTH-005 | API/UI | Robot | Future | Must | Designed | `robot-tests/api/auth.robot` | Robot artifacts | CSRF inclus |
| FR-AUTH-011 | Routes privées | SEC-AUTH-004 | Security | Robot | Future | Must | Designed | `robot-tests/security/authorization.robot` | output.xml | Contrôle serveur |
| FR-AUTH-012 | Multi-utilisateurs | IT-AUTH-002 | Integration | Pytest | Future | Must | Planned | `backend/tests/integration/` | pytest output | Sessions isolées |
| FR-AUTH-013 | Désactivé | SEC-AUTH-005 | Security/API | Robot | Future | Must | Designed | `robot-tests/security/auth.robot` | output.xml | Erreur générique |
| FR-AUTH-014 | Verrouillage | SEC-AUTH-006 | Security | Robot/Pytest | Future | Should | Designed | `robot-tests/security/lockout.robot` | output.xml | Valeurs à confirmer |
| FR-AUTH-015 | Fin verrouillage | UT-AUTH-007 | Unit | Pytest | Future | Should | Planned | `backend/tests/test_lockout.py` | pytest output | Horloge injectée |
| FR-AUTH-016 | Expiration | SEC-AUTH-007 | Security | Robot | Future | Should | Designed | `robot-tests/security/session.robot` | output.xml | — |
| FR-AUTH-017 | Token modifié | SEC-AUTH-008 | Security | Robot | Future | Should | Designed | `robot-tests/security/session.robot` | output.xml | Ne pas loguer token |
| FR-ADMIN-001 | Liste users | API-ADMIN-001 | API | Robot RequestsLibrary | Future | Must | Designed | `robot-tests/api/admin.robot` | Robot artifacts | — |
| FR-ADMIN-002 | Créer user | API-ADMIN-002 | API/DB | Robot | Future | Must | Designed | `robot-tests/api/admin.robot` | Robot artifacts | Hash DB |
| FR-ADMIN-003 | Activer | API-ADMIN-003 | API | Robot | Future | Must | Planned | `robot-tests/api/admin.robot` | output.xml | — |
| FR-ADMIN-004 | Désactiver | SEC-ADMIN-002 | Security | Robot | Future | Must | Designed | `robot-tests/security/admin.robot` | output.xml | Sessions à confirmer |
| FR-ADMIN-005 | Rôles | DB-ADMIN-003 | Database | DatabaseLibrary | Future | Should | Planned | `robot-tests/database/roles.robot` | output.xml | — |
| FR-ADMIN-006 | Accès admin | SEC-ADMIN-003 | Security | Robot | Future | Must | Designed | `robot-tests/security/admin.robot` | output.xml | 401/403 |
| FR-AUDIT-001 | Audit succès | DB-AUTH-001 | Database | DatabaseLibrary | Future | Must | Designed | `robot-tests/database/audit.robot` | output.xml | Sans secret |
| FR-AUDIT-002 | Audit échec | DB-AUTH-002 | Database | DatabaseLibrary | Future | Must | Designed | `robot-tests/database/audit.robot` | output.xml | Cause interne |
| FR-AUDIT-003 | Lire audit | SEC-AUDIT-001 | Security/API | Robot | Future | Must | Planned | `robot-tests/security/audit.robot` | output.xml | Minimisation |
| FR-TEST-001 | Pytest | UT-PLATFORM-002 | Unit | Pytest | Future | Must | Planned | `backend/tests/` | pytest output | Health déjà distinct |
| FR-TEST-002 | API Robot | API-AUTH-001 | API | RequestsLibrary | Future | Must | Designed | `robot-tests/api/` | Robot artifacts | — |
| FR-TEST-003 | UI Robot | UI-AUTH-001 | UI | SeleniumLibrary | Future | Must | Designed | `robot-tests/ui/` | Robot artifacts | — |
| FR-TEST-004 | DB Robot | DB-AUTH-001 | Database | DatabaseLibrary | Future | Must | Designed | `robot-tests/database/` | Robot artifacts | — |
| FR-TEST-005 | Sécurité | SEC-AUTH-001 | Security | Robot | Future | Must | Designed | `robot-tests/security/` | Robot artifacts | — |
| FR-TEST-006 | output.xml | REG-AUTH-001 | System | Robot | Future | Must | Planned | `robot-tests/results/` | output.xml | Répertoire par run |
| FR-TEST-007 | log.html | REG-AUTH-002 | System | Robot | Future | Must | Planned | `robot-tests/results/` | log.html | Expurgé |
| FR-TEST-008 | report.html | REG-AUTH-003 | System | Robot | Future | Must | Planned | `robot-tests/results/` | report.html | Totaux cohérents |
| FR-TEST-009 | Régression | REG-AUTH-004 | Regression | Robot/CI | Future | Must | Planned | `.github/workflows/` | CI artifacts | Future CI |
| FR-AI-001 | Brouillon IA | AI-TEST-001 | AI | Pytest/Robot | Future | Could | Planned | `ai-testing/tests/` | rapport IA | Revue humaine |
| FR-AI-002 | Analyse | AI-TEST-002 | AI | Pytest | Future | Could | Planned | `ai-testing/tests/` | rapport IA | Copie expurgée |
| FR-AI-003 | Classification | AI-TEST-003 | AI | Pytest | Future | Could | Planned | `ai-testing/tests/` | rapport IA | unknown permis |
| FR-AI-004 | Recommandations | AI-TEST-004 | AI/Security | Pytest | Future | Could | Planned | `ai-testing/tests/` | rapport IA | Non exécutées |
| FR-AI-005 | Revue humaine | AI-TEST-005 | Workflow | Robot/Pytest | Future | Must si IA | Planned | `ai-testing/tests/` | décision revue | — |
| FR-AI-006 | Verdict immuable | AI-TEST-006 | Integration | Pytest | Future | Must si IA | Designed | `ai-testing/tests/` | avant/après | Panne sans impact |

Total : 43 lignes de données, dont 41 couvrent toutes les exigences fonctionnelles.
