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

# Coverage and quality
make test-coverage       # Test coverage report
make full-test           # Tests + linting + type checking

# Development workflow
make pre-commit          # Format + lint + unit tests
make quick-test          # Fast tests (unit + API)
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
make backup-db           # Backup database
make test-db             # Reset test database
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

**Granular Resource Details**: Issues contain structured JSON in the `element` field with specific resource information (URLs, file sizes, optimization recommendations). Each resource generates individual issues rather than aggregate counts.

**Performance-Aware Issue Limiting**: For large scans (>5000 issues), the system automatically limits to 2000 issues for UI performance, distributed across severity levels.

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

**Component-Based Structure**:
- `components/sections/` - Main page sections (SEMrush-inspired design)
- `components/modals/` - Form modals for CRUD operations
- `components/cards/` - Metric display components

**Template Router** (`app/routers/templates.py`): Processes database data for template consumption, including resource detail grouping for granular issue display with pagination support.

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
- `/api/v1/clients/` - Client CRUD
- `/api/v1/websites/` - Website management 
- `/api/v1/scans/` - Scan operations including `/api/v1/scans/{id}/results`
- `/api/v1/scheduler/` - Real-time worker monitoring and queue management
- `/templated/` - Server-side rendered interface

### Error Handling
HTTP exceptions use FastAPI's `HTTPException`. Database errors include rollback handling. Celery tasks have retry logic with exponential backoff.

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
make debug               # Debug server with breakpoints
```

### Performance Debugging
The system includes built-in performance monitoring. Core Web Vitals analysis provides timing data. Use Adminer to inspect database query performance.

## Key Files for Common Tasks

- **Add new SEO analyzer**: Extend `app/services/seo_analyzer/` with new analyzer class
- **Modify issue detection**: Update `issue_detector.py` and scoring weights in `config.py`
- **Add new API endpoint**: Create router in `app/routers/` following existing async patterns
- **Modify frontend**: Update templates in `app/templates/components/`
- **Add background task**: Extend `app/tasks/` and register with Celery app
- **Create granular issues**: Use `ResourceDetailsBuilder` and `IssueFactory` from `core/resource_details.py`
- **Handle large scans**: Modify issue limiting logic in `templates.py` (MAX_ISSUES_FOR_UI constant)
- **Add table pagination**: Follow pattern in `scan_results_semrush.html` with data attributes and JavaScript functions

## Critical Architecture Decisions

**Issue Granularity Strategy**: The system generates individual issues per resource per page (e.g., each JS file on each page = separate issue). This creates detailed actionable reports but can generate 20k+ issues for large sites. The template system uses pagination and limiting to maintain UI performance.

**Severity Escalation**: Base severities are defined in `SeverityCalculator.BASE_SEVERITIES` but can be escalated based on context (e.g., JS in `<head>` vs `<body>`, file sizes, site-wide frequency).

**Async/Sync Database Sessions**: The system maintains both async sessions (for API/web) and sync sessions (for Celery compatibility) defined in `database.py`.

## Commercial Context

This platform targets digital agencies and enterprise customers as a cost-effective alternative to SEMrush/Ahrefs, focusing on bulk monitoring capabilities and API accessibility. The architecture supports agency-scale operations with white-label deployment options.