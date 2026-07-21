# Exigences non fonctionnelles

Toutes sont **Proposed — supervisor validation required**. Une valeur précédée de **Initial target — to be validated with the supervisor** n’est pas une exigence contractuelle validée.

| ID | Description et justification | Priorité | Vérification / critère mesurable | Niveau | Statut | Décision encadrant |
|---|---|---|---|---|---|---|
| NFR-SEC-001 | Défense en profondeur : hash robuste, requêtes paramétrées, moindre privilège, cookies sécurisés, validation serveur. Réduit compromission et contournement. | Must | Revue, SAST futur et tests SEC; zéro secret/`password_hash` dans réponses | Security | Proposed | Algorithme de hash et politique session |
| NFR-PRIV-001 | Minimiser login, IP, user-agent et preuves; finalités et rétention documentées. | Must | Revue schéma/logs/rapports; tests de redaction | Security/Data | Proposed | Rétention, anonymisation IP, contraintes KPIT |
| NFR-PERF-001 | Login et lectures admin restent utilisables sous charge attendue. | Should | Test de charge futur. **Initial target — to be validated with the supervisor:** p95 login < 500 ms hors réseau IA, charge à définir | Performance | Proposed | Charge, percentile et environnement |
| NFR-REL-001 | Une erreur partielle ne crée ni faux succès ni session incohérente. | Must | Tests d’intégration transactionnels et indisponibilité DB/IA; 0 faux PASS | Integration | Proposed | Stratégie si audit indisponible |
| NFR-MAINT-001 | Responsabilités séparées, code typé, conventions et ADR pour décisions structurantes. | Should | Revue; lint; complexité/couverture comme indicateurs non bloquants | Static/Review | Proposed | Seuils qualité éventuels |
| NFR-TEST-001 | Comportements contrôlables : horloge injectable, données isolées, locateurs stables, erreurs déterministes. | Must | Revue et tests sans sleeps arbitraires; exécution sans clé IA | All | Proposed | Navigateurs et matrice plateformes |
| NFR-TRACE-001 | Chaque exigence possède au moins un test planifié et chaque preuve référence commit/environnement. | Must | Script documentaire; couverture IDs = 100 % des FR | Documentation | Proposed | Granularité exigée |
| NFR-REPRO-001 | Installation verrouillée et commandes documentées donnent des résultats reproductibles. | Must | Nouvelle installation/CI future avec lockfiles; versions enregistrées | System | Proposed | OS/versions de référence |
| NFR-ACCESS-001 | Formulaire utilisable au clavier, labels/erreurs associés, focus visible, contraste de base. | Should | Tests UI + audit manuel; **Initial target — to be validated with the supervisor:** WCAG 2.2 AA sur parcours auth | Accessibility | Proposed | Niveau WCAG et outils |
| NFR-OBS-001 | Logs structurés et métriques futures sans secrets permettent diagnostic et corrélation. | Should | Revue logs; identifiant de corrélation; tests redaction | Integration | Proposed | Métriques/SLA et Prometheus/Grafana |
| NFR-REPORT-001 | `output.xml`, `log.html`, `report.html` sont cohérents, lisibles et expurgés. | Must | Parser XML; égalité totaux/statut; scan de secrets | System | Proposed | Rétention des artefacts |
| NFR-DATA-001 | Données de test dédiées, réinitialisables sans toucher aux données réelles. | Must | DB dédiée/schema isolé; nettoyage vérifié; interdiction des volumes destructifs | Database | Proposed | Stratégie CI et jeux autorisés |
| NFR-SECRET-001 | Secrets hors Git, logs, captures, rapports et prompts; rotation possible. | Must | `git grep`/scanner CI futur; 0 secret connu; `.env` non lu/versionné | Security | Proposed | Gestionnaire de secrets autorisé |
| NFR-AI-001 | IA assistive, optionnelle, expurgée, explicable et soumise à revue; elle ne modifie aucun verdict. | Must si IA | Tests panne/provider, prompt injection, redaction; statut Robot inchangé dans 100 % des cas | AI/Security | Proposed | API externe, modèle local, données permises |

## Cibles encore ouvertes

Les durées de session/verrouillage/rétention, volumes, objectifs de performance, navigateurs, couverture et seuils d’accessibilité exigent une validation de l’encadrant avant de devenir des critères de sortie contractuels.
