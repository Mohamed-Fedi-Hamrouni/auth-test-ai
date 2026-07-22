# Matrice de traçabilité

Statuts autorisés : Planned, Designed, Implemented, Executed, Passed, Failed, Blocked. Les tests Pytest backend de semaine 2 sont **Implemented**; ce statut décrit le dépôt et ne prétend pas qu’une future exécution a réussi. Les tests Robot métier restent Designed/Planned.

| Requirement ID | Résumé | Test Case ID | Niveau | Outil | Automatisation | Priorité | Statut | Chemin futur | Preuve future | Remarque |
|---|---|---|---|---|---|---|---|---|---|---|
| NFR-REL-001 | Health API | UT-PLATFORM-001 | Unit/API | Pytest | Oui | Must | Implemented | `backend/tests/integration/test_auth_api.py::test_health_and_csrf_contract` | pytest output | Technique uniquement |
| NFR-REPRO-001 | Workspace Robot | REG-SMOKE-001 | Smoke | Robot | Oui | Must | Implemented | `robot-tests/smoke/workspace_smoke.robot` | output/log/report | Technique uniquement |
| NFR-SECRET-001 | Configuration fail-closed | UT-CONFIG-001 | Unit | Pytest | Oui | Must | Implemented | `backend/tests/unit/test_config.py::test_explicit_environments_and_fail_closed_selection` | pytest output | Environnement explicite |
| NFR-SECRET-001 | Secret production | UT-CONFIG-002 | Unit | Pytest | Oui | Must | Implemented | `backend/tests/unit/test_config.py::test_production_secret_validation_rejects_weak_values` | pytest output | Placeholder exact inclus |
| FR-AUTH-005 | Authentification réussie | UT-AUTH-001 | Integration | Pytest/PostgreSQL | Oui | Must | Implemented | `backend/tests/integration/test_auth_api.py::test_successful_login_normalization_me_and_logout` | pytest output | HTTP 200, identité, session et logout |
| FR-AUTH-014/015 | Verrouillage/expiration | UT-AUTH-006 | Unit | Pytest | Oui | Must | Implemented | `backend/tests/unit/test_domain.py::test_lockout_calculation_and_expiration` | pytest output | Horloge contrôlée |
| FR-AUTH-014 | Verrou de ligne | UT-AUTH-008 | Unit | Pytest | Oui | Must | Implemented | `backend/tests/unit/test_domain.py::test_locked_lookup_uses_select_for_update` | pytest output | Vérifie `FOR UPDATE`; concurrence réelle future |
| FR-AUTH-006/007 | Identifiants invalides génériques | IT-AUTH-001 | Integration | Pytest/PostgreSQL | Oui | Must | Implemented | `backend/tests/integration/test_auth_api.py::test_invalid_credentials_are_generic` | pytest output | Login inconnu et mauvais password paramétrés |
| FR-AUTH-010, FR-AUTH-012, FR-AUTH-017 | Sessions/logout | IT-AUTH-002 | Integration | Pytest/PostgreSQL | Oui | Must | Implemented | `backend/tests/integration/test_auth_api.py::test_sessions_are_isolated_and_modified_cookie_is_refused` | pytest output | Isolation et cookie modifié |
| FR-AUTH-003/004/008 | Champs requis et casse password | IT-AUTH-003 | Integration | Pytest/PostgreSQL | Oui | Must | Implemented | `backend/tests/integration/test_auth_api.py::test_password_is_case_sensitive_and_required_fields` | pytest output | Login/password requis; password sensible à la casse |
| FR-ADMIN-002..004 | CSRF admin | IT-CSRF-002 | Integration | Pytest/PostgreSQL | Oui | Must | Implemented | `backend/tests/integration/test_admin_api.py::test_admin_mutations_require_valid_csrf` | pytest output | Absence et invalidité |
| FR-AUDIT-003 | Pagination audit | IT-AUDIT-001 | Integration | Pytest/PostgreSQL | Oui | Must | Implemented | `backend/tests/integration/test_admin_api.py::test_audit_pagination_boundaries_and_safe_filters` | pytest output | Sémantique des filtres et champs sûrs |
| FR-AUTH-010 | Rotation CSRF au login | IT-CSRF-003 | Integration | Pytest/PostgreSQL | Oui | Must | Implemented | `backend/tests/integration/test_auth_api.py::test_login_invalidates_anonymous_csrf_token` | pytest output | Ancien jeton refusé |
| FR-AUTH-010 | Cookie logout production | IT-SESSION-003 | Integration | Pytest/PostgreSQL | Oui | Must | Implemented | `backend/tests/integration/test_auth_api.py::test_production_style_logout_cookie_is_secure` | pytest output | Secure/HttpOnly/SameSite/Path |
| NFR-DATA-001 | Schéma Flask-Session | IT-DB-002 | Integration | Pytest/PostgreSQL | Oui | Must | Implemented | `backend/tests/integration/test_migrations.py::test_session_schema_matches_flask_session_model` | pytest output | Types, nullabilité, contraintes et index |
| NFR-DATA-001 | Migration réversible | IT-DB-001 | Integration | Pytest/Alembic | Oui | Must | Implemented | `backend/tests/integration/test_migrations.py::test_alembic_empty_upgrade_downgrade_and_second_upgrade` | pytest output | Base dédiée uniquement |
| FR-AUTH-001 | Page login | UI-AUTH-001 | UI | SeleniumLibrary | Future | Must | Designed | `robot-tests/ui/login.robot` | Robot artifacts | — |
| FR-AUTH-002 | Champs | UI-AUTH-002 | UI | SeleniumLibrary | Future | Must | Designed | `robot-tests/ui/login.robot` | screenshot expurgée | — |
| FR-AUTH-003 | Login requis | FE-UT-AUTH-001 | Unit | Angular/Jasmine | Future | Must | Planned | `frontend/src/app/auth/` | test output | — |
| FR-AUTH-004 | Password requis | UT-AUTH-002 | Unit | Angular/Jasmine | Future | Must | Planned | `frontend/src/app/auth/` | test output | — |
| FR-AUTH-005 | Succès | API-AUTH-001 | API | Robot RequestsLibrary | Future | Must | Designed | `robot-tests/api/auth.robot` | Robot artifacts | DB aussi |
| FR-AUTH-006 | Inconnu | SEC-AUTH-001 | Security/API | Robot | Future | Must | Designed | `robot-tests/security/auth.robot` | Robot artifacts | Erreur générique |
| FR-AUTH-007 | Mauvais password | SEC-AUTH-002 | Security/API | Robot | Future | Must | Designed | `robot-tests/security/auth.robot` | Robot artifacts | Erreur générique |
| FR-AUTH-008 | Casse | API-AUTH-004 | API | Robot RequestsLibrary | Future | Must | Planned | `robot-tests/api/auth.robot` | output.xml | Politique à confirmer |
| FR-AUTH-009 | Welcome | UI-AUTH-005 | UI | SeleniumLibrary | Future | Must | Designed | `robot-tests/ui/auth.robot` | screenshot expurgée | — |
| FR-AUTH-010 | Logout | API-AUTH-005 | API/UI | Robot | Future | Must | Designed | `robot-tests/api/auth.robot` | Robot artifacts | CSRF inclus |
| FR-AUTH-011 | Routes privées | SEC-AUTH-004 | Security | Robot | Future | Must | Designed | `robot-tests/security/authorization.robot` | output.xml | Contrôle serveur |
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
| FR-TEST-002 | API Robot | TEST-API-001 | API | RequestsLibrary | Future | Must | Designed | `robot-tests/api/` | Robot artifacts | — |
| FR-TEST-003 | UI Robot | TEST-UI-001 | UI | SeleniumLibrary | Future | Must | Designed | `robot-tests/ui/` | Robot artifacts | — |
| FR-TEST-004 | DB Robot | TEST-DB-001 | Database | DatabaseLibrary | Future | Must | Designed | `robot-tests/database/` | Robot artifacts | — |
| FR-TEST-005 | Sécurité | TEST-SEC-001 | Security | Robot | Future | Must | Designed | `robot-tests/security/` | Robot artifacts | — |
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

Total : 56 lignes de données — Implemented: 16; Designed: 23; Planned: 17.
