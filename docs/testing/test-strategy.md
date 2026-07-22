# Stratégie de test

## Objectifs, périmètre et principes

La stratégie démontre conformité fonctionnelle, sécurité, fiabilité et traçabilité. Sont couverts : backend Flask, frontend Angular, PostgreSQL, contrats API, parcours auth/admin, audits, artefacts et intégration IA future. Hors périmètre semaine 1 : implémentation métier, charge contractuelle, pentest externe, haute disponibilité, mobile natif et qualité intrinsèque d’un modèle IA.

Les tests classiques sont déterministes, fonctionnent sans clé IA et fixent seuls le verdict. L’IA ne change jamais le statut Robot; sa panne ne fait pas échouer la suite classique. Brouillons et recommandations exigent une revue humaine. Aucune capture sensible n’est envoyée à distance par défaut; secrets et PII sont masqués avant analyse.

## Pyramide et suites

1. Nombreux tests unitaires **Pytest** : validation, verrouillage avec horloge injectée, autorisation et redaction.
2. Tests d’intégration Flask/PostgreSQL : transactions, contraintes, audits, session/révocation.
3. Tests **Robot Framework RequestsLibrary** : contrat API, scénarios positifs/négatifs et autorisation.
4. Tests **DatabaseLibrary** ciblés : effets persistants sans dupliquer la logique API.
5. Peu de tests UI **SeleniumLibrary** : parcours critiques avec `data-testid`, attentes explicites, aucun sleep arbitraire.
6. Tests sécurité négatifs puis smoke rapide et régression complète. Les tests de contrat vérifient codes, schémas, headers/cookies et absence de champs interdits.

Tags futurs : `smoke`, `regression`, `api`, `ui`, `database`, `security`, `authentication`, `authorization`, `negative`, `ai-assisted`. Un test peut cumuler plusieurs tags; `ai-assisted` reste exclu du verdict classique.

## Données, temps et isolation

- Données synthétiques par run, IDs uniques et rôles explicites; aucune donnée réelle. Les intégrations et migrations refusent toute URL dont la base n’est pas exactement `auth_test_ai_test`. Setup idempotent et nettoyage ciblé par `TRUNCATE` sur cette base dédiée; jamais suppression de volume ou de base de développement.
- La factory valide le nom exact `auth_test_ai_test` avant toute extension ou connexion; les migrations sont exercées réellement depuis `base` vers `head`, puis downgrade et second upgrade. Le schéma `server_sessions` produit par Flask-Session `>=0.8,<0.9` est comparé à la migration versionnée (types, tailles, nullabilité, clés et index).
- La protection des compteurs concurrents est vérifiée de façon déterministe en compilant `SELECT ... FOR UPDATE` avec le dialecte PostgreSQL; un test de contention à deux transactions est réservé à une future suite de charge isolée pour éviter une dépendance à l’ordonnancement.
- Geler/injecter l’horloge pour expiration et verrouillage. Ne pas attendre réellement. Seuil, durée et reset sont configurés par fixtures après validation.
- Parallélisation future uniquement après isolation par worker (schema, comptes et répertoire de résultats distincts); commencer séquentiel.
- En échec UI, capture limitée à la page utile après masquage; jamais password, cookie, token ou console contenant un secret.

## Exécution, preuves et environnements

Local : Pytest backend; Angular unit tests/build; Robot par tags lorsque services requis sont prêts. Future CI GitHub Actions : installation verrouillée, services PostgreSQL, migrations non destructives, suites, puis publication conditionnelle des artefacts.

Chaque run Robot écrit dans un répertoire unique : `output.xml` (source machine), `log.html` (diagnostic) et `report.html` (synthèse). Totaux, timestamps, code retour, commit et environnement sont corrélés. Logs backend/frontend et captures sont joints seulement si nécessaires et expurgés. Rétention/ACL sont à confirmer; l’échec de publication ne transforme jamais un FAIL en PASS.

## Critères de pilotage

- **Entrée** : version identifiée, environnement sain, données isolées, dépendances installées, exigences/tests liés et aucun incident bloquant connu.
- **Sortie** : tous tests prévus exécutés, aucun défaut critique ouvert accepté implicitement, preuves cohérentes, écarts/flaky documentés. Seuils de couverture et tolérance défauts : à valider.
- **Suspension** : environnement corrompu, fuite potentielle de secret, données non isolées, contrat non stabilisé ou taux d’incidents empêchant un verdict fiable.
- **Reprise** : cause corrigée, secret rotaté si besoin, environnement revalidé, données recréées proprement, smoke réussi puis périmètre affecté relancé.

Un défaut contient exigence, test, version, environnement, étapes, attendu/observé et preuve expurgée. Un flaky reste Failed/Blocked selon résultat réel; reruns sont diagnostiques, jamais un moyen de sélectionner un PASS. Il est isolé, mesuré, assigné et corrigé avant réactivation.

## Responsabilités

Le développeur maintient unitaires/intégration; Test Engineer conçoit Robot, données et preuves; Security owner revoit menaces/cas négatifs; DevOps maintient future CI et secrets; encadrant valide politiques et seuils; humain revoit toute sortie IA. Les environnements local/CI/staging sont configurés séparément, sans secrets partagés.
