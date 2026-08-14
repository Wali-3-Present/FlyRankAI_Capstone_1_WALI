# AI & Architecture Buildlog

- **Architecture Decisions**: Designed separate HTTP routes for Tenant Auth/CRUD, Delivery CDN static script, and Hardened Public Submissions.
- **AI Assist**: Used AI to scaffold SQLite schemas and FastAPI CORS configuration.
- **Refactoring**: Corrected CORS configuration to support CORS OPTIONS preflight headers.
- **Resilience Testing**: Added mock fallback chains to ensure geo enrichment provider errors gracefully degrade without failing lead submissions.