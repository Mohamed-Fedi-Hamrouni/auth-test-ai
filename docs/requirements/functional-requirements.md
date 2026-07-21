# Exigences fonctionnelles

Version de conception semaine 1. Statut de toutes les exigences : **Proposed — supervisor validation required**. Les scénarios et tests sont planifiés, sauf le health check explicitement identifié dans la matrice.

## Classification

- **Sujet obligatoire (Must)** : FR-AUTH-001 à 013, FR-ADMIN-001/002/003/004/006, FR-AUDIT-001 à 003, FR-TEST-001 à 009.
- **Amélioration de sécurité (Should)** : FR-AUTH-014 à 017 et FR-ADMIN-005.
- **Bonus (Could)** : extension fine des rôles au-delà des rôles validés.
- **IA future (Could)** : FR-AI-001 à 006 ; hors MVP déterministe.

Les champs `Alt./exceptions` regroupent scénarios alternatifs et exceptions. Les critères sont vérifiables mais toute valeur de politique non validée reste une cible initiale.

## Authentification

| ID | Titre / description | Acteur; priorité | Préconditions; déclencheur | Scénario principal | Alt./exceptions | Résultat et critères d’acceptation mesurables | Niveau; Test Case IDs | Dépendances |
|---|---|---|---|---|---|---|---|---|
| FR-AUTH-001 | Affichage de la page de connexion | User; Must | Frontend disponible; navigation vers `/login` | Angular affiche le formulaire | API indisponible : formulaire visible, soumission échoue proprement | Titre, labels, champs et bouton visibles; navigation clavier possible | UI; UI-AUTH-001 | Frontend, routage |
| FR-AUTH-002 | Présence des champs login et password | User; Must | Page chargée; affichage | Rendre deux contrôles typés correctement | Autofill autorisé sans exposer le secret | Un champ login et un champ `password`, avec labels et `data-testid` stables | UI; UI-AUTH-002 | FR-AUTH-001 |
| FR-AUTH-003 | Login obligatoire | User; Must | Formulaire ouvert; soumission vide | Bloquer et associer une erreur au login | Espaces seuls considérés vides | Aucune requête d’authentification; erreur accessible | Unit/UI; UT-AUTH-001, UI-AUTH-003 | FR-AUTH-002 |
| FR-AUTH-004 | Password obligatoire | User; Must | Formulaire ouvert; soumission vide | Bloquer et associer une erreur au password | Espaces seuls : politique à confirmer | Aucune requête; secret jamais réaffiché | Unit/UI; UT-AUTH-002, UI-AUTH-004 | FR-AUTH-002 |
| FR-AUTH-005 | Authentification réussie | User; Must | Compte actif/non verrouillé; identifiants exacts | Vérifier hash, créer session, auditer | Erreur technique : réponse générique, pas de session | HTTP 200; cookie sécurisé; audit succès; accès privé autorisé | Unit/Integration/API; UT-AUTH-003, IT-AUTH-001, API-AUTH-001 | DB, FR-AUDIT-001, ADR-0003 |
| FR-AUTH-006 | Utilisateur inconnu | User; Must | Login absent; soumission | Refuser sans session | Entrée mal formée : 400 | HTTP 401 et même message public que mauvais mot de passe; audit interne sans `user_id` | API/Security; API-AUTH-002, SEC-AUTH-001 | FR-AUDIT-002 |
| FR-AUTH-007 | Mot de passe incorrect | User; Must | Compte existant; mauvais secret | Refuser et auditer | Seuil atteint : verrouillage | HTTP 401 générique; aucune session; compteur mis à jour | Unit/API/Security; UT-AUTH-004, API-AUTH-003, SEC-AUTH-002 | FR-AUTH-014, FR-AUDIT-002 |
| FR-AUTH-008 | Sensibilité à la casse | User; Must | Compte existant; casse modifiée | Comparer selon politique explicite | Normalisation Unicode à confirmer | Password toujours sensible; règle login documentée et testée sans contournement | Unit/API; UT-AUTH-005, API-AUTH-004 | Politique encadrant |
| FR-AUTH-009 | `Welcome FIRST_NAME LAST_NAME` | User; Must | Session valide; ouverture accueil privé | Lire identité serveur et afficher | Nom absent : erreur maîtrisée; contenu échappé | Texte exact avec données du compte authentifié, jamais celles du formulaire | UI/Security; UI-AUTH-005, SEC-AUTH-003 | FR-AUTH-005, FR-AUTH-011 |
| FR-AUTH-010 | Déconnexion | User; Must | Session présente; action logout | Invalider serveur et expirer cookie | Session absente/expirée : opération idempotente | Après réponse, `/me` et routes privées refusent l’accès | API/UI; API-AUTH-005, UI-AUTH-006 | ADR-0003, blocklist/session |
| FR-AUTH-011 | Protection des routes privées | User; Must | Route privée; requête | Backend vérifie session et autorisation | Absente/expirée/modifiée : refus uniforme | API 401 sans données; UI redirige; contrôle serveur obligatoire | API/UI/Security; API-AUTH-006, UI-AUTH-007, SEC-AUTH-004 | FR-AUTH-016/017 |
| FR-AUTH-012 | Plusieurs utilisateurs | User; Must | Deux comptes; connexions séparées | Créer des sessions isolées | Connexions concurrentes : politique à confirmer | `/me`, accueil et droits correspondent toujours à chaque session | Integration/API; IT-AUTH-002, API-AUTH-007 | FR-AUTH-005 |
| FR-AUTH-013 | Compte désactivé | User; Must | `is_active=false`; connexion | Refuser et auditer cause interne | Session existante : invalidation à confirmer | 401 générique; aucune session; pas d’énumération | API/Security; API-AUTH-008, SEC-AUTH-005 | FR-ADMIN-004, FR-AUDIT-002 |
| FR-AUTH-014 | Verrouillage après échecs | User; Should (sécurité) | Politique configurée; échecs répétés | Incrémenter puis verrouiller au seuil | Succès avant seuil : reset à confirmer | Seuil configurable; aucune connexion pendant verrouillage; audit complet | Unit/API/Security; UT-AUTH-006, API-AUTH-009, SEC-AUTH-006 | Horloge, politique encadrant |
| FR-AUTH-015 | Expiration du verrouillage | User; Should (sécurité) | `locked_until` dépassé; nouvel essai | Autoriser une nouvelle vérification | Horloge indisponible : refus sûr | Comportement testé avec horloge contrôlée; compteur selon politique | Unit/API; UT-AUTH-007, API-AUTH-010 | FR-AUTH-014 |
| FR-AUTH-016 | Session ou jeton expiré | User; Should (sécurité) | Session expirée; appel privé | Refuser et demander reconnexion | Logout expiré reste idempotent | 401; aucune donnée privée; cookie nettoyé si applicable | API/Security; API-AUTH-011, SEC-AUTH-007 | ADR-0003 |
| FR-AUTH-017 | Jeton modifié refusé | User; Should (sécurité) | Cookie/jeton altéré; appel | Échec de validation cryptographique | Format invalide traité pareil | 401 générique; aucune exécution métier; événement sans token brut | API/Security; API-AUTH-012, SEC-AUTH-008 | Gestion clés |

