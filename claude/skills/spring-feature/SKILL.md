---
name: spring-feature
description: Implement a Spring Boot feature end-to-end (controller/service/repository) with tests.
---
Steps:
1) Confirm acceptance criteria (API contract, edge cases, error codes).
2) Inspect existing patterns (packages, naming, error handling, logging).
3) Implement the smallest viable change:
   - Controller (DTOs, validation, mapping)
   - Service (business logic, transaction boundary)
   - Repository (queries)
4) Add/update tests (behavior-focused).
5) Provide commands to verify (gradle/maven tests).
6) Summarize what changed and why.