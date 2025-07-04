# 🚀 SEO Auditing Solution
### Piattaforma Professionale di Monitoraggio SEO Enterprise

Una soluzione completa di analisi SEO progettata come alternativa enterprise a SEMrush/Ahrefs, ottimizzata per agenzie digitali e operazioni su larga scala (100-500+ siti web).

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7-red.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)

---

## 🎯 Caratteristiche Principali

### 📊 **Analisi SEO Completa**
- **Analisi Granulare**: Ogni risorsa (CSS, JS, immagini) genera issue specifiche per report dettagliati
- **Core Web Vitals**: Monitoraggio performance e metriche di velocità
- **SEO Tecnico**: Schema markup, meta tag, struttura HTML, accessibilità
- **Analisi Contenuti**: Qualità del contenuto, ottimizzazione keyword, leggibilità

### 🏢 **Sistema Enterprise URL Discovery**
- **Strategia Sitemap-First**: Priorità alle URL strutturate per processing efficiente
- **Discovery Multi-Fonte**: Sitemap XML, robots.txt, crawling intelligente
- **Gestione Crawl Budget**: Processamento intelligente per siti di grandi dimensioni
- **Metadata Completi**: Tracking source discovery, priorità, change frequency

### ⚡ **Architettura High-Performance**
- **Async/Await Pattern**: Tutte le operazioni database e crawling sono asincrone
- **Modular Template System**: Architettura componenti con 75% riduzione duplicazione codice
- **Smart Issue Distribution**: Limitazione intelligente a 2000 issue per UI performance
- **Database Optimization**: Query ottimizzate con eager loading per prevenire N+1

### 🔄 **Processing Background**
- **Celery + Redis**: Task asincroni per scansioni long-running
- **Queue Dedicate**: Separazione scansioni e monitoraggio per performance ottimali
- **Retry Logic**: Gestione errori con exponential backoff
- **Real-time Monitoring**: Status worker e dimensioni queue in tempo reale

---

## 🚀 Quick Start

### Prerequisiti
- Docker & Docker Compose
- 4GB RAM minimo
- Python 3.11+ (per sviluppo locale)

### Avvio Rapido con Docker

```bash
# Clone della repository
git clone <repository-url>
cd seo-auditing-solution

# Avvio stack completo
make docker-run
# oppure: docker-compose up -d

# Verifica stato servizi
make health
```

### Accesso Interfacce

| Servizio | URL | Descrizione |
|----------|-----|-------------|
| **Web Interface** | http://localhost:8000/templated/ | Dashboard principale SEO |
| **API Documentation** | http://localhost:8000/docs | Swagger UI interattivo |
| **Database Admin** | http://localhost:8080 | Adminer (User: seo_user, Pass: seo_password) |
| **Health Check** | http://localhost:8000/health | Status sistema |

---

## 🏗️ Architettura del Sistema

### **Pattern Architetturali Core**

#### **Design Async-First**
Tutte le operazioni database, web crawling e API endpoint utilizzano asyncio con sessioni separate sync/async per compatibilità Celery.

#### **Repository Pattern**
Layer services (`app/services/`) astrae operazioni database da route API (`app/routers/`). Ogni service gestisce business logic mentre le route si concentrano su HTTP concerns.

#### **Sistema Granulare di Analisi**
L'analizzatore SEO genera issue individuali per risorsa (es. ogni file CSS bloccante = issue separato) anziché conteggi aggregati.

### **Componenti del Sistema**

```
📁 Struttura Principale
├── app/
│   ├── services/
│   │   ├── seo_analyzer/         # Engine analisi SEO multi-layer
│   │   ├── enterprise_scan_service.py  # Orchestratore scansioni enterprise
│   │   ├── url_discovery_service.py    # Discovery URL multi-fonte
│   │   └── sitemap_parser.py           # Parser sitemap XML completo
│   ├── routers/
│   │   ├── templates/            # Router template modulare
│   │   │   ├── __init__.py      # Router principale sezioni
│   │   │   └── scan_results.py  # Handler dedicato risultati scan
│   │   └── api/v1/              # API REST endpoint
│   ├── models/                   # Modelli database SQLAlchemy
│   ├── tasks/                    # Task Celery background
│   └── templates/               # Template Jinja2 componenti
└── alembic/                     # Migrations database
```

### **Gerarchia Database**
```
Client → Website → Scan → Page → Issue
                 → Schedule
                 → RobotsSnapshot  
                 → SitemapSnapshot
```

---

## 🛠️ Sviluppo

### **Comandi Essenziali**

```bash
# Sviluppo con hot reload
make dev

# Testing completo
make test                # Suite completa test
make test-unit           # Solo unit test veloci
make test-api            # Test endpoint API
make test-seo            # Test analizzatore SEO

# Quality & Performance
make pre-commit          # Format + lint + unit test
make full-test           # Test + linting + type checking
make test-coverage       # Report copertura test (80% minimo)

# Database
make db-shell            # Shell PostgreSQL interattiva
make migrate             # Applica migration pending
make migrate-create      # Crea nuova migration

# Docker & Debug
make logs                # Log applicazione
make debug               # Server debug con breakpoint (porta 5678)
make clean               # Pulisci cache e file temporanei
```

### **Workflow Development**

1. **Setup Environment**
   ```bash
   make docker-run     # Avvia stack completo
   make dev           # Development server locale
   ```

2. **Development Cycle**
   ```bash
   make pre-commit    # Prima di ogni commit
   make test-working  # Test rapidi durante sviluppo
   make logs         # Monitor errori
   ```

