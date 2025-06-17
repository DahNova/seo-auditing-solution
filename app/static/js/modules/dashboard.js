// SEO Auditing Solution - Dashboard Module
class DashboardModule {
    constructor() {
        this.charts = {};
        this.realTimeInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }

    setupEventListeners() {
        // Subscribe to data changes
        appState.subscribe('data.clients', () => this.updateStats());
        appState.subscribe('data.websites', () => this.updateStats());
        appState.subscribe('data.scans', () => this.updateStats());
    }

    async loadData() {
        try {
            appState.setLoading('dashboard', true);
            
            // Load all required data
            const [clients, websites, scans] = await Promise.all([
                apiClient.getClients(),
                apiClient.getWebsites(),
                apiClient.getScans()
            ]);

            // Enrich websites with client data
            const enrichedWebsites = websites.map(website => {
                const client = clients.find(c => c.id === website.client_id);
                return {
                    ...website,
                    client: client || null
                };
            });

            // Enrich clients with website counts
            const enrichedClients = clients.map(client => ({
                ...client,
                websites: enrichedWebsites.filter(w => w.client_id === client.id),
                is_active: true
            }));

            // Enrich scans with website and client data
            const enrichedScans = scans.map(scan => {
                const website = enrichedWebsites.find(w => w.id === scan.website_id);
                return {
                    ...scan,
                    website: website || null
                };
            });

            // Update state with enriched data
            appState.setData('clients', enrichedClients);
            appState.setData('websites', enrichedWebsites);
            appState.setData('scans', enrichedScans);

            this.updateDashboard();

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            utils.showToast('Errore nel caricamento dei dati', 'error');
        } finally {
            appState.setLoading('dashboard', false);
        }
    }

    updateDashboard() {
        this.updateStats();
        this.renderRecentScansList();
        this.renderHealthOverview();
        this.renderCriticalAlerts();
        this.renderActivityFeed();
    }

    updateStats() {
        const clients = appState.getData('clients') || [];
        const websites = appState.getData('websites') || [];
        const scans = appState.getData('scans') || [];

        // Update header stats
        this.updateElement('clients-count-header', clients.length);
        this.updateElement('total-websites-header', websites.length);

        // Update main stats cards
        this.updateElement('total-clients', clients.length);
        this.updateElement('total-websites', websites.length);
        this.updateElement('total-scans', scans.length);

        // Calculate derived stats
        const activeWebsites = websites.filter(w => w.is_active).length;
        this.updateElement('active-websites', activeWebsites);

        const completedScans = scans.filter(s => s.status === 'completed');
        const criticalIssues = completedScans.reduce((total, scan) => {
            return total + (scan.critical_issues_count || 0);
        }, 0);
        this.updateElement('critical-issues-total', criticalIssues);

        // Recent scan time
        const sortedScans = [...scans].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        const lastScanTime = sortedScans.length > 0 ? 
            utils.formatRelativeTime(sortedScans[0].created_at) : 'mai';
        this.updateElement('last-scan-time', lastScanTime);

        // Growth calculation (mock for now)
        const clientsGrowth = Math.max(0, clients.length - 10);
        this.updateElement('clients-growth', `+${clientsGrowth}`);

        // Mini stats for dashboard header
        const activeScans = scans.filter(s => s.status === 'running').length;
        this.updateElement('mini-active-scans', activeScans);
        this.updateElement('mini-last-update', utils.formatRelativeTime(new Date()));
    }

    renderRecentScansList() {
        const container = document.getElementById('recent-scans-list');
        if (!container) return;

        const scans = appState.getData('scans') || [];
        const recentScans = [...scans]
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 5);

