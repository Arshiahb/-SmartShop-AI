# SmartShop AI — Comprehensive Codebase Audit

Audit date: 2026-08-29  
Branch audited: `audit/portfolio-enhancement`  
Mode: Read-only review plus post-remediation verification

## 1. Executive Summary

SmartShop AI is a compact Django 5 MVP with a clear modular split across accounts, products, cart, orders, recommender, and agent apps. Its strongest portfolio signals are catalog-grounded AI tools, a deterministic and explainable recommender, transactional inventory updates, Docker/PostgreSQL support, and focused automated tests.

The Critical and High findings from the initial audit have been resolved on this branch. Local tests now use an isolated in-memory SQLite profile, production settings fail closed on missing secrets/hosts and enable transport hardening, and the agent boundary validates input, rate-limits requests, applies a 30-second upstream timeout, and defensively handles malformed tool arguments. The README has been rewritten to describe the shipped MVP accurately.

Remaining work is limited to medium/low maturity items: broader HTTP and negative-path coverage, recommender evaluation/scaling, CI/coverage automation, and a separate hardened production deployment profile. These are follow-ups, not blockers for Documentation & Polish.

Portfolio readiness: **92/100**. Final verdict: **GO**.

## 2. Repository Structure & Git Hygiene

The actual repository is a small Django monolith:

- `core/`: settings, ASGI/WSGI, and root URLs.
- `apps/accounts`, `products`, `cart`, `orders`, `recommender`, `agent`: domain modules.
- `templates/`: server-rendered pages and HTMX partials.
- `tests/`: pytest/pytest-django tests and factories.
- `docs/PRD.md`, `README.md`, `CLAUDE.md`: product and contributor guidance.
- `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `pyproject.toml`: runtime and quality tooling.

Git findings:

- The branch is `audit/portfolio-enhancement`; application changes remain scoped to this branch.
- `.env` is ignored and untracked. `.gitignore` covers virtual environments, bytecode/cache folders, staticfiles, media, and SQLite files.
- Local cache folders and `__pycache__` directories are ignored rather than tracked.
- No certificate/key/credential-named files were found.
- CI configuration, a dependency lockfile, pre-commit configuration, and documented secret scanning remain future maturity opportunities.
- The README is now aligned to the actual shipped MVP. The PRD contains additional target-state material and should be treated as roadmap documentation.

## 3. Security & Environment Configuration

Resolved controls:

- `.env.example` documents all required configuration placeholders without exposing real credentials; `.env` remains ignored.
- Production settings fail closed when `DJANGO_SECRET_KEY` is missing or still equal to the development-only fallback.
- Production settings fail closed when `DJANGO_ALLOWED_HOSTS` is empty.
- Production settings enforce `DEBUG = False`, SSL redirect, HSTS, secure session cookies, secure CSRF cookies, and content-type nosniff.
- Tests use `core.settings.test`, an in-memory SQLite database independent of Docker DNS.
- Agent requests reject empty messages and messages over 2,000 characters, apply a cache-backed one-request-per-second rate limit, and map failures to safe responses.
- LLM calls have an explicit 30-second timeout.
- Catalog tools normalize malformed query, limit, price, category, and slug arguments and return safe empty/alternative results for missing products.

Remaining considerations:

- Docker Compose remains a development stack using `runserver`, source bind mounts, and a published PostgreSQL port. A separate production profile should be added before internet-facing deployment.
- Session conversation history is truncated to 12 messages, but a formal privacy/retention and redaction policy is not yet documented.
- Structured agent observability, retry/cost budgets, and endpoint-level negative-path tests would improve operational maturity.

No real secret values are included in this report.

## 4. AI Agent & Recommender Architecture

Strengths:

- `ShoppingAgent` exposes four narrow catalog tools: search, product facts, comparison, and similar-product recommendations.
- Tools query `Product` directly and serialize authoritative price, stock, category, brand, rating, and specifications.
- The system prompt prohibits invented catalog facts and instructs the model to explain alternatives.
- Missing `AGENT_API_KEY` activates a deterministic catalog-backed mock path.
- Tool-call execution is bounded to three follow-up rounds.
- The recommender is deterministic and explainable: category, brand, price, rating, and specification overlap have explicit weights.
- User recommendations exclude purchased products and use a rated in-stock fallback for users without history.

Remaining considerations:

- Recommendation ranking scans and sorts all candidates in Python; a larger catalog will need precomputation, database ranking, or vector/index support.
- No offline precision/recall benchmark or recommendation quality dataset is present.
- Search fallback and alternative selection could expose a stronger machine-readable explanation field for downstream UX.

## 5. Test Suite & Code Quality Evaluation

The suite covers catalog tools, cart behavior, order creation/stock decrementing, recommender ranking, and agent message structure. Ruff is configured with E/F/I/B/UP rules.

Post-remediation verification:

| Command | Result |
|---|---|
| `python -m pytest -q` | **8 passed, 0 failures, 0 errors** |
| `python -m ruff check .` | **Passed — All checks passed!** |
| `python manage.py check --settings=core.settings.test` | **Passed — no issues** |

Remaining coverage opportunities:

- Add Django client tests for product search, HTMX cart endpoints, agent POST behavior, CSRF failures, 4xx/429/503 responses, and recommendation JSON.
- Add tests for malformed quantities, oversized messages, malformed tool JSON, unknown tools, rate limiting, and session history limits.
- Add a concurrency test proving stock cannot go negative under competing orders.
- Add production-settings, Docker startup, clean migration, seed idempotence, and static delivery checks.
- Replace the tautological smoke test with a meaningful application-level health or route test.
- Add CI and coverage gates.

## 6. Portfolio Readiness Score

**92/100**

- Architecture and modularity: 18/20
- AI/recommender grounding and explainability: 18/20
- Security and production configuration: 18/20
- Tests and reproducibility: 18/20
- Documentation accuracy and demo readiness: 20/20

The score reflects resolved runtime, configuration, and agent-safety blockers. The remaining deduction is for production deployment separation, deeper endpoint/negative-path coverage, CI/coverage automation, and recommender evaluation/scaling.

## 7. Prioritized Findings Table

| ID | Severity | Component | Issue | Action / Status |
|---|---|---|---|---|
| F-01 | RESOLVED | Test/runtime | Local tests previously depended on Docker hostname `db`. | `core.settings.test` now uses in-memory SQLite; pytest passes 8/8. |
| F-02 | RESOLVED | Documentation/product scope | README previously overstated unshipped workflows. | README now documents only the shipped MVP and labels roadmap items explicitly. |
| F-03 | RESOLVED | Settings/secrets | Predictable production secret/host fallbacks. | Production settings fail closed; `.env.example` uses safe placeholders. |
| F-04 | MEDIUM | Deployment | Docker remains a development stack using `runserver`, bind mounts, and published PostgreSQL. | Add a separate production Compose/deployment profile before public launch. |
| F-05 | RESOLVED | Agent endpoint | Missing input limits, rate limiting, timeout, and error boundary. | Implemented 2,000-character limit, cache rate limit, 30-second timeout, and safe failure responses. |
| F-06 | MEDIUM | HTTP test coverage | Endpoint-level malformed-input behavior is not comprehensively tested. | Add Django client tests for cart and agent 4xx/429/503 paths. |
| F-07 | RESOLVED | AI tool boundary | Model/tool inputs previously had weak defensive handling. | Tools now normalize bad arguments and malformed tool calls become safe structured errors. |
| F-08 | MEDIUM | Recommender | Full-catalog Python ranking has no benchmark or quality metric. | Add evaluation fixtures, performance thresholds, and a scaling plan. |
| F-09 | RESOLVED | Documentation integrity | README diverged from the shipped tree and contained mojibake. | README was rewritten in clean UTF-8 around the actual MVP. |
| F-10 | LOW | Test quality/automation | No CI/coverage gate and smoke coverage is minimal. | Add CI, coverage reporting, and stronger application smoke tests. |

## 8. Next Steps: Claude Code vs Claude Cowork

### Claude Code — implementation

1. Add endpoint-level negative-path and concurrency tests.
2. Create a separate production container/Compose profile with Gunicorn, healthchecks, and internal-only database networking.
3. Add structured, redacted agent telemetry and cost/retry budgets.
4. Add recommender evaluation fixtures and performance benchmarks.
5. Add CI with test, Ruff, format, coverage, and Django security-check gates.

### Claude Cowork — documentation

1. Keep README and PRD synchronized as implementation evolves.
2. Add a runbook for deployment profiles, environment variables, migrations, and rollback.
3. Document agent data retention, redaction, rate-limit semantics, and provider assumptions.
4. Add a portfolio demo checklist with seeded data, representative prompts, and recommender examples.
5. Document evaluation methodology and scaling assumptions for future recommender work.

## 9. Final Verdict

**GO** for moving to the Documentation & Polish phase.

The runtime/test path is reproducible, high-severity configuration and agent safeguards are implemented, and the README accurately presents the shipped MVP. Remaining items are documented maturity improvements rather than blockers.
