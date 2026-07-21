# Architecture initiale

```text
auth-test-ai/
├── frontend/          # Application Angular standalone
├── backend/           # API Flask et future persistance PostgreSQL
├── robot-tests/       # Suites API, UI, base, sécurité et smoke
├── ai-testing/        # Future analyse complémentaire et anonymisée
├── docs/              # Architecture, décisions et preuves de livraison
├── infra/             # Future observabilité et configuration infrastructure
└── .github/workflows/ # Futurs pipelines CI
```

Le frontend est le système web visible. Le backend expose les API métier et
sera responsable de la persistance. PostgreSQL est lancé localement avec Docker
Compose. Robot Framework couvre les parcours transverses ; Pytest couvre la
logique backend. La couche IA restera indépendante des résultats déterministes.