        if (recentScans.length === 0) {
            container.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="bi bi-search fs-1 opacity-50"></i>
                    <p class="mt-2">Nessuna scansione recente</p>
                    <button class="btn btn-primary btn-sm" onclick="app.showNewScanModal()">
                        <i class="bi bi-plus"></i> Avvia Prima Scansione
                    </button>
                </div>
            `;
            return;
        }

        container.innerHTML = recentScans.map(scan => `
            <div class="scan-item-modern" onclick="scanResults.viewResults(${scan.id})">
                <div class="scan-info">
                    <div class="scan-website">${scan.website?.domain || 'N/A'}</div>
                    <div class="scan-meta">
                        <span class="scan-date">${utils.formatRelativeTime(scan.created_at)}</span>
                        <span class="mx-2">•</span>
                        <span class="scan-pages">${scan.pages_found || scan.pages_scanned || 0} pagine</span>
                    </div>
                </div>
                <div class="scan-status">
                    ${utils.getStatusBadge(scan.status)}
                    ${scan.seo_score ? utils.getSEOScoreBadge(scan.seo_score) : ''}
                </div>
            </div>
        `).join('');
    }

    renderHealthOverview() {
        const scans = appState.getData('scans') || [];
        const completedScans = scans.filter(s => s.status === 'completed' && s.seo_score);
        
        if (completedScans.length === 0) {
            this.updateElement('overall-score', '--');
            return;
        }

        // Calculate average score
        const averageScore = Math.round(
            completedScans.reduce((sum, scan) => sum + scan.seo_score, 0) / completedScans.length
        );
        
        this.updateElement('overall-score', averageScore);

        // Update health insights
        this.renderHealthInsights(completedScans, averageScore);
        
        // Update chart if available
        this.updateHealthChart(completedScans);
    }

    renderHealthInsights(scans, averageScore) {
        const container = document.getElementById('health-insights');
        if (!container) return;

        const insights = [];
        
        if (averageScore >= 90) {
            insights.push({ type: 'success', text: 'Eccellente! I tuoi siti hanno performance SEO ottimali.' });
        } else if (averageScore >= 70) {
            insights.push({ type: 'info', text: 'Buone performance SEO, con margini di miglioramento.' });
        } else {
            insights.push({ type: 'warning', text: 'Le performance SEO necessitano di attenzione.' });
        }

        // Add specific insights
        const criticalCount = scans.reduce((sum, s) => sum + (s.critical_issues_count || 0), 0);
        if (criticalCount > 0) {
            insights.push({ 
                type: 'danger', 
                text: `${criticalCount} problemi critici rilevati richiedono attenzione immediata.` 
            });
        }

        container.innerHTML = insights.map(insight => `
            <div class="insight-item alert alert-${insight.type} py-2 px-3 mb-2">
                <i class="bi bi-lightbulb me-2"></i>
                <small>${insight.text}</small>
            </div>
        `).join('');
    }

    updateHealthChart(scans) {
        const ctx = document.getElementById('dashboardHealthChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.charts.health) {
            this.charts.health.destroy();
        }

        // Prepare data
        const scoreRanges = { excellent: 0, good: 0, fair: 0, poor: 0 };
        scans.forEach(scan => {
            const score = scan.seo_score;
            if (score >= 90) scoreRanges.excellent++;
            else if (score >= 70) scoreRanges.good++;
            else if (score >= 50) scoreRanges.fair++;
            else scoreRanges.poor++;
        });

        this.charts.health = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Eccellente (90+)', 'Buono (70-89)', 'Sufficiente (50-69)', 'Scarso (<50)'],
                datasets: [{
                    data: [scoreRanges.excellent, scoreRanges.good, scoreRanges.fair, scoreRanges.poor],
                    backgroundColor: ['#10b981', '#06b6d4', '#f59e0b', '#ef4444'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    renderCriticalAlerts() {
        const container = document.getElementById('critical-alerts');
        if (!container) return;

        const scans = appState.getData('scans') || [];
        const criticalScans = scans.filter(s => s.status === 'completed' && (s.critical_issues_count || 0) > 0);

        this.updateElement('alert-counter', criticalScans.length);

        if (criticalScans.length === 0) {
            container.innerHTML = `
                <div class="text-center p-3 text-muted">
                    <i class="bi bi-shield-check fs-1 text-success opacity-50"></i>
                    <p class="mt-2 mb-0">Nessun problema critico rilevato</p>
                </div>
            `;
            return;
        }

        container.innerHTML = criticalScans.slice(0, 5).map(scan => `
            <div class="alert-item-modern" onclick="scanResults.viewResults(${scan.id})">
                <div class="alert-icon">
                    <i class="bi bi-exclamation-triangle text-danger"></i>
                </div>
                <div class="alert-content">
                    <div class="alert-title">${scan.website?.domain || 'Sito sconosciuto'}</div>
                    <div class="alert-desc">${scan.critical_issues_count} problemi critici</div>
                </div>
                <div class="alert-time">${utils.formatRelativeTime(scan.created_at)}</div>
            </div>
        `).join('');
    }

    renderActivityFeed() {
        const container = document.getElementById('activity-feed');
        if (!container) return;

        const scans = appState.getData('scans') || [];
        const recentActivity = [...scans]
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 10);

        if (recentActivity.length === 0) {
            container.innerHTML = `
                <div class="text-center p-3 text-muted">
                    <i class="bi bi-clock-history fs-1 opacity-50"></i>
                    <p class="mt-2 mb-0">Nessuna attività recente</p>
                </div>
            `;
            return;
        }

        container.innerHTML = recentActivity.map(activity => `
            <div class="activity-item">
                <div class="activity-time">${utils.formatRelativeTime(activity.created_at)}</div>
                <div class="activity-content">
                    <div class="activity-icon">
                        <i class="bi bi-search"></i>
                    </div>
                    <div class="activity-text">
                        Scansione di <strong>${activity.website?.domain || 'sito sconosciuto'}</strong>
                        ${utils.getStatusBadge(activity.status)}
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    startRealTimeUpdates() {
        // Update every 30 seconds
        this.realTimeInterval = setInterval(() => {
            this.loadData();
        }, 30000);
    }

    stopRealTimeUpdates() {
        if (this.realTimeInterval) {
            clearInterval(this.realTimeInterval);
            this.realTimeInterval = null;
        }
    }

    destroy() {
        this.stopRealTimeUpdates();
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};
    }
}

// Export module
window.dashboard = new DashboardModule();