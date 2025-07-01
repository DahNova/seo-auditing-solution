# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# SEO Auditing Solution - Enterprise SEO Monitoring Platform

## Project Architecture Overview

This is a production-ready FastAPI-based SEO auditing platform designed as an alternative to enterprise tools like SEMrush/Ahrefs. The system uses **async/await patterns throughout** and is built for agency-scale operations (100-500+ websites).

### Core Architecture Patterns

**Async-First Design**: All database operations, web crawling, and API endpoints use asyncio. The codebase maintains separate sync/async database sessions for Celery compatibility.

**Repository Pattern**: Services layer (`app/services/`) abstracts database operations from API routes (`app/routers/`). Each service handles business logic while routes focus on HTTP concerns.

**Background Processing**: Celery with Redis handles long-running SEO scans. The system uses dedicated queues (`scans`, `monitoring`) with proper task routing.

**Granular Analysis System**: The SEO analyzer generates individual issues per resource (e.g., each blocking CSS file gets its own issue) rather than aggregate counts. This enables actionable reporting.

## Essential Development Commands

### Quick Start
```bash
# Full stack startup
make docker-run          # or docker-compose up -d

# Development with hot reload  
make dev                 # Local development server

# Check everything is working
make health              # Test API availability
```

### Testing Strategy
```bash
# Essential test commands
make test                # Full test suite
make test-unit           # Fast unit tests only
make test-api            # API endpoint tests
make test-seo            # SEO analyzer tests
make test-working        # Quick tests for active development
make test-services       # Service layer tests only
make test-tasks          # Background task tests only
make test-models         # Database model tests only

# Coverage and quality
make test-coverage       # Test coverage report (80% minimum)
make full-test           # Tests + linting + type checking
make test-performance    # Performance baseline tests

# Development workflow
make pre-commit          # Format + lint + unit tests
make quick-test          # Fast tests (unit + API)
make test-watch          # Tests in watch mode for TDD

# CI/CD testing
make ci-test             # CI-compatible test output (JUnit XML)
make ci-security         # Security scanning (bandit + safety)
```

### Docker Operations
```bash
# Rebuild after code changes
make build               # Rebuild app container
docker-compose build app && docker-compose up -d app

# Debug and monitoring
make logs                # Follow application logs
make db-shell            # PostgreSQL shell access
docker-compose ps        # Check service status

# Clean restart
make docker-clean        # Clean Docker resources
make docker-run          # Fresh start
```

### Database Operations
```bash
# Database access
make db-shell            # Interactive PostgreSQL shell
# Credentials: seo_user/seo_password on localhost:5432

# Web interface
# http://localhost:8080 (Adminer)
# Server: postgres, User: seo_user, Password: seo_password

# Migrations (Alembic)
make migrate             # Apply pending migrations
make migrate-create      # Create new migration

# Database utilities
make backup-db           # Backup database with timestamp
make restore-db          # Restore database from backup
make test-db             # Reset test database (SQLite)

# Development utilities
make check-env           # Check Python/package versions
make shell               # Python shell with app context loaded
```

## Core System Components

### SEO Analysis Engine (`app/services/seo_analyzer/`)

**Multi-Layer Analysis Architecture**:
- `seo_analyzer.py` - Main orchestrator
- `issue_detector.py` - Converts findings to standardized issues with granular resource details
- `performance_analyzer.py` - Core Web Vitals and blocking resources (CSS/JS files)
- `technical_seo_analyzer.py` - Schema, meta tags, technical factors
- `content/` - Content quality and accessibility analyzers
- `severity_calculator.py` - Standardized severity assignment with context-based escalation

**Granular Resource Details**: Issues contain structured JSON in the `element` field with specific resource information (URLs, file sizes, optimization recommendations). Each resource generates individual issues rather than aggregate counts. The system uses `ResourceDetailsBuilder` for creating structured issue data and `IssueFactory` for both granular and consolidated issue formats.

**Smart Issue Conversion**: Major issues have been converted to granular format with intelligent suggestions:
- `canonical_mancante` - Generates suggested canonical URLs
- `h1_mancante` - Provides optimized H1 suggestions based on content analysis
- `meta_description_mancante` - Creates SEO-optimized meta descriptions
- `missing_schema_markup` - Recommends appropriate schema types based on page content

**Performance-Aware Issue Limiting**: For large scans (>5000 issues), the system automatically limits to 2000 issues for UI performance, with smart distribution prioritizing critical (40%) and high (35%) severity issues. Granular issues (those with detailed element data) are prioritized over legacy issues.

### Background Processing (`app/tasks/`)

**Celery Task Architecture**:
- `scan_tasks.py` - SEO scan execution
- `monitoring_tasks.py` - Scheduled health checks
- Uses both async (`AsyncSessionLocal`) and sync (`SyncSessionLocal`) database sessions

**Queue Management**: Dedicated queues prevent blocking. Monitor via `/api/v1/scheduler/status`.

### Database Models (`app/models/`)

**Relationship Hierarchy**:
```
Client -> Website -> Scan -> Page -> Issue
                  -> Schedule
                  -> RobotsSnapshot
                  -> SitemapSnapshot
```

**Critical Models**:
- `Scan` - Central entity with performance metrics and status tracking
- `Issue` - SEO problems with severity, category, and resource details
- `Page` - Individual page analysis with scores and Core Web Vitals data

### Frontend Architecture (`app/templates/`)

**Hybrid HTMX/Static Architecture**:
- `components/sections/` - Main page sections (SEMrush-inspired design)
- `components/modals/` - Form modals use static includes (not HTMX) to avoid form data persistence issues
- `components/cards/` - Metric display components
- `components/forms/` - Standalone edit forms used in both static and HTMX contexts

**Critical Modal Implementation**: The system uses **static modal includes** in `base.html` rather than HTMX-loaded modals. This architectural decision prevents form data persistence issues where dynamically loaded forms would reset values. The JavaScript functions `showAddClientModal()` and `showAddWebsiteModal()` directly trigger static modals via Bootstrap's modal API.

**HTMX Router** (`app/routers/htmx.py`): Provides dynamic modal content for edit operations and table updates. These endpoints return partial HTML for:
- Edit form modals with pre-populated data
- Updated table rows after CRUD operations
- Dynamic client/website dropdowns

**Template Router** (`app/routers/templates.py`): Processes database data for template consumption, ensuring all pages that include modals have access to required data (e.g., `clients` list for website creation dropdown).

**Resource Details Display**: The scan results use nested accordions (Severity → Issue Type → Resource Details) with:
- Enhanced 6-column resource tables for granular issues
- Pagination controls (50 resources per page) for performance
- Simple page lists fallback for non-granular issues
- Sorting capabilities by page, resource, type, and impact

## Configuration System

### Environment Setup
- `app/core/config.py` - Main application settings
- SEO thresholds configurable via `SEOConfig` class
- Docker environment variables in `docker-compose.yml`

### SEO Analysis Configuration
- Title/meta description length standards (2024/2025 optimized)
- Image optimization thresholds
- Content quality scoring weights
- Granular issue severity mappings

## API Architecture

### Async Patterns
All API endpoints use `async def` with `AsyncSession = Depends(get_db)`. Database operations use SQLAlchemy's async session pattern.

### Key Endpoints Structure
- `/api/v1/clients/` - Client CRUD (expects `name`, `contact_email`, `description`)
- `/api/v1/websites/` - Website management (expects `domain`, `name`, `client_id`, optional config)
- `/api/v1/scans/` - Scan operations including `/api/v1/scans/{id}/results`
- `/api/v1/scheduler/` - Real-time worker monitoring and queue management
- `/templated/` - Server-side rendered interface (clients, websites, scans, scheduler sections)
- `/htmx/` - Partial HTML endpoints for dynamic content (edit modals, table updates)

### Error Handling
HTTP exceptions use FastAPI's `HTTPException`. Database errors include rollback handling. Celery tasks have retry logic with exponential backoff.

### Schema Validation Patterns
The API uses Pydantic schemas in `app/schemas/` with strict validation:
- **Client Creation**: Requires `name` (min 1 char), optional `contact_email` and `description`
- **Website Creation**: Requires `domain` (extracted from full URLs), `client_id`, optional `name` and config
- JavaScript form handlers automatically extract domains from full URLs and map form fields to API schema expectations
- Validation errors return 422 with detailed field-level error messages

## Web Crawling Integration

### Crawl4AI Integration
- Uses async web crawler with Playwright backend
- Supports both single-page and deep crawling strategies
- Extracts structured SEO data including Core Web Vitals estimates
- Respects robots.txt when configured

### Content Analysis Pipeline
1. Crawl4AI extracts raw HTML and metadata
2. Multiple specialized analyzers process different aspects
3. Issues are converted to standardized format with resource details
4. Scoring engine calculates overall SEO scores

## Development Workflow

### Code Quality Pipeline
```bash
make pre-commit          # Format + lint + unit tests
make format              # Black + isort formatting
make lint                # flake8 + black check + isort check
make type-check          # mypy type checking
make clean               # Clean cache and temporary files

# Additional quality checks
make check-deps          # Security audit (pip-audit + safety)
make update-deps         # Update dependency locks (pip-compile)
```

### Testing Database
The system uses SQLite for testing with async support (`aiosqlite`). Test database is isolated from development PostgreSQL.

### Performance Considerations
- All database queries use async sessions
- Celery workers prevent API blocking on long scans
- Template rendering includes pagination for large datasets (50 resources per accordion)
- Core Web Vitals calculation uses efficient aggregation
- URL cleaning utility (`app/services/url_utils.py`) removes invisible Unicode characters
- Resource details tables use JavaScript-based pagination to handle 20k+ issues per type

### JavaScript Architecture (`app/static/js/app-minimal.js`)
**Namespace Pattern**: JavaScript functions are organized in namespaces (`clients`, `websites`) to avoid global pollution while maintaining compatibility with inline onclick handlers.

**Error Handling**: Client-side JavaScript includes proper error handling with specific validation error parsing for 422 responses, displaying user-friendly error messages via toast notifications.

**Form Data Processing**: Form submission functions automatically transform form data to match API schemas (e.g., extracting domain from full URLs, mapping form field names to API field names).

## Production Deployment

### Docker Stack
- `postgres` - PostgreSQL 15 with health checks
- `redis` - Redis 7 for Celery broker
- `app` - FastAPI application with hot reload
- `celery-worker` - Background task processor
- `celery-beat` - Scheduled task coordinator
- `adminer` - Database administration interface

### Service URLs
- Web Interface: http://localhost:8000/templated/
- API Documentation: http://localhost:8000/docs
- Database Admin: http://localhost:8080
- Health Check: http://localhost:8000/health

### Monitoring
Real-time scheduler status via `/api/v1/scheduler/status` includes worker health, queue sizes, and task completion rates.

## Troubleshooting

### Common Issues
- **Celery connection errors**: Check Redis service health
- **Database connection errors**: Verify PostgreSQL health check passes
- **Scan failures**: Check Celery worker logs for browser/network issues
- **Template errors**: Check resource detail processing in `templates.py`

### Debug Tools
```bash
make logs                # Application logs
docker-compose logs celery-worker --tail=20  # Celery worker logs
make debug               # Debug server with breakpoints (port 5678)
make profile             # Performance profiling with cProfile

# Service-specific debugging
docker-compose logs postgres --tail=20  # Database logs
docker-compose logs redis --tail=20     # Redis/Celery broker logs
docker-compose ps                       # Service status check
```

### Performance Debugging
The system includes built-in performance monitoring. Core Web Vitals analysis provides timing data. Use Adminer to inspect database query performance.

## Key Files for Common Tasks

- **Add new SEO analyzer**: Extend `app/services/seo_analyzer/` with new analyzer class, import in `seo_analyzer.py`
- **Modify issue detection**: Update `issue_detector.py` and scoring weights in `config.py`
- **Convert legacy to granular**: Add `ResourceDetailsBuilder` method in `core/resource_details.py`, update analyzer to use `IssueFactory.create_granular_issue()`
- **Add new API endpoint**: Create router in `app/routers/` following existing async patterns with `AsyncSession = Depends(get_db)`
- **Add frontend modals**: Create static templates in `components/modals/`, include in `base.html`, add JavaScript trigger functions
- **Add HTMX endpoints**: Extend `app/routers/htmx.py` for partial HTML responses (edit forms, table updates)
- **Modify template sections**: Update templates in `app/templates/components/sections/` and ensure required data in `templates.py`
- **Add background task**: Extend `app/tasks/` and register with Celery app in `celery_app.py`
- **Handle large scans**: Modify issue limiting logic in `templates.py` (MAX_ISSUES_FOR_UI constant, smart severity distribution)
- **Add table pagination**: Follow pattern in `scan_results_semrush.html` with data attributes and JavaScript functions
- **Debug scan issues**: Check Celery worker logs, verify crawl results in issue detection methods
- **Update Italian translations**: Modify issue type mappings in `templates.py` ISSUE_TYPE_INFO

## Critical Architecture Decisions

**Issue Granularity Strategy**: The system generates individual issues per resource per page (e.g., each JS file on each page = separate issue). This creates detailed actionable reports but can generate 20k+ issues for large sites. The template system uses pagination and limiting to maintain UI performance.

**Severity Escalation**: Base severities are defined in `SeverityCalculator.BASE_SEVERITIES` but can be escalated based on context (e.g., JS in `<head>` vs `<body>`, file sizes, site-wide frequency).

**Async/Sync Database Sessions**: The system maintains both async sessions (for API/web) and sync sessions (for Celery compatibility) defined in `database.py`.

**Frontend Form Handling**: The system uses a hybrid approach where create modals are statically included to avoid form persistence issues, while edit modals are loaded via HTMX with pre-populated data. This prevents the common issue where dynamically loaded forms lose user input due to DOM replacement timing.

**Granular Issue Format**: The system has evolved from simple aggregate issues to detailed granular format with intelligent suggestions. Key conversions include Italian standardization and context-aware optimization recommendations using content analysis and keyword extraction.

**Anti-Overload System**: Large scans are handled with smart issue distribution (40% critical, 35% high, 20% medium, 5% low) and prioritization of granular issues over legacy format to maintain UI performance while maximizing actionable insights.

## Commercial Context

This platform targets digital agencies and enterprise customers as a cost-effective alternative to SEMrush/Ahrefs, focusing on bulk monitoring capabilities and API accessibility. The architecture supports agency-scale operations with white-label deployment options.