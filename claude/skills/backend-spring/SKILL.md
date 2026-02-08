---
name: backend-spring
description: Work safely in Java/Kotlin/Spring Boot codebases (architecture, transactions, errors, tests).
---

## Checklist (must do)
- Controllers: HTTP boundary only (DTOs, validation, mapping).
- Services: business logic + transaction boundary.
- Repositories: persistence only. No repo access from controllers.
- Prefer constructor injection; avoid field injection.
- Prefer `@Transactional` on service methods; keep transactions small.
- Centralize exception handling; log with context, never secrets/PII.

## JPA/Hibernate safety
- Watch N+1 risks.
- Avoid eager fetches of large collections by default.

## Spring testing
- Prefer slice tests:
  - `@WebMvcTest` for controllers
  - `@DataJpaTest` for repositories
- Use `@SpringBootTest` only for true integration scenarios.
- If DB integration is required, prefer Testcontainers.

## Anti-patterns (do NOT do)
- Business logic in controllers.
- `@Transactional` on controllers.
- Transactions spanning external API calls.
- Silent exception swallowing.
