# Architecture initiale

```text
auth-test-ai/
├── frontend/          # Application Angular standalone
├── backend/           # API Flask et persistance PostgreSQL 17
├── robot-tests/       # Suites API, UI, base, sécurité et smoke
├── ai-testing/        # Future analyse complémentaire et anonymisée
├── docs/              # Architecture, décisions et preuves de livraison
├── infra/             # Future observabilité et configuration infrastructure
└── .github/workflows/ # Futurs pipelines CI
```

Le frontend est le système web visible. Le backend expose les API métier et
est responsable de la persistance applicative et des sessions serveur. PostgreSQL 17 est lancé localement avec Docker
Compose. Robot Framework couvre les parcours transverses ; Pytest couvre la
logique backend. La couche IA restera indépendante des résultats déterministes.

## Diagramme de contexte

```mermaid
flowchart LR
  U[User/Admin] -->|HTTPS| SYS[AuthTest AI]
  TE[Test Engineer] -->|commandes/rapports| SYS
  CI[GitHub Actions futur] -->|tests/build| SYS
  SYS -->|données expurgées, optionnel| P[AI Provider]
  SYS -->|métriques futures| O[Prometheus / Grafana]
```

## Diagramme de conteneurs

```mermaid
flowchart TB
  B[Browser] -->|HTTPS| NG[Angular frontend]
  NG -->|JSON, cookie HttpOnly, CSRF| FL[Flask backend]
  FL -->|SQL paramétré| PG[(PostgreSQL)]
  PY[Pytest] --> FL
  RF[Robot Framework] --> RQ[RequestsLibrary]
  RF --> SE[SeleniumLibrary]
  RF --> DB[DatabaseLibrary]
  RQ --> FL
  SE --> NG
  DB --> PG
  RF --> ART[output.xml / log.html / report.html]
  ART --> AI[AI testing package futur]
  AI -. expurgé et autorisé .-> EXT[AI provider optionnel]
  FL -. métriques futures .-> PROM[Prometheus / Grafana]
```

## Flux de connexion

```mermaid
sequenceDiagram
  actor U as User
  participant A as Angular
  participant F as Flask
  participant D as PostgreSQL
  U->>A: login + password
  A->>F: POST /api/auth/login
  F->>D: lire User (requête paramétrée)
  D-->>F: hash + état internes
  F->>F: vérifier hash/état/verrouillage
  F->>D: journaliser succès
  F-->>A: 200 + cookie HttpOnly
  A->>F: GET /api/auth/me
  F-->>A: identité minimale
  A-->>U: Welcome FIRST_NAME LAST_NAME
```

## Flux de refus de connexion

```mermaid
sequenceDiagram
  actor U as User
  participant A as Angular
  participant F as Flask
  participant D as PostgreSQL
  U->>A: identifiants
  A->>F: POST /api/auth/login
  F->>D: recherche/contrôle
  F->>F: vérification et règle verrouillage
  F->>D: tentative + cause interne contrôlée
  F-->>A: 401 Invalid credentials
  A-->>U: erreur générique
```

## Flux de logout

```mermaid
sequenceDiagram
  actor U as User
  participant A as Angular
  participant F as Flask
  participant S as Session store / blocklist
  U->>A: Logout
  A->>F: POST /api/auth/logout + CSRF
  F->>S: invalider session
  F-->>A: 204 + expiration cookie
  A-->>U: page login
```

## Flux Robot Framework

```mermaid
flowchart LR
  CMD[Commande + tags] --> SETUP[Données isolées]
  SETUP --> RF[Robot Framework]
  RF --> API[RequestsLibrary vers Flask]
  RF --> UI[SeleniumLibrary vers Angular]
  RF --> DATA[DatabaseLibrary vers PostgreSQL]
  API --> V[Verdict déterministe]
  UI --> V
  DATA --> V
  V --> XML[output.xml]
  XML --> HTML[log.html + report.html]
  HTML --> CLEAN[Nettoyage ciblé]
```

## Flux d’analyse IA futur

```mermaid
flowchart LR
  XML[Copie output.xml] --> PARSE[Parser local]
  PARSE --> REDACT[Redaction / allowlist]
  REDACT --> LOCAL[Analyse locale]
  REDACT -. si autorisé .-> EXT[Provider externe]
  LOCAL --> DRAFT[Classification + recommandations]
  EXT --> DRAFT
  DRAFT --> REVIEW[Validation humaine]
  ORIGINAL[Statut Robot original] --> IMM[Verdict immuable]
  REVIEW -. ne modifie jamais .-> IMM
```

## Flux CI/CD futur

```mermaid
flowchart LR
  PUSH[Push / PR] --> GHA[GitHub Actions]
  GHA --> INSTALL[Installations verrouillées]
  INSTALL --> CHECK[Lint + Pytest + Angular tests/build]
  CHECK --> SERVICES[PostgreSQL isolé]
  SERVICES --> ROBOT[Smoke puis suites Robot]
  ROBOT --> ART[Artefacts expurgés]
  ART --> STATUS[Statut pipeline]
  ROBOT -. IA off par défaut .-> AIOPT[Analyse optionnelle]
```

## Frontières de confiance et flux sensibles

Les frontières sont navigateur/API, API/DB, runners CI/secrets, artefacts/lecteurs et package IA/provider. Login/password traverse uniquement HTTPS vers Flask; le password est vérifié puis abandonné, jamais logué. Cookies et CSRF restent hors logs/captures. Réponses DB, journaux et XML sont non fiables lorsqu’ils deviennent des entrées de rapport ou d’IA. Toute sortie vers un provider exige accord, redaction locale et minimisation. PostgreSQL applicatif et résultats de test sont séparés logiquement; les accès CI suivent le moindre privilège.

Le cookie navigateur contient uniquement un identifiant de session opaque. Les données de session sont conservées dans la table PostgreSQL `server_sessions`; elles expirent après 30 minutes d’inactivité et au plus tard après 8 heures. Prometheus/Grafana, GitHub Actions et le provider IA sont futurs et ne sont pas des dépendances du fonctionnement classique.