## Administration et audit

| ID | Titre / description | Acteur; priorité | Préconditions; déclencheur | Scénario principal | Alt./exceptions | Résultat et critères | Niveau; Test Case IDs | Dépendances |
|---|---|---|---|---|---|---|---|---|
| FR-ADMIN-001 | Consultation des utilisateurs | Admin; Must | Session Admin; GET liste | Retourner métadonnées autorisées | Aucun compte : liste vide | 200; jamais `password_hash`; non-admin 403; pagination à confirmer | API/Security; API-ADMIN-001, SEC-ADMIN-001 | FR-ADMIN-006 |
| FR-ADMIN-002 | Création d’un utilisateur | Admin; Must | Admin; données valides | Valider, hasher, persister | Login dupliqué/invalide : 409/400 sans détail sensible | 201; hash uniquement; rôle autorisé; audit administratif futur | Unit/API/DB; UT-ADMIN-001, API-ADMIN-002, DB-ADMIN-001 | Politique password/rôles |
| FR-ADMIN-003 | Activation d’un compte | Admin; Must | Compte inactif; PATCH actif | Passer `is_active=true` | Inconnu : 404; conflit : réponse idempotente | État persisté; login possible si non verrouillé | API/DB; API-ADMIN-003, DB-ADMIN-002 | FR-ADMIN-006 |
| FR-ADMIN-004 | Désactivation d’un compte | Admin; Must | Compte actif; PATCH inactif | Passer `is_active=false` | Auto-désactivation/dernière admin à confirmer | État persisté; nouvelle connexion refusée; sessions existantes selon politique | API/Security; API-ADMIN-004, SEC-ADMIN-002 | FR-AUTH-013 |
| FR-ADMIN-005 | Consultation des rôles | Admin; Should | Admin; GET/lecture utilisateur | Retourner rôles autorisés | Rôle inconnu : erreur maîtrisée | Aucun droit implicite; associations uniques; liste sans secret | API/DB; API-ADMIN-005, DB-ADMIN-003 | Modèle Role/UserRole |
| FR-ADMIN-006 | Contrôle d’accès administrateur | Admin; Must | Session valide; endpoint admin | Vérifier rôle côté serveur | Non authentifié 401; non-admin 403 | Aucun endpoint admin accessible par simple modification UI/claim non fiable | Integration/Security; IT-ADMIN-001, SEC-ADMIN-003 | FR-AUTH-011 |
| FR-AUDIT-001 | Journalisation succès | System/Admin; Must | Login réussi; fin traitement | Écrire tentative succès | Échec stockage : stratégie à confirmer | Horodatage, login protégé, user_id et succès; aucun secret/token | Integration/DB; IT-AUDIT-001, DB-AUTH-001 | AuthenticationAttempt |
| FR-AUDIT-002 | Journalisation échec | System/Admin; Must | Login refusé; fin traitement | Écrire cause interne contrôlée | Login inconnu : user_id null | Échec enregistré sans password; cause jamais exposée publiquement | Integration/DB; IT-AUDIT-002, DB-AUTH-002 | AuthenticationAttempt |
| FR-AUDIT-003 | Consultation des tentatives | Admin; Must | Admin; GET tentatives | Filtrer/paginer résultats | Non-admin 403; plage invalide 400 | Champs sensibles minimisés; tri stable; politique de rétention appliquée | API/Security; API-AUDIT-001, SEC-AUDIT-001 | FR-ADMIN-006, NFR-PRIV |

## Tests automatisés

| ID | Titre / description | Acteur; priorité | Préconditions; déclencheur | Scénario principal | Alt./exceptions | Résultat et critères | Niveau; Test Case IDs | Dépendances |
|---|---|---|---|---|---|---|---|---|
| FR-TEST-001 | Tests unitaires Pytest | Test Engineer/CI; Must | Environnement prêt; commande | Exécuter Pytest backend | Dépendance absente : échec explicite | Code retour fiable et résultats reproductibles | Unit; UT-PLATFORM-001 | Pytest |
| FR-TEST-002 | Tests API Robot | Test Engineer/CI; Must | API/données prêtes; suite `api` | Exécuter RequestsLibrary | API indisponible : échec explicite | Vérifier contrat, statuts, schémas et effets | API; API-AUTH-001..012 | RequestsLibrary |
| FR-TEST-003 | Tests UI Robot | Test Engineer/CI; Must | UI/API/navigateur prêts | Exécuter SeleniumLibrary | Navigateur indisponible : suspension documentée | Locateurs stables; aucun sleep arbitraire | UI; UI-AUTH-001..007 | SeleniumLibrary |
| FR-TEST-004 | Tests base Robot | Test Engineer/CI; Must | DB isolée; migrations/données | Exécuter DatabaseLibrary | DB indisponible : échec/suspension explicite | Assertions persistantes et nettoyage vérifié | Database; DB-AUTH-001..003 | DatabaseLibrary |
| FR-TEST-005 | Tests sécurité | Test Engineer/CI; Must | Environnement autorisé | Exécuter cas négatifs contrôlés | Aucun test destructif hors cible | Couverture des SEC IDs; preuves expurgées | Security; SEC-AUTH-001..008 | Threat model |
| FR-TEST-006 | Génération `output.xml` | CI/Test Engineer; Must | Robot lancé | Écrire résultat machine | Échec disque : campagne signalée | XML valide, cohérent avec verdict, chemin unique | System; REG-REPORT-001 | Robot Framework |
| FR-TEST-007 | Génération `log.html` | CI/Test Engineer; Must | `output.xml` disponible | Générer journal détaillé | Donnée sensible : masquer avant conservation | HTML généré, accessible, sans secret connu | System; REG-REPORT-002 | FR-TEST-006 |
| FR-TEST-008 | Génération `report.html` | CI/Test Engineer; Must | `output.xml` disponible | Générer synthèse | Artefact incomplet : signaler | Totaux cohérents avec XML et statut processus | System; REG-REPORT-003 | FR-TEST-006 |
| FR-TEST-009 | Déclenchement régression | CI/Test Engineer; Must | Critères d’entrée remplis; push/commande | Lancer tags regression | Infrastructure indisponible : Blocked, jamais Passed | Toutes suites prévues lancées; code retour agrégé | Regression; REG-AUTH-001 | Future CI |

## IA assistive future

| ID | Titre / description | Acteur; priorité | Préconditions; déclencheur | Scénario principal | Alt./exceptions | Résultat et critères | Niveau; Test Case IDs | Dépendances |
|---|---|---|---|---|---|---|---|---|
| FR-AI-001 | Brouillon de scénario | Test Engineer/AI Assistant; Could | IA autorisée; besoin fourni | Expurger puis générer brouillon marqué | IA désactivée : indisponibilité explicite | Aucun ajout automatique aux suites; provenance visible | AI/Security; AI-TEST-001, SEC-AI-001 | Redaction, validation humaine |
| FR-AI-002 | Analyse échec Robot | Test Engineer/AI Assistant; Could | Copie expurgée de `output.xml` | Extraire preuve et analyser | Parsing/appel échoue : verdict inchangé | Rapport séparé lié au TestRun; aucun secret | AI; AI-TEST-002 | FR-TEST-006 |
| FR-AI-003 | Classification échec | AI Assistant/Test Engineer; Could | Analyse disponible | Proposer catégorie contrôlée | Incertain : `unknown` et faible confiance | Catégorie, preuve et confiance enregistrées, jamais présentées comme certitude | AI; AI-TEST-003 | Taxonomie à valider |
| FR-AI-004 | Recommandations | AI Assistant; Could | Cause probable disponible | Proposer actions non exécutées | Recommandation risquée : rejeter | Actions traçables, sans exécution automatique | AI/Security; AI-TEST-004, SEC-AI-002 | FR-AI-003 |
| FR-AI-005 | Validation humaine obligatoire | Test Engineer; Must pour toute IA | Sortie IA; demande de publication | Examiner, accepter/rejeter explicitement | Absence de revue : reste brouillon | `requires_human_review` vrai jusqu’à décision; auteur/date tracés | Workflow; AI-TEST-005 | FR-AI-001..004 |
| FR-AI-006 | Conservation statut Robot | System; Must pour toute IA | Verdict Robot existant; analyse | Copier sans mutation | IA indisponible/contradictoire : ignorer pour verdict | Statut original et code retour bit-à-bit/logiquement inchangés | Integration; AI-TEST-006 | FR-AI-002 |

## Hypothèses et décisions à confirmer

- Casse et normalisation du login, exigences de mot de passe, seuil/durée de verrouillage et remise à zéro du compteur.
- Durée de session, révocation, invalidation lors d’une désactivation et stratégie exacte cookie/session.
- Pagination, conservation des audits, anonymisation IP et niveau d’administration.
- Fournisseur IA, modèle local éventuel et données autorisées. L’IA reste facultative et désactivée en CI par défaut.