3. **Database Changes**
   ```bash
   make migrate-create  # Crea migration
   make migrate        # Applica modifiche
   ```

---

## 📊 Funzionalità Enterprise

### **Sistema Discovery URL Avanzato**

#### **Strategia Multi-Fase**
1. **Discovery Phase**: Parsing sitemap XML con metadata completi
2. **Priority Processing**: Queue intelligente basata su priority scoring
3. **SEO Analysis**: Analisi completa ogni URL scoperto

#### **Features Enterprise**
- **Processing 10k+ Pagine**: Gestione efficiente siti di grandi dimensioni
- **Metadata Sitemap**: Changefreq, priority, lastmod processing
- **Source Tracking**: Tracciamento come ogni URL è stato scoperto
- **Crawl Budget Management**: Controllo risorse crawling intelligente

### **Performance & Scalabilità**

#### **Ottimizzazioni Database**
- **Eager Loading**: `selectinload()` previene query N+1
- **Smart Distribution**: Caricamento intelligente per dataset grandi
- **Pagination Avanzata**: Controlli performance-aware
- **Indexing Strategico**: Index ottimizzati per query enterprise

#### **Template Performance**
- **Architettura Modulare**: Sistema componenti con caching template
- **CSS/JS Ottimizzato**: Caricamento specializzato con prevenzione FOUC
- **Component Reuse**: Riduzione 75% duplicazione codice

---

## 🔧 Configurazione

### **Variabili Ambiente Principali**

```bash
# Database
DATABASE_URL=postgresql://seo_user:seo_password@localhost:5432/seo_db

# Redis/Celery  
REDIS_URL=redis://localhost:6379/0

# SEO Configuration
MAX_PAGES_PER_SCAN=1000
CRAWL_DELAY_SECONDS=1
MAX_ISSUES_FOR_UI=2000

# Performance
TEMPLATE_CACHE_ENABLED=true
EAGER_LOADING_ENABLED=true
```

### **Soglie SEO Configurabili**
- Lunghezza title/meta description (standard 2024/2025)
- Soglie ottimizzazione immagini
- Pesi scoring qualità contenuto
- Mapping severità issue granulari

---

## 🚨 Troubleshooting

### **Problemi Comuni**

**Errori Connessione Celery**
```bash
docker-compose logs redis --tail=20
docker-compose logs celery-worker --tail=20
```

**Errori Database**
```bash
make db-shell  # Verifica connessione
docker-compose logs postgres --tail=20
```

**Fallimenti Scan**
```bash
make logs  # Log applicazione
docker-compose logs celery-worker --tail=50
```

**Performance Issue**
```bash
make profile  # Profiling performance
# Verifica query database tramite Adminer
```

### **Debug Tools**

```bash
# Monitoring servizi
docker-compose ps              # Status servizi
make health                   # Health check completo

# Log specifici
make logs                     # Log applicazione
docker-compose logs [service] # Log servizio specifico

# Database debugging
make db-shell                 # Shell PostgreSQL
# Adminer: http://localhost:8080
```

---

## 📈 Monitoraggio & Analytics

### **Metriche Real-time**
- **Worker Status**: Salute worker Celery in tempo reale
- **Queue Monitoring**: Dimensioni queue e task completion rate
- **Performance Metrics**: Core Web Vitals aggregati
- **Discovery Analytics**: Source tracking e metadata processing

### **Dashboard Professionale**
- **SEMrush-inspired Design**: Interface moderna e professionale
- **Nested Accordions**: Organizzazione gerarchica issue (Severità → Tipo → Risorse)
- **Tables Responsive**: Tabelle risorse con pagination JavaScript
- **Real-time Updates**: HTMX per aggiornamenti contenuti dinamici

---

## 🎯 Target Commercial

Questa piattaforma è progettata per:

- **Agenzie Digitali**: Monitoraggio bulk clienti con white-label deployment
- **Enterprise Customers**: Alternative cost-effective a SEMrush/Ahrefs
- **SEO Professionals**: Capabilities API complete per integrazioni custom
- **Development Teams**: Architettura moderna scalabile per customization

### **Vantaggi Competitivi**
- ✅ **Costi Ridotti**: Soluzione on-premise senza costi per-seat
- ✅ **Controllo Completo**: Dati e analisi completamente sotto controllo
- ✅ **Scalabilità**: Architettura async per handling 500+ websites
- ✅ **Customization**: Codebase aperto per adattamenti specifici
- ✅ **API-First**: Integrazione completa con sistemi esistenti

---

## 📝 License

Questo progetto è rilasciato sotto licenza MIT. Vedi file `LICENSE` per dettagli completi.

---

## 🤝 Contributi

I contributi sono benvenuti! Per contribuire:

1. Fork del progetto
2. Crea feature branch (`git checkout -b feature/nuova-funzionalita`)
3. Commit modifiche (`git commit -m 'Aggiunge nuova funzionalità'`)
4. Push branch (`git push origin feature/nuova-funzionalita`)
5. Apri Pull Request

### **Development Guidelines**
- Segui patterns async/await esistenti
- Mantieni copertura test >80%
- Usa `make pre-commit` prima di ogni commit
- Documenta nuove feature in CLAUDE.md

---

## 📞 Support

Per supporto tecnico:
- **Issues**: Usa GitHub Issues per bug report e feature request
- **Documentation**: Consulta CLAUDE.md per dettagli architettura
- **API Docs**: http://localhost:8000/docs per documentazione interattiva

---

*Sviluppato con ❤️ per la community SEO italiana*