// SEO Auditing Solution - Frontend JavaScript
class SEOAuditingApp {
    constructor() {
        this.apiBase = '/api/v1';
        this.currentSection = 'dashboard';
        this.clients = [];
        this.websites = [];
        this.scans = [];
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupModernFeatures();
        await this.loadInitialData();
        this.updateDashboard();
        this.startRealTimeUpdates();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.closest('[data-section]').dataset.section;
                this.showSection(section);
            });
        });

        // Search functionality
        const clientSearch = document.getElementById('client-search');
        if (clientSearch) {
            clientSearch.addEventListener('input', () => this.filterClients());
        }

        // Client filter
        const clientFilter = document.getElementById('client-filter');
        if (clientFilter) {
            clientFilter.addEventListener('change', () => this.filterClients());
        }

        // Modal reset listeners
        const addClientModal = document.getElementById('addClientModal');
        if (addClientModal) {
            addClientModal.addEventListener('hidden.bs.modal', () => this.resetAddClientModal());
        }

        const addWebsiteModal = document.getElementById('addWebsiteModal');
        if (addWebsiteModal) {
            addWebsiteModal.addEventListener('hidden.bs.modal', () => this.resetAddWebsiteModal());
        }

        const newScanModal = document.getElementById('newScanModal');
        if (newScanModal) {
            newScanModal.addEventListener('hidden.bs.modal', () => this.resetNewScanModal());
        }

        const scheduleModal = document.getElementById('scheduleModal');
        if (scheduleModal) {
            scheduleModal.addEventListener('hidden.bs.modal', () => this.resetScheduleModal());
        }

        const editScheduleModal = document.getElementById('editScheduleModal');
        if (editScheduleModal) {
            editScheduleModal.addEventListener('hidden.bs.modal', () => this.resetEditScheduleModal());
        }
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.style.display = 'none';
        });

        // Show selected section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
        }

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        this.currentSection = sectionName;

        // Load section-specific data
        switch (sectionName) {
            case 'clients':
                this.loadClients();
                break;
            case 'websites':
                this.loadWebsites();
                break;
            case 'scans':
                this.loadScans();
                break;
            case 'scheduler':
                this.loadSchedulerData();
                break;
        }
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadClients(),
                this.loadWebsites(),
                this.loadScans()
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showAlert('Errore nel caricamento dei dati', 'danger');
        }
    }

    async loadClients() {
        try {
            const response = await fetch(`${this.apiBase}/clients/`);
            this.clients = await response.json();
            this.renderClientsTable();
            this.populateClientDropdown();
        } catch (error) {
            console.error('Error loading clients:', error);
        }
    }

    async loadWebsites() {
        try {
            const response = await fetch(`${this.apiBase}/websites/`);
            this.websites = await response.json();
            this.renderWebsitesTable();
        } catch (error) {
            console.error('Error loading websites:', error);
        }
    }

    async loadScans() {
        try {
            const response = await fetch(`${this.apiBase}/scans/`);
            this.scans = await response.json();
            this.renderScansTable();
        } catch (error) {
            console.error('Error loading scans:', error);
        }
    }

    renderClientsTable() {
        const tbody = document.getElementById('clients-table-body');
        if (!tbody) return;

        if (this.clients.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
                        <i class="bi bi-people h2"></i><br>
                        Nessun cliente trovato
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.clients.map(client => {
            const clientWebsites = this.websites.filter(w => w.client_id === client.id);
            const lastUpdate = client.updated_at ? 
                new Date(client.updated_at).toLocaleDateString('it-IT') : 
                new Date(client.created_at).toLocaleDateString('it-IT');

            return `
                <tr>
                    <td>
                        <strong>${this.escapeHtml(client.name)}</strong>
                        ${client.description ? `<br><small class="text-muted">${this.escapeHtml(client.description)}</small>` : ''}
                    </td>
                    <td>
                        ${client.contact_email ? 
                            `<a href="mailto:${client.contact_email}">${this.escapeHtml(client.contact_email)}</a>` : 
                            '<span class="text-muted">N/A</span>'
                        }
                    </td>
                    <td>
                        <span class="badge bg-primary">${clientWebsites.length} siti</span>
                    </td>
                    <td>${lastUpdate}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="app.editClient(${client.id})" title="Modifica">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-outline-success" onclick="app.viewClientWebsites(${client.id})" title="Visualizza siti">
                                <i class="bi bi-globe"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="app.deleteClient(${client.id})" title="Elimina">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    renderWebsitesTable() {
        const tbody = document.getElementById('websites-table-body');
        if (!tbody) return;

        if (this.websites.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted py-4">
                        <i class="bi bi-globe h2"></i><br>
                        Nessun sito web trovato
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.websites.map(website => {
            const client = this.clients.find(c => c.id === website.client_id);
            const lastScan = website.last_scan_at ? 
                new Date(website.last_scan_at).toLocaleDateString('it-IT') : 
                'Mai';

            const statusBadge = website.is_active ? 
                '<span class="badge bg-success">Attivo</span>' : 
                '<span class="badge bg-secondary">Inattivo</span>';

            const frequencyText = {
                'daily': 'Giornaliera',
                'weekly': 'Settimanale',
                'monthly': 'Mensile'
            }[website.scan_frequency] || website.scan_frequency;

            return `
                <tr>
                    <td>
                        <a href="${website.domain}" target="_blank" class="text-decoration-none">
                            ${this.escapeHtml(website.domain)}
                            <i class="bi bi-box-arrow-up-right ms-1"></i>
                        </a>
                    </td>
                    <td>
                        <strong>${this.escapeHtml(website.name || 'N/A')}</strong>
                        ${website.description ? `<br><small class="text-muted">${this.escapeHtml(website.description)}</small>` : ''}
                    </td>
                    <td>${client ? this.escapeHtml(client.name) : 'N/A'}</td>
                    <td>${frequencyText}</td>
                    <td>${lastScan}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-warning" onclick="app.startScan(${website.id})" title="Avvia scansione">
                                <i class="bi bi-play-circle"></i>
                            </button>
                            <button class="btn btn-outline-primary" onclick="app.editWebsite(${website.id})" title="Modifica">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="app.deleteWebsite(${website.id})" title="Elimina">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    renderScansTable() {
        const tbody = document.getElementById('scans-table-body');
        if (!tbody) return;

        if (this.scans.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted py-4">
                        <i class="bi bi-search h2"></i><br>
                        Nessuna scansione trovata
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.scans.map(scan => {
            const website = this.websites.find(w => w.id === scan.website_id);
            const startDate = new Date(scan.started_at).toLocaleDateString('it-IT');
            
            let statusBadge = '';
            switch (scan.status) {
                case 'completed':
                    statusBadge = '<span class="badge bg-success">Completata</span>';
                    break;
                case 'running':
                    statusBadge = '<span class="badge bg-info">In corso</span>';
                    break;
                case 'pending':
                    statusBadge = '<span class="badge bg-warning">In attesa</span>';
                    break;
                case 'failed':
                    statusBadge = '<span class="badge bg-danger">Fallita</span>';
                    break;
                case 'cancelled':
                    statusBadge = '<span class="badge bg-secondary">Annullata</span>';
                    break;
                default:
                    statusBadge = '<span class="badge bg-secondary">Sconosciuto</span>';
            }

            const seoScore = scan.seo_score ? 
                `<span class="seo-score ${this.getSeoScoreClass(scan.seo_score)}">${scan.seo_score}/100</span>` : 
                'N/A';

            return `
                <tr>
                    <td>${website ? this.escapeHtml(website.domain) : 'N/A'}</td>
                    <td>${startDate}</td>
                    <td>${statusBadge}</td>
                    <td>${scan.pages_scanned || 0}</td>
                    <td>
                        <span class="badge bg-warning">${scan.total_issues || 0}</span>
                    </td>
                    <td>${seoScore}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            ${scan.status === 'completed' ? 
                                `<button class="btn btn-outline-info" onclick="app.viewScanResults(${scan.id})" title="Visualizza risultati">
                                    <i class="bi bi-eye"></i>
                                </button>
                                <button class="btn btn-outline-primary" onclick="app.downloadReport(${scan.id})" title="Scarica report">
                                    <i class="bi bi-download"></i>
                                </button>` : 
                                ''
                            }
                            ${scan.status === 'failed' || scan.status === 'pending' ? 
                                `<button class="btn btn-outline-warning" onclick="app.retryScan(${scan.id})" title="Riprova scansione">
                                    <i class="bi bi-arrow-clockwise"></i>
                                </button>` : 
                                ''
                            }
                            ${scan.status === 'running' || scan.status === 'pending' ? 
                                `<button class="btn btn-outline-secondary" onclick="app.cancelScan(${scan.id})" title="Annulla scansione">
                                    <i class="bi bi-stop-circle"></i>
                                </button>` : 
                                ''
                            }
                            <button class="btn btn-outline-danger" onclick="app.deleteScan(${scan.id})" title="Elimina scansione">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    updateDashboard() {
        // Basic stats
        document.getElementById('total-clients').textContent = this.clients.length;
        document.getElementById('total-websites').textContent = this.websites.length;
        document.getElementById('total-scans').textContent = this.scans.length;
        
        // Enhanced metrics
        const activeWebsites = this.websites.filter(w => w.is_active).length;
        const activeWebsitesElement = document.getElementById('active-websites');
        if (activeWebsitesElement) {
            activeWebsitesElement.textContent = activeWebsites;
        }
        
        // Calculate critical issues across all scans
        const criticalIssues = this.scans.reduce((total, scan) => {
            return total + (scan.critical_issues || 0);
        }, 0);
        const criticalElement = document.getElementById('critical-issues-total');
        if (criticalElement) {
            criticalElement.textContent = criticalIssues;
        }
        
        // Last scan time
        const lastScan = this.scans.length > 0 ? 
            new Date(this.scans[0].started_at).toLocaleDateString('it-IT') : '-';
        const lastScanElement = document.getElementById('last-scan-time');
        if (lastScanElement) {
            lastScanElement.textContent = lastScan;
        }
        
        // Growth metrics (mock data for now)
        const growthElement = document.getElementById('clients-growth');
        if (growthElement) {
            growthElement.textContent = '+' + Math.max(0, this.clients.length - 5);
        }
        
        // Render enhanced dashboard components
        this.renderRecentScansList();
        this.renderDashboardHealthChart();
        this.renderCriticalAlerts();
        this.renderActivityFeed();
        this.renderHealthInsights();
    }
    
    renderRecentScansList() {
        const container = document.getElementById('recent-scans-list');
        if (!container) return;
        
        const recentScans = this.scans.slice(0, 5); // Last 5 scans
        
        if (recentScans.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-3">Nessuna scansione recente</p>';
            return;
        }
        
        container.innerHTML = recentScans.map(scan => {
            const website = this.websites.find(w => w.id === scan.website_id);
            const statusClass = {
                'completed': 'success',
                'running': 'primary',
                'failed': 'danger',
                'pending': 'warning'
            }[scan.status] || 'secondary';
            
            return `
                <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${website?.domain || 'N/A'}</h6>
                        <small class="text-muted">
                            ${new Date(scan.started_at).toLocaleDateString('it-IT')} • 
                            ${scan.pages_scanned || 0} pagine • 
                            ${scan.total_issues || 0} problemi
                        </small>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-${statusClass} mb-1">${this.formatScanStatus(scan.status)}</span>
                        ${scan.status === 'completed' ? 
                            `<br><button class="btn btn-sm btn-outline-primary" onclick="app.viewScanResults(${scan.id})">
                                <i class="bi bi-eye"></i>
                            </button>` : ''
                        }
                    </div>
                </div>
            `;
        }).join('');
    }
    
    renderDashboardHealthChart() {
        const ctx = document.getElementById('dashboardHealthChart');
        if (!ctx) return;
        
        // Aggregate health data across all scans
        const healthData = this.calculateOverallHealth();
        
        if (this.dashboardChart) {
            this.dashboardChart.destroy();
        }
        
        this.dashboardChart = new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Siti Sani', 'Problemi Moderati', 'Problemi Critici'],
                datasets: [{
                    data: [healthData.healthy, healthData.moderate, healthData.critical],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    }
                }
            }
        });
    }
    
    calculateOverallHealth() {
        let healthy = 0, moderate = 0, critical = 0;
        
        this.scans.forEach(scan => {
            const criticalIssues = scan.critical_issues || 0;
            const totalIssues = scan.total_issues || 0;
            
            if (criticalIssues > 0) {
                critical++;
            } else if (totalIssues > 5) {
                moderate++;
            } else {
                healthy++;
            }
        });
        
        return { healthy, moderate, critical };
    }
    
    renderCriticalAlerts() {
        const container = document.getElementById('critical-alerts');
        if (!container) return;
        
        const criticalScans = this.scans.filter(scan => 
            (scan.critical_issues || 0) > 0 || scan.status === 'failed'
        ).slice(0, 3);
        
        if (criticalScans.length === 0) {
            container.innerHTML = `
                <div class="text-center py-3">
                    <i class="bi bi-check-circle-fill text-success fs-2"></i>
                    <div class="mt-2">
                        <h6 class="text-success">Nessun Alert Critico</h6>
                        <small class="text-muted">Tutti i siti sono in buone condizioni</small>
                    </div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = criticalScans.map(scan => {
            const website = this.websites.find(w => w.id === scan.website_id);
            return `
                <div class="alert alert-danger alert-dismissible fade show p-3 mb-2">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        <div class="flex-grow-1">
                            <strong>${website?.domain || 'N/A'}</strong>
                            <br><small>${scan.critical_issues || 0} problemi critici rilevati</small>
                        </div>
                        <button class="btn btn-sm btn-outline-danger" onclick="app.viewScanResults(${scan.id})">
                            Risolvi
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    renderActivityFeed() {
        const container = document.getElementById('activity-feed');
        if (!container) return;
        
        // Generate activity feed from recent actions
        const activities = this.generateActivityFeed();
        
        container.innerHTML = activities.map(activity => `
            <div class="d-flex mb-3">
                <div class="flex-shrink-0">
                    <div class="bg-${activity.color} bg-opacity-10 p-2 rounded-circle">
                        <i class="bi ${activity.icon} text-${activity.color}"></i>
                    </div>
                </div>
                <div class="flex-grow-1 ms-3">
                    <h6 class="mb-1 small">${activity.title}</h6>
                    <p class="text-muted small mb-1">${activity.description}</p>
                    <small class="text-muted">${activity.time}</small>
                </div>
            </div>
        `).join('');
    }
    
    generateActivityFeed() {
        const activities = [];
        
        // Recent scans
        this.scans.slice(0, 3).forEach(scan => {
            const website = this.websites.find(w => w.id === scan.website_id);
            activities.push({
                icon: 'bi-search',
                color: scan.status === 'completed' ? 'success' : 'warning',
                title: 'Scansione completata',
                description: `${website?.domain || 'N/A'} - ${scan.total_issues || 0} problemi trovati`,
                time: new Date(scan.started_at).toLocaleDateString('it-IT')
            });
        });
        
        // Recent websites
        this.websites.slice(0, 2).forEach(website => {
            activities.push({
                icon: 'bi-globe',
                color: 'info',
                title: 'Nuovo sito aggiunto',
                description: website.domain,
                time: new Date(website.created_at || Date.now()).toLocaleDateString('it-IT')
            });
        });
        
        return activities.slice(0, 5);
    }
    
    renderHealthInsights() {
        const container = document.getElementById('health-insights');
        if (!container) return;
        
        const totalScans = this.scans.length;
        const completedScans = this.scans.filter(s => s.status === 'completed').length;
        const totalIssues = this.scans.reduce((sum, scan) => sum + (scan.total_issues || 0), 0);
        const avgIssuesPerSite = totalScans > 0 ? (totalIssues / totalScans).toFixed(1) : 0;
        
        const insights = [
            {
                title: 'Tasso di Completamento',
                value: totalScans > 0 ? Math.round((completedScans / totalScans) * 100) : 0,
                suffix: '%',
                color: 'success'
            },
            {
                title: 'Media Problemi per Sito',
                value: avgIssuesPerSite,
                suffix: '',
                color: avgIssuesPerSite < 3 ? 'success' : avgIssuesPerSite < 7 ? 'warning' : 'danger'
            },
            {
                title: 'Siti Attivi',
                value: this.websites.filter(w => w.is_active).length,
                suffix: `/${this.websites.length}`,
                color: 'info'
            }
        ];
        
        container.innerHTML = insights.map(insight => `
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                    <span class="text-muted small">${insight.title}</span>
                    <span class="fw-bold text-${insight.color}">${insight.value}${insight.suffix}</span>
                </div>
                <div class="progress mt-1" style="height: 4px;">
                    <div class="progress-bar bg-${insight.color}" style="width: ${Math.min(insight.value, 100)}%"></div>
                </div>
            </div>
        `).join('');
    }
    
    formatScanStatus(status) {
        const statusMap = {
            'completed': 'Completata',
            'running': 'In corso',
            'pending': 'In attesa',
            'failed': 'Fallita',
            'cancelled': 'Annullata'
        };
        return statusMap[status] || status;
    }
    
    viewAllReports() {
        this.showSection('scans');
    }

    populateClientDropdown() {
        const select = document.getElementById('websiteClient');
        if (!select) return;

        select.innerHTML = '<option value="">Seleziona cliente...</option>' +
            this.clients.map(client => 
                `<option value="${client.id}">${this.escapeHtml(client.name)}</option>`
            ).join('');
    }

    filterClients() {
        const searchTerm = document.getElementById('client-search').value.toLowerCase();
        const filterValue = document.getElementById('client-filter').value;
        
        let filteredClients = this.clients;
        
        if (searchTerm) {
            filteredClients = filteredClients.filter(client =>
                client.name.toLowerCase().includes(searchTerm) ||
                (client.contact_email && client.contact_email.toLowerCase().includes(searchTerm))
            );
        }
        
        // Apply additional filters here if needed
        
        const originalClients = this.clients;
        this.clients = filteredClients;
        this.renderClientsTable();
        this.clients = originalClients;
    }

    // Modal functions
    showAddClientModal() {
        const modal = new bootstrap.Modal(document.getElementById('addClientModal'));
        document.getElementById('addClientForm').reset();
        modal.show();
    }

    showAddWebsiteModal() {
        const modal = new bootstrap.Modal(document.getElementById('addWebsiteModal'));
        document.getElementById('addWebsiteForm').reset();
        this.populateClientDropdown();
        modal.show();
    }

    async addClient() {
        const form = document.getElementById('addClientForm');
        const formData = new FormData(form);
        
        const clientData = {
            name: document.getElementById('clientName').value,
            contact_email: document.getElementById('clientEmail').value || null,
            description: document.getElementById('clientDescription').value || null
        };

        try {
            const response = await fetch(`${this.apiBase}/clients/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(clientData)
            });

            if (response.ok) {
                const newClient = await response.json();
                this.clients.push(newClient);
                this.renderClientsTable();
                this.updateDashboard();
                this.populateClientDropdown();
                
                bootstrap.Modal.getInstance(document.getElementById('addClientModal')).hide();
                this.showAlert('Cliente aggiunto con successo!', 'success');
            } else {
                throw new Error('Errore durante l\'aggiunta del cliente');
            }
        } catch (error) {
            console.error('Error adding client:', error);
            this.showAlert('Errore durante l\'aggiunta del cliente', 'danger');
        }
    }

    async addWebsite() {
        const websiteData = {
            domain: document.getElementById('websiteDomain').value,
            name: document.getElementById('websiteName').value || null,
            client_id: parseInt(document.getElementById('websiteClient').value),
            description: document.getElementById('websiteDescription').value || null,
            scan_frequency: document.getElementById('scanFrequency').value,
            max_pages: parseInt(document.getElementById('maxPages').value)
        };

        try {
            const response = await fetch(`${this.apiBase}/websites/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(websiteData)
            });

            if (response.ok) {
                const newWebsite = await response.json();
                this.websites.push(newWebsite);
                this.renderWebsitesTable();
                this.updateDashboard();
                
                bootstrap.Modal.getInstance(document.getElementById('addWebsiteModal')).hide();
                this.showAlert('Sito web aggiunto con successo!', 'success');
            } else {
                throw new Error('Errore durante l\'aggiunta del sito web');
            }
        } catch (error) {
            console.error('Error adding website:', error);
            this.showAlert('Errore durante l\'aggiunta del sito web', 'danger');
        }
    }

    // Utility functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getSeoScoreClass(score) {
        if (score >= 90) return 'excellent';
        if (score >= 70) return 'good';
        if (score >= 50) return 'fair';
        return 'poor';
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.insertBefore(alertDiv, document.body.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // CRUD operations
    editClient(clientId) {
        const client = this.clients.find(c => c.id === clientId);
        if (!client) return;

        // Populate form with existing data
        document.getElementById('clientName').value = client.name;
        document.getElementById('clientEmail').value = client.contact_email || '';
        document.getElementById('clientDescription').value = client.description || '';
        
        // Change modal title and button
        document.querySelector('#addClientModal .modal-title').textContent = 'Modifica Cliente';
        const saveBtn = document.querySelector('#addClientModal .btn-primary');
        saveBtn.textContent = 'Aggiorna Cliente';
        saveBtn.onclick = () => this.updateClient(clientId);
        
        const modal = new bootstrap.Modal(document.getElementById('addClientModal'));
        modal.show();
    }

    async updateClient(clientId) {
        const clientData = {
            name: document.getElementById('clientName').value,
            contact_email: document.getElementById('clientEmail').value || null,
            description: document.getElementById('clientDescription').value || null
        };

        try {
            const response = await fetch(`${this.apiBase}/clients/${clientId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(clientData)
            });

            if (response.ok) {
                const updatedClient = await response.json();
                const index = this.clients.findIndex(c => c.id === clientId);
                this.clients[index] = updatedClient;
                this.renderClientsTable();
                
                bootstrap.Modal.getInstance(document.getElementById('addClientModal')).hide();
                this.showAlert('Cliente aggiornato con successo!', 'success');
                this.resetAddClientModal();
            } else {
                throw new Error('Errore durante l\'aggiornamento del cliente');
            }
        } catch (error) {
            console.error('Error updating client:', error);
            this.showAlert('Errore durante l\'aggiornamento del cliente', 'danger');
        }
    }

    async deleteClient(clientId) {
        const client = this.clients.find(c => c.id === clientId);
        if (!client) return;

        const clientWebsites = this.websites.filter(w => w.client_id === clientId);
        let confirmMessage = `Sei sicuro di voler eliminare il cliente "${client.name}"?`;
        
        if (clientWebsites.length > 0) {
            confirmMessage += `\n\nATTENZIONE: Questo cliente ha ${clientWebsites.length} siti web associati che verranno eliminati.`;
        }

        if (confirm(confirmMessage)) {
            try {
                const response = await fetch(`${this.apiBase}/clients/${clientId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.clients = this.clients.filter(c => c.id !== clientId);
                    this.websites = this.websites.filter(w => w.client_id !== clientId);
                    this.renderClientsTable();
                    this.renderWebsitesTable();
                    this.updateDashboard();
                    this.populateClientDropdown();
                    this.showAlert('Cliente eliminato con successo!', 'success');
                } else {
                    throw new Error('Errore durante l\'eliminazione del cliente');
                }
            } catch (error) {
                console.error('Error deleting client:', error);
                this.showAlert('Errore durante l\'eliminazione del cliente', 'danger');
            }
        }
    }

    viewClientWebsites(clientId) {
        this.showSection('websites');
        // Filter websites table by client
        const client = this.clients.find(c => c.id === clientId);
        if (client) {
            this.showAlert(`Visualizzazione siti per: ${client.name}`, 'info');
        }
    }

    editWebsite(websiteId) {
        const website = this.websites.find(w => w.id === websiteId);
        if (!website) return;

        // Populate form with existing data
        document.getElementById('websiteDomain').value = website.domain;
        document.getElementById('websiteName').value = website.name || '';
        document.getElementById('websiteClient').value = website.client_id;
        document.getElementById('websiteDescription').value = website.description || '';
        document.getElementById('scanFrequency').value = website.scan_frequency;
        document.getElementById('maxPages').value = website.max_pages;
        
        // Change modal title and button
        document.querySelector('#addWebsiteModal .modal-title').textContent = 'Modifica Sito Web';
        const saveBtn = document.querySelector('#addWebsiteModal .btn-primary');
        saveBtn.textContent = 'Aggiorna Sito Web';
        saveBtn.onclick = () => this.updateWebsite(websiteId);
        
        const modal = new bootstrap.Modal(document.getElementById('addWebsiteModal'));
        modal.show();
    }

    async updateWebsite(websiteId) {
        const websiteData = {
            domain: document.getElementById('websiteDomain').value,
            name: document.getElementById('websiteName').value || null,
            description: document.getElementById('websiteDescription').value || null,
            scan_frequency: document.getElementById('scanFrequency').value,
            max_pages: parseInt(document.getElementById('maxPages').value)
        };

        try {
            const response = await fetch(`${this.apiBase}/websites/${websiteId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(websiteData)
            });

            if (response.ok) {
                const updatedWebsite = await response.json();
                const index = this.websites.findIndex(w => w.id === websiteId);
                this.websites[index] = updatedWebsite;
                this.renderWebsitesTable();
                
                bootstrap.Modal.getInstance(document.getElementById('addWebsiteModal')).hide();
                this.showAlert('Sito web aggiornato con successo!', 'success');
                this.resetAddWebsiteModal();
            } else {
                throw new Error('Errore durante l\'aggiornamento del sito web');
            }
        } catch (error) {
            console.error('Error updating website:', error);
            this.showAlert('Errore durante l\'aggiornamento del sito web', 'danger');
        }
    }

    async deleteWebsite(websiteId) {
        const website = this.websites.find(w => w.id === websiteId);
        if (!website) return;

        if (confirm(`Sei sicuro di voler eliminare il sito "${website.domain}"?`)) {
            try {
                const response = await fetch(`${this.apiBase}/websites/${websiteId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.websites = this.websites.filter(w => w.id !== websiteId);
                    this.renderWebsitesTable();
                    this.updateDashboard();
                    this.showAlert('Sito web eliminato con successo!', 'success');
                } else {
                    throw new Error('Errore durante l\'eliminazione del sito web');
                }
            } catch (error) {
                console.error('Error deleting website:', error);
                this.showAlert('Errore durante l\'eliminazione del sito web', 'danger');
            }
        }
    }

    resetAddClientModal() {
        document.querySelector('#addClientModal .modal-title').textContent = 'Aggiungi Nuovo Cliente';
        const saveBtn = document.querySelector('#addClientModal .btn-primary');
        saveBtn.textContent = 'Salva Cliente';
        saveBtn.onclick = () => this.addClient();
    }

    resetAddWebsiteModal() {
        document.querySelector('#addWebsiteModal .modal-title').textContent = 'Aggiungi Nuovo Sito Web';
        const saveBtn = document.querySelector('#addWebsiteModal .btn-primary');
        saveBtn.textContent = 'Salva Sito Web';
        saveBtn.onclick = () => this.addWebsite();
    }

    resetNewScanModal() {
        document.getElementById('newScanForm').reset();
        this.populateWebsiteDropdownForScan();
    }

    resetScheduleModal() {
        document.getElementById('scheduleForm').reset();
        document.getElementById('scheduleFrequency').value = 'monthly';
        document.getElementById('scheduleMaxPages').value = 1000;
        document.getElementById('scheduleMaxDepth').value = 5;
        document.getElementById('scheduleRobotsRespect').checked = true;
        document.getElementById('scheduleIncludeExternal').checked = false;
        document.getElementById('scheduleStartNow').checked = false;
    }

    resetEditScheduleModal() {
        document.getElementById('editScheduleForm').reset();
        document.getElementById('editWebsiteId').value = '';
        document.getElementById('editWebsiteDomain').value = '';
    }

    async startScan(websiteId) {
        const website = this.websites.find(w => w.id === websiteId);
        if (!website) {
            this.showAlert('Sito web non trovato', 'danger');
            return;
        }

        if (confirm(`Avviare una nuova scansione per "${website.domain}"?`)) {
            try {
                const response = await fetch(`${this.apiBase}/scans/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        website_id: websiteId
                    })
                });
                
                if (response.ok) {
                    const newScan = await response.json();
                    this.scans.unshift(newScan); // Add to beginning of array
                    this.renderScansTable();
                    this.updateDashboard();
                    
                    this.showAlert(`Scansione avviata per ${website.domain}`, 'success');
                    
                    // Optionally switch to scans section
                    this.showSection('scans');
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Errore durante l\'avvio della scansione');
                }
            } catch (error) {
                console.error('Error starting scan:', error);
                this.showAlert(`Errore durante l'avvio della scansione: ${error.message}`, 'danger');
            }
        }
    }

    showNewScanModal() {
        const modal = new bootstrap.Modal(document.getElementById('newScanModal'));
        this.populateWebsiteDropdownForScan();
        modal.show();
    }

    populateWebsiteDropdownForScan() {
        const select = document.getElementById('scanWebsite');
        if (!select) return;

        const activeWebsites = this.websites.filter(w => w.is_active);
        
        if (activeWebsites.length === 0) {
            select.innerHTML = '<option value="">Nessun sito web attivo trovato</option>';
            return;
        }

        select.innerHTML = '<option value="">Seleziona sito web...</option>' +
            activeWebsites.map(website => {
                const client = this.clients.find(c => c.id === website.client_id);
                const clientName = client ? client.name : 'N/A';
                return `<option value="${website.id}">${website.domain} (${clientName})</option>`;
            }).join('');
    }

    async startNewScan() {
        const websiteId = parseInt(document.getElementById('scanWebsite').value);
        
        if (!websiteId) {
            this.showAlert('Seleziona un sito web', 'warning');
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById('newScanModal')).hide();
        
        // Use the existing startScan function
        await this.startScan(websiteId);
    }

    async viewScanResults(scanId) {
        try {
            this.currentScanId = scanId;
            
            // Initialize pagination state for accordion sections
            this.accordionPagination = {
                critical: { page: 1, limit: 50, total: 0 },
                high: { page: 1, limit: 50, total: 0 },
                medium: { page: 1, limit: 50, total: 0 },
                low: { page: 1, limit: 50, total: 0 },
                pages: { page: 1, limit: 50, total: 0 }
            };
            
            // Fetch scan details
            const scanResponse = await fetch(`${this.apiBase}/scans/${scanId}`);
            if (!scanResponse.ok) throw new Error('Failed to fetch scan details');
            const scan = await scanResponse.json();
            
            // Store scan data
            this.currentScanData = { scan };
            
            // Load initial data and show UI
            await this.loadPagesPage(1);
            
            this.renderScanSummary();
            this.setupAccordionFiltering();
            this.showSection('scan-results');
            
        } catch (error) {
            console.error('Error viewing scan results:', error);
            this.showAlert('Errore nel caricamento dei risultati della scansione', 'danger');
        }
    }

    // Legacy function - no longer used with accordion interface
    async loadIssuesPage(page) {
        // This function is deprecated in favor of loadAccordionIssues
        console.warn('loadIssuesPage is deprecated, use loadAccordionIssues instead');
    }

    async loadPagesPage(page) {
        const { limit } = this.accordionPagination.pages;
        const skip = (page - 1) * limit;
        
        const response = await fetch(`${this.apiBase}/scans/${this.currentScanId}/pages?skip=${skip}&limit=${limit}`);
        if (!response.ok) throw new Error('Failed to fetch pages');
        
        const pages = await response.json();
        this.currentScanData.pages = pages;
        this.accordionPagination.pages.page = page;
        
        // Estimate total from scan data
        if (this.currentScanData.scan && this.currentScanData.scan.pages_found) {
            this.accordionPagination.pages.total = this.currentScanData.scan.pages_found;
        }
        
        this.renderPagesTable(pages);
        this.renderPagesPagination();
    }

    renderScanSummary() {
        const { scan } = this.currentScanData;
        
        // Update summary cards from scan metadata
        document.getElementById('scan-pages-count').textContent = scan.pages_found || 0;
        document.getElementById('scan-total-issues').textContent = scan.total_issues || 0;
        document.getElementById('scan-seo-score').textContent = scan.seo_score ? `${scan.seo_score}/100` : 'N/A';
        
        // Format scan date
        if (scan.started_at) {
            const date = new Date(scan.started_at);
            document.getElementById('scan-date').textContent = date.toLocaleDateString('it-IT');
        }
        
        // Initialize issue counts by severity
        this.issueCounts = { critical: 0, high: 0, medium: 0, low: 0, minor: 0 };
        
        // Load all issues to calculate severity distribution
        this.loadAllIssuesForSummary();
    }
    
    async loadAllIssuesForSummary() {
        try {
            // Load first batch to get total count
            const response = await fetch(`${this.apiBase}/scans/${this.currentScanId}/issues?skip=0&limit=1000`);
            if (!response.ok) throw new Error('Failed to fetch issues');
            
            const issues = await response.json();
            
            // Organize issues by severity and type
            this.issuesBySeverity = {
                critical: {},
                high: {},
                medium: {},
                low: {}
            };
            
            this.issueCounts = { critical: 0, high: 0, medium: 0, low: 0, minor: 0 };
            
            issues.forEach(issue => {
                let severity = issue.severity;
                
                // Group 'minor' with 'low' for display purposes
                if (severity === 'minor') {
                    severity = 'low';
                    this.issueCounts.minor++;
                } else if (this.issueCounts.hasOwnProperty(severity)) {
                    this.issueCounts[severity]++;
                }
                
                // Create nested structure: severity -> issue type -> issues
                if (!this.issuesBySeverity[severity]) {
                    this.issuesBySeverity[severity] = {};
                }
                
                if (!this.issuesBySeverity[severity][issue.type]) {
                    this.issuesBySeverity[severity][issue.type] = {
                        count: 0,
                        issues: []
                    };
                }
                
                this.issuesBySeverity[severity][issue.type].count++;
                this.issuesBySeverity[severity][issue.type].issues.push(issue);
            });
            
            // Update accordion badges
            document.getElementById('critical-count').textContent = this.issueCounts.critical;
            document.getElementById('high-count').textContent = this.issueCounts.high;
            document.getElementById('medium-count').textContent = this.issueCounts.medium;
            document.getElementById('low-count').textContent = this.issueCounts.low + this.issueCounts.minor;
            
            // Create issues distribution chart
            this.createIssuesDistributionChart();
            
            // Generate nested accordions for each severity level
            this.generateNestedAccordions();
            
            // Generate professional insights
            this.generateKeyInsights();
            
            // Store all issues for filtering
            this.allIssues = issues;
            
        } catch (error) {
            console.error('Error loading issues summary:', error);
        }
    }
    
    createIssuesDistributionChart() {
        const ctx = document.getElementById('issuesDistributionChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.issuesChart) {
            this.issuesChart.destroy();
        }
        
        this.issuesChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Critici', 'Alta Priorità', 'Media Priorità', 'Bassa Priorità'],
                datasets: [{
                    data: [
                        this.issueCounts.critical,
                        this.issueCounts.high,
                        this.issueCounts.medium,
                        this.issueCounts.low + this.issueCounts.minor
                    ],
                    backgroundColor: [
                        '#dc3545', // Critical - Red
                        '#fd7e14', // High - Orange
                        '#17a2b8', // Medium - Blue
                        '#6c757d'  // Low - Gray
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed * 100) / total).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    generateNestedAccordions() {
        const severityLevels = ['critical', 'high', 'medium', 'low'];
        
        severityLevels.forEach(severity => {
            const container = document.getElementById(`${severity}SubAccordion`);
            if (!container) return;
            
            const issueTypes = this.issuesBySeverity[severity];
            if (!issueTypes || Object.keys(issueTypes).length === 0) {
                container.innerHTML = '<p class="text-muted text-center py-3">Nessun problema trovato in questa categoria</p>';
                return;
            }
            
            // Generate nested accordion items for each issue type
            container.innerHTML = Object.entries(issueTypes).map(([type, data], index) => {
                const issueIcon = this.getIssueTypeIcon(type);
                const issueTitle = this.formatIssueType(type);
                const collapseId = `${severity}-${type}-collapse`;
                const accordionId = `${severity}SubAccordion`;
                
                return `
                    <div class="accordion-item border-start border-3 border-${this.getSeverityBorderColor(severity)}">
                        <h3 class="accordion-header">
                            <button class="accordion-button collapsed fs-6" type="button" 
                                    data-bs-toggle="collapse" data-bs-target="#${collapseId}" 
                                    aria-expanded="false" onclick="app.loadIssueTypeData('${severity}', '${type}')">
                                <span class="me-2">${issueIcon}</span>
                                <strong>${issueTitle}</strong>
                                <span class="badge bg-${this.getSeverityColor(severity)} ms-auto">${data.count} ${data.count === 1 ? 'pagina' : 'pagine'}</span>
                            </button>
                        </h3>
                        <div id="${collapseId}" class="accordion-collapse collapse" data-bs-parent="#${accordionId}">
                            <div class="accordion-body">
                                <div class="row mb-3">
                                    <div class="col-md-8">
                                        <input type="text" class="form-control form-control-sm" 
                                               id="${severity}-${type}-search" 
                                               placeholder="Cerca in ${issueTitle.toLowerCase()}...">
                                    </div>
                                    <div class="col-md-4">
                                        <button class="btn btn-outline-primary btn-sm" 
                                                onclick="app.exportIssueType('${severity}', '${type}')" 
                                                title="Esporta lista pagine">
                                            <i class="bi bi-download"></i> Esporta Lista
                                        </button>
                                    </div>
                                </div>
                                <div class="table-responsive">
                                    <table class="table table-sm table-hover">
                                        <thead class="table-light">
                                            <tr>
                                                <th width="30%">Pagina</th>
                                                <th width="25%">Titolo Pagina</th>
                                                <th width="25%">Dettagli Problema</th>
                                                <th width="20%">Azione Raccomandata</th>
                                            </tr>
                                        </thead>
                                        <tbody id="${severity}-${type}-table">
                                            <!-- Populated by JavaScript -->
                                        </tbody>
                                    </table>
                                </div>
                                <div id="${severity}-${type}-pagination" class="d-flex justify-content-center mt-3">
                                    <!-- Pagination -->
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        });
    }
    
    getIssueTypeIcon(type) {
        const iconMap = {
            'missing_title': '📋',
            'title_too_short': '📏',
            'title_too_long': '📏',
            'missing_meta_description': '📝',
            'meta_desc_too_short': '📐',
            'meta_desc_too_long': '📐',
            'thin_content': '📄',
            'missing_h1': '🔤',
            'multiple_h1': '🔀',
            'empty_h1': '⭕',
            'broken_heading_hierarchy': '📊',
            'excessive_headings': '📚',
            'images_missing_alt': '🖼️',
            'images_bad_filename': '🏷️',
            'oversized_images': '📷',
            'http_error_404': '🚨',
            'http_error_500': '💥',
            'image_bad_filename': '🏷️',
            'pdf_bad_filename': '📄',
            'pdf_accessibility': '♿'
        };
        return iconMap[type] || '⚠️';
    }
    
    getSeverityColor(severity) {
        const colorMap = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'secondary'
        };
        return colorMap[severity] || 'secondary';
    }
    
    getSeverityBorderColor(severity) {
        const colorMap = {
            'critical': 'danger',
            'high': 'warning', 
            'medium': 'info',
            'low': 'secondary'
        };
        return colorMap[severity] || 'secondary';
    }
    
    generateKeyInsights() {
        const insightsContainer = document.getElementById('key-insights');
        const actionsContainer = document.getElementById('priority-actions');
        
        if (!insightsContainer || !actionsContainer) return;
        
        // Calculate insights based on issue data
        const insights = this.calculateProfessionalInsights();
        const priorityActions = this.generatePriorityActions();
        
        // Render insights
        insightsContainer.innerHTML = insights.map(insight => `
            <div class="alert alert-${insight.type} border-start border-4 border-${insight.type}">
                <div class="d-flex">
                    <div class="flex-shrink-0">
                        <i class="bi ${insight.icon} fs-5"></i>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <h6 class="alert-heading mb-1">${insight.title}</h6>
                        <p class="mb-0 small">${insight.description}</p>
                        ${insight.impact ? `<small class="text-muted">💡 ${insight.impact}</small>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
        
        // Render priority actions
        actionsContainer.innerHTML = priorityActions.map(action => `
            <li class="mb-2">
                <strong>${action.title}</strong>
                <div class="small text-muted">${action.description}</div>
                <span class="badge bg-${action.priority === 'high' ? 'danger' : action.priority === 'medium' ? 'warning' : 'info'} me-1">${action.pages} pagine</span>
                <span class="badge bg-outline-secondary">${action.effort}</span>
            </li>
        `).join('');
    }
    
    calculateProfessionalInsights() {
        const insights = [];
        const totalIssues = this.issueCounts.critical + this.issueCounts.high + this.issueCounts.medium + this.issueCounts.low + this.issueCounts.minor;
        const pagesCount = this.currentScanData?.scan?.pages_found || 1;
        
        // Critical Issues Analysis
        if (this.issueCounts.critical > 0) {
            const criticalPercent = Math.round((this.issueCounts.critical / totalIssues) * 100);
            insights.push({
                type: 'danger',
                icon: 'bi-exclamation-triangle-fill',
                title: 'Problemi Critici Rilevati',
                description: `${this.issueCounts.critical} problemi critici trovati (${criticalPercent}% del totale). Questi richiedono intervento immediato.`,
                impact: 'Impatto alto sulla visibilità nei motori di ricerca'
            });
        } else {
            insights.push({
                type: 'success',
                icon: 'bi-check-circle-fill',
                title: 'Nessun Problema Critico',
                description: 'Ottimo! Il sito non presenta problemi critici che compromettono la SEO.',
                impact: 'Fondamenta SEO solide'
            });
        }
        
        // Content Quality Analysis
        const hasContentIssues = this.hasIssueType('thin_content') || this.hasIssueType('missing_h1') || this.hasIssueType('multiple_h1');
        if (hasContentIssues) {
            insights.push({
                type: 'warning',
                icon: 'bi-file-text',
                title: 'Opportunità di Miglioramento Contenuti',
                description: 'Alcune pagine necessitano ottimizzazioni nella struttura e qualità del contenuto.',
                impact: 'Migliorare la struttura contenuti può aumentare l\'engagement'
            });
        }
        
        // Technical Issues Analysis
        const hasTechnicalIssues = this.hasIssueType('http_error_404') || this.hasIssueType('http_error_500') || this.hasIssueType('oversized_images');
        if (hasTechnicalIssues) {
            insights.push({
                type: 'info',
                icon: 'bi-gear-fill',
                title: 'Aspetti Tecnici da Ottimizzare',
                description: 'Sono stati rilevati alcuni problemi tecnici che influiscono sulle performance.',
                impact: 'Risolvere migliora velocità e user experience'
            });
        }
        
        // Overall Health Assessment
        const issuesPerPage = totalIssues / pagesCount;
        if (issuesPerPage < 2) {
            insights.push({
                type: 'success',
                icon: 'bi-star-fill',
                title: 'Stato SEO Complessivo Buono',
                description: `Media di ${issuesPerPage.toFixed(1)} problemi per pagina. Il sito è in buone condizioni SEO.`,
                impact: 'Poche ottimizzazioni mirate per risultati eccellenti'
            });
        } else if (issuesPerPage < 5) {
            insights.push({
                type: 'warning',
                icon: 'bi-speedometer2',
                title: 'Stato SEO da Migliorare',
                description: `Media di ${issuesPerPage.toFixed(1)} problemi per pagina. Opportunità di ottimizzazione evidenti.`,
                impact: 'Potenziale di miglioramento significativo'
            });
        } else {
            insights.push({
                type: 'danger',
                icon: 'bi-exclamation-octagon-fill',
                title: 'Attenzione: Molti Problemi Rilevati',
                description: `Media di ${issuesPerPage.toFixed(1)} problemi per pagina. È necessaria una strategia di ottimizzazione sistemica.`,
                impact: 'Priorità alta per recuperare ranking persi'
            });
        }
        
        return insights;
    }
    
    generatePriorityActions() {
        const actions = [];
        
        // Analyze most common issues and generate actions
        Object.entries(this.issuesBySeverity).forEach(([severity, types]) => {
            Object.entries(types).forEach(([type, data]) => {
                if (data.count >= 3) { // Only show actions for issues affecting 3+ pages
                    const action = this.getActionForIssueType(type, data.count, severity);
                    if (action) actions.push(action);
                }
            });
        });
        
        // Sort by priority and impact
        return actions.sort((a, b) => {
            const priorityOrder = { high: 3, medium: 2, low: 1 };
            return priorityOrder[b.priority] - priorityOrder[a.priority];
        }).slice(0, 5); // Top 5 actions
    }
    
    getActionForIssueType(type, count, severity) {
        const actionMap = {
            'missing_title': {
                title: 'Aggiungi Title Tags',
                description: 'Ottimizza title tags per migliorare CTR nei risultati di ricerca',
                priority: severity === 'critical' ? 'high' : 'medium',
                effort: 'Basso'
            },
            'missing_meta_description': {
                title: 'Aggiungi Meta Descriptions',
                description: 'Migliora snippets nei risultati di ricerca con descrizioni accattivanti',
                priority: 'medium',
                effort: 'Basso'
            },
            'missing_h1': {
                title: 'Struttura Heading H1',
                description: 'Aggiungi tag H1 per migliorare struttura e keyword targeting',
                priority: 'high',
                effort: 'Medio'
            },
            'thin_content': {
                title: 'Espandi Contenuti Scarsi',
                description: 'Arricchisci pagine con contenuto di valore per migliorare ranking',
                priority: 'medium',
                effort: 'Alto'
            },
            'images_missing_alt': {
                title: 'Ottimizza Alt Text Immagini',
                description: 'Migliora accessibilità e ranking immagini con alt text descriptivi',
                priority: 'medium',
                effort: 'Basso'
            },
            'http_error_404': {
                title: 'Correggi Errori 404',
                description: 'Ripara link rotti o implementa redirect per mantenere link equity',
                priority: 'high',
                effort: 'Medio'
            }
        };
        
        const action = actionMap[type];
        if (action) {
            return {
                ...action,
                pages: count
            };
        }
        return null;
    }
    
    hasIssueType(type) {
        return Object.values(this.issuesBySeverity).some(severity => 
            severity[type] && severity[type].count > 0
        );
    }
    
    formatIssueType(type) {
        const typeMap = {
            'missing_title': 'Title Mancante',
            'title_too_short': 'Title Troppo Corto',
            'title_too_long': 'Title Troppo Lungo',
            'missing_meta_description': 'Meta Description Mancante',
            'meta_desc_too_short': 'Meta Description Corta',
            'meta_desc_too_long': 'Meta Description Lunga',
            'thin_content': 'Contenuto Scarso',
            'missing_h1': 'H1 Mancante',
            'multiple_h1': 'H1 Multiple',
            'empty_h1': 'H1 Vuoto',
            'broken_heading_hierarchy': 'Gerarchia Heading Rotta',
            'excessive_headings': 'Troppi Heading',
            'images_missing_alt': 'Immagini Senza Alt',
            'images_bad_filename': 'Nome File Immagini',
            'oversized_images': 'Immagini Troppo Grandi',
            'http_error_404': 'Errore 404',
            'http_error_500': 'Errore 500'
        };
        return typeMap[type] || type;
    }

    async loadIssueTypeData(severity, type) {
        try {
            if (!this.issuesBySeverity[severity] || !this.issuesBySeverity[severity][type]) {
                console.warn(`No data found for ${severity} ${type}`);
                return;
            }
            
            const issueData = this.issuesBySeverity[severity][type];
            let issues = [...issueData.issues];
            
            // Apply search filter if present
            const searchInput = document.getElementById(`${severity}-${type}-search`);
            if (searchInput) {
                searchInput.addEventListener('input', () => this.filterIssueTypeData(severity, type));
                
                const searchTerm = searchInput.value.toLowerCase();
                if (searchTerm.trim()) {
                    issues = issues.filter(issue => 
                        (issue.page?.url || '').toLowerCase().includes(searchTerm) ||
                        (issue.page?.title || '').toLowerCase().includes(searchTerm) ||
                        issue.description.toLowerCase().includes(searchTerm)
                    );
                }
            }
            
            // For now, show all issues (we can add pagination later if needed)
            this.renderIssueTypeTable(severity, type, issues);
            
        } catch (error) {
            console.error(`Error loading ${severity} ${type} data:`, error);
        }
    }
    
    renderIssueTypeTable(severity, type, issues) {
        const tableBody = document.getElementById(`${severity}-${type}-table`);
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        if (issues.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">Nessun problema trovato</td></tr>';
            return;
        }
        
        issues.forEach(issue => {
            const row = document.createElement('tr');
            
            // Get specific details based on issue type
            const problemDetails = this.getIssueSpecificDetails(type, issue);
            const actionRecommendation = this.getActionableRecommendation(type, issue);
            
            row.innerHTML = `
                <td>
                    <a href="${issue.page?.url || '#'}" target="_blank" class="text-decoration-none">
                        ${this.truncateUrl(issue.page?.url || 'N/A', 35)}
                    </a>
                </td>
                <td>
                    <div class="text-truncate" style="max-width: 200px;" title="${issue.page?.title || 'N/A'}">
                        ${issue.page?.title || '<em class="text-muted">Nessun titolo</em>'}
                    </div>
                </td>
                <td>
                    <small class="text-muted">${problemDetails}</small>
                </td>
                <td>
                    <small class="text-primary">${actionRecommendation}</small>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
    }
    
    getIssueSpecificDetails(type, issue) {
        switch(type) {
            case 'missing_title':
                return 'Nessun tag title presente';
            case 'title_too_short':
                return `Titolo troppo corto (${issue.description.match(/\d+/)?.[0] || 'N/A'} caratteri)`;
            case 'title_too_long':
                return `Titolo troppo lungo (${issue.description.match(/\d+/)?.[0] || 'N/A'} caratteri)`;
            case 'missing_meta_description':
                return 'Nessuna meta description presente';
            case 'meta_desc_too_short':
                return `Meta description troppo corta (${issue.description.match(/\d+/)?.[0] || 'N/A'} caratteri)`;
            case 'meta_desc_too_long':
                return `Meta description troppo lunga (${issue.description.match(/\d+/)?.[0] || 'N/A'} caratteri)`;
            case 'thin_content':
                return `Contenuto scarso (${issue.description.match(/\d+/)?.[0] || 'N/A'} parole)`;
            case 'missing_h1':
                return 'Nessun tag H1 presente';
            case 'multiple_h1':
                return `${issue.description.match(/\d+/)?.[0] || 'N/A'} tag H1 presenti`;
            case 'empty_h1':
                return 'Tag H1 presente ma vuoto';
            case 'broken_heading_hierarchy':
                return 'Gerarchia heading non rispettata';
            case 'excessive_headings':
                return `${issue.description.match(/\d+/)?.[0] || 'N/A'} heading tags (troppi)`;
            case 'images_missing_alt':
                return `${issue.description.match(/\d+/)?.[0] || 'N/A'} immagini senza alt text`;
            case 'images_bad_filename':
            case 'image_bad_filename':
                return 'Nome file non SEO-friendly';
            case 'oversized_images':
                return 'Immagini troppo grandi';
            case 'http_error_404':
                return 'Pagina non trovata (404)';
            case 'http_error_500':
                return 'Errore interno del server (500)';
            default:
                return issue.description;
        }
    }
    
    getActionableRecommendation(type, issue) {
        switch(type) {
            case 'missing_title':
                return 'Aggiungi tag title 30-60 caratteri';
            case 'title_too_short':
                return 'Estendi a 30-60 caratteri';
            case 'title_too_long':
                return 'Riduci a 30-60 caratteri';
            case 'missing_meta_description':
                return 'Aggiungi meta description 120-160 caratteri';
            case 'meta_desc_too_short':
                return 'Estendi a 120-160 caratteri';
            case 'meta_desc_too_long':
                return 'Riduci a 120-160 caratteri';
            case 'thin_content':
                return 'Aggiungi contenuto di valore (min 300 parole)';
            case 'missing_h1':
                return 'Aggiungi tag H1 con keyword principale';
            case 'multiple_h1':
                return 'Mantieni solo un H1, converti altri in H2-H6';
            case 'empty_h1':
                return 'Aggiungi testo descriptivo al tag H1';
            case 'broken_heading_hierarchy':
                return 'Rispetta gerarchia H1 > H2 > H3';
            case 'excessive_headings':
                return 'Semplifica struttura contenuto';
            case 'images_missing_alt':
                return 'Aggiungi testo alt descriptivo alle immagini';
            case 'images_bad_filename':
            case 'image_bad_filename':
                return 'Rinomina con parole chiave descriptive';
            case 'oversized_images':
                return 'Ottimizza dimensioni e formato';
            case 'http_error_404':
                return 'Correggi link o aggiungi redirect 301';
            case 'http_error_500':
                return 'Correggi errori del server';
            default:
                return issue.recommendation || 'Vedi documentazione SEO';
        }
    }
    
    filterIssueTypeData(severity, type) {
        // Reload data with current filter
        this.loadIssueTypeData(severity, type);
    }
    
    exportIssueType(severity, type) {
        try {
            if (!this.issuesBySeverity[severity] || !this.issuesBySeverity[severity][type]) {
                this.showAlert('Nessun dato da esportare', 'warning');
                return;
            }
            
            const issues = this.issuesBySeverity[severity][type].issues;
            const issueTitle = this.formatIssueType(type);
            
            // Create CSV content
            const headers = ['URL Pagina', 'Titolo Pagina', 'Problema', 'Raccomandazione'];
            const csvContent = [
                headers.join(','),
                ...issues.map(issue => [
                    `"${issue.page?.url || 'N/A'}"`,
                    `"${issue.page?.title || 'N/A'}"`,
                    `"${issue.description}"`,
                    `"${issue.recommendation || 'N/A'}"`
                ].join(','))
            ].join('\\n');
            
            // Download CSV
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', `${issueTitle.replace(/\s+/g, '_')}_${severity}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
        } catch (error) {
            console.error('Error exporting issue type:', error);
            this.showAlert("Errore durante l\\'esportazione', 'danger'");
        }
    }
    
    // Legacy function - no longer used with nested accordion interface
    renderIssuesTable(issues) {
        // This function is deprecated in favor of renderIssueTypeTable
        console.warn('renderIssuesTable is deprecated, use renderIssueTypeTable instead');
    }

    renderPagesTable(pages) {
        const tbody = document.getElementById('pages-table-body');
        tbody.innerHTML = '';
        
        pages.forEach(page => {
            const row = document.createElement('tr');
            
            // Status badge
            const statusClass = page.status_code === 200 ? 'success' : 
                               page.status_code >= 400 ? 'danger' : 'warning';
            
            // Issues badge
            const issuesCount = page.issues_count || 0;
            const issuesClass = issuesCount === 0 ? 'success' : 
                               issuesCount <= 3 ? 'warning' : 'danger';
            
            row.innerHTML = `
                <td>
                    <a href="${page.url}" target="_blank" class="text-decoration-none">
                        ${this.truncateUrl(page.url, 40)}
                    </a>
                </td>
                <td><span class="badge bg-${statusClass}">${page.status_code}</span></td>
                <td>
                    <div class="text-truncate" style="max-width: 200px;" title="${page.title || 'N/A'}">
                        ${page.title || '<em class="text-muted">Nessun titolo</em>'}
                    </div>
                </td>
                <td>
                    <div class="text-truncate" style="max-width: 200px;" title="${page.meta_description || 'N/A'}">
                        ${page.meta_description || '<em class="text-muted">Nessuna meta description</em>'}
                    </div>
                </td>
                <td>${page.word_count || 0}</td>
                <td>
                    <span class="badge bg-${issuesClass}">
                        ${issuesCount} ${issuesCount === 1 ? 'problema' : 'problemi'}
                    </span>
                </td>
            `;
            
            tbody.appendChild(row);
        });
        
        if (pages.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nessuna pagina trovata</td></tr>';
        }
    }
    
    async filterPages() {
        try {
            const statusFilter = document.getElementById('page-status-filter');
            const searchInput = document.getElementById('page-search');
            const issuesFilter = document.getElementById('page-issues-filter');
            
            let filteredPages = [...this.currentScanData.pages];
            
            // Apply status filter
            if (statusFilter && statusFilter.value) {
                const statusCode = parseInt(statusFilter.value);
                filteredPages = filteredPages.filter(page => page.status_code === statusCode);
            }
            
            // Apply issues filter
            if (issuesFilter && issuesFilter.value) {
                switch(issuesFilter.value) {
                    case 'has-issues':
                        filteredPages = filteredPages.filter(page => (page.issues_count || 0) > 0);
                        break;
                    case 'no-issues':
                        filteredPages = filteredPages.filter(page => (page.issues_count || 0) === 0);
                        break;
                }
            }
            
            // Apply search filter
            if (searchInput && searchInput.value.trim()) {
                const searchTerm = searchInput.value.toLowerCase();
                filteredPages = filteredPages.filter(page => 
                    page.url.toLowerCase().includes(searchTerm) ||
                    (page.title || '').toLowerCase().includes(searchTerm) ||
                    (page.meta_description || '').toLowerCase().includes(searchTerm)
                );
            }
            
            // Apply pagination to filtered results
            const { page, limit } = this.accordionPagination.pages;
            const startIndex = (page - 1) * limit;
            const paginatedPages = filteredPages.slice(startIndex, startIndex + limit);
            
            // Update pagination info
            this.accordionPagination.pages.total = filteredPages.length;
            
            this.renderPagesTable(paginatedPages);
            this.renderPagesPagination();
            
        } catch (error) {
            console.error('Error filtering pages:', error);
        }
    }

    setupAccordionFiltering() {
        // Pages filtering only (issue filtering is now handled per issue type)
        const pageFilters = {
            status: document.getElementById('page-status-filter'),
            search: document.getElementById('page-search'),
            issues: document.getElementById('page-issues-filter')
        };
        
        Object.values(pageFilters).forEach(filter => {
            if (filter) {
                filter.addEventListener('change', () => this.filterPages());
                filter.addEventListener('input', () => this.filterPages());
            }
        });
    }
    
    // Legacy functions removed - now using nested accordion structure

    renderIssuesPagination() {
        const container = document.getElementById('issues-pagination');
        const { page, limit, total } = this.pagination.issues;
        const totalPages = Math.ceil(total / limit);
        
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let paginationHtml = '<nav><ul class="pagination pagination-sm">';
        
        // Previous button
        paginationHtml += `
            <li class="page-item ${page === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="app.loadIssuesPage(${page - 1})" ${page === 1 ? 'tabindex="-1"' : ''}>
                    <i class="bi bi-chevron-left"></i>
                </a>
            </li>
        `;
        
        // Page numbers (show 5 pages around current)
        const startPage = Math.max(1, page - 2);
        const endPage = Math.min(totalPages, page + 2);
        
        if (startPage > 1) {
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" onclick="app.loadIssuesPage(1)">1</a></li>`;
            if (startPage > 2) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHtml += `
                <li class="page-item ${i === page ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="app.loadIssuesPage(${i})">${i}</a>
                </li>
            `;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" onclick="app.loadIssuesPage(${totalPages})">${totalPages}</a></li>`;
        }
        
        // Next button
        paginationHtml += `
            <li class="page-item ${page === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="app.loadIssuesPage(${page + 1})" ${page === totalPages ? 'tabindex="-1"' : ''}>
                    <i class="bi bi-chevron-right"></i>
                </a>
            </li>
        `;
        
        paginationHtml += '</ul></nav>';
        
        // Add info
        const startRecord = (page - 1) * limit + 1;
        const endRecord = Math.min(page * limit, total);
        paginationHtml += `<small class="text-muted">Mostrando ${startRecord}-${endRecord} di ${total} problemi</small>`;
        
        container.innerHTML = paginationHtml;
    }

    renderPagesPagination() {
        const container = document.getElementById('pages-pagination');
        const { page, limit, total } = this.accordionPagination.pages;
        const totalPages = Math.ceil(total / limit);
        
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let paginationHtml = '<nav><ul class="pagination pagination-sm">';
        
        // Previous button
        paginationHtml += `
            <li class="page-item ${page === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="app.loadPagesPage(${page - 1})" ${page === 1 ? 'tabindex="-1"' : ''}>
                    <i class="bi bi-chevron-left"></i>
                </a>
            </li>
        `;
        
        // Page numbers (show 5 pages around current)
        const startPage = Math.max(1, page - 2);
        const endPage = Math.min(totalPages, page + 2);
        
        if (startPage > 1) {
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" onclick="app.loadPagesPage(1)">1</a></li>`;
            if (startPage > 2) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHtml += `
                <li class="page-item ${i === page ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="app.loadPagesPage(${i})">${i}</a>
                </li>
            `;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" onclick="app.loadPagesPage(${totalPages})">${totalPages}</a></li>`;
        }
        
        // Next button
        paginationHtml += `
            <li class="page-item ${page === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="app.loadPagesPage(${page + 1})" ${page === totalPages ? 'tabindex="-1"' : ''}>
                    <i class="bi bi-chevron-right"></i>
                </a>
            </li>
        `;
        
        paginationHtml += '</ul></nav>';
        
        // Add info
        const startRecord = (page - 1) * limit + 1;
        const endRecord = Math.min(page * limit, total);
        paginationHtml += `<small class="text-muted">Mostrando ${startRecord}-${endRecord} di ${total} pagine</small>`;
        
        container.innerHTML = paginationHtml;
    }

    filterIssues() {
        const severity = document.getElementById('issue-severity-filter').value;
        const type = document.getElementById('issue-type-filter').value;
        const search = document.getElementById('issue-search').value.toLowerCase();
        
        let filteredIssues = this.currentScanData.issues;
        
        if (severity) {
            filteredIssues = filteredIssues.filter(issue => issue.severity === severity);
        }
        
        if (type) {
            filteredIssues = filteredIssues.filter(issue => issue.type === type);
        }
        
        if (search) {
            filteredIssues = filteredIssues.filter(issue => 
                (issue.description || '').toLowerCase().includes(search) ||
                (issue.element || '').toLowerCase().includes(search) ||
                (issue.page?.url || '').toLowerCase().includes(search)
            );
        }
        
        this.renderIssuesTable(filteredIssues);
    }

    filterPages() {
        const status = document.getElementById('page-status-filter').value;
        const search = document.getElementById('page-search').value.toLowerCase();
        
        let filteredPages = this.currentScanData.pages;
        
        if (status) {
            filteredPages = filteredPages.filter(page => page.status_code == status);
        }
        
        if (search) {
            filteredPages = filteredPages.filter(page => 
                (page.url || '').toLowerCase().includes(search) ||
                (page.title || '').toLowerCase().includes(search)
            );
        }
        
        this.renderPagesTable(filteredPages);
    }

    truncateUrl(url, maxLength = 60) {
        if (!url || url.length <= maxLength) return url;
        return url.substring(0, maxLength) + '...';
    }

    async downloadReport(scanId) {
        try {
            // Show loading indicator
            const button = document.getElementById('download-scan-report');
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="bi bi-hourglass-split"></i> Generando...';
            button.disabled = true;
            
            // Download the report
            const response = await fetch(`${this.apiBase}/scans/${scanId}/report`);
            
            if (!response.ok) {
                throw new Error('Failed to generate report');
            }
            
            // Get the filename from the response headers
            const contentDisposition = response.headers.get('content-disposition');
            let filename = 'seo_report.pdf';
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }
            
            // Create blob and download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            
            // Cleanup
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showAlert('Report scaricato con successo!', 'success');
            
        } catch (error) {
            console.error('Error downloading report:', error);
            this.showAlert('Errore nel download del report', 'danger');
        } finally {
            // Reset button
            const button = document.getElementById('download-scan-report');
            if (button) {
                button.innerHTML = '<i class="bi bi-download"></i> Scarica Report';
                button.disabled = false;
            }
        }
    }

    async deleteScan(scanId) {
        const scan = this.scans.find(s => s.id === scanId);
        if (!scan) return;

        if (confirm(`Sei sicuro di voler eliminare la scansione del ${new Date(scan.started_at).toLocaleDateString('it-IT')}?`)) {
            try {
                const response = await fetch(`${this.apiBase}/scans/${scanId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.scans = this.scans.filter(s => s.id !== scanId);
                    this.renderScansTable();
                    this.updateDashboard();
                    this.showAlert('Scansione eliminata con successo!', 'success');
                } else {
                    throw new Error('Errore durante l\'eliminazione della scansione');
                }
            } catch (error) {
                console.error('Error deleting scan:', error);
                this.showAlert('Errore durante l\'eliminazione della scansione', 'danger');
            }
        }
    }

    async retryScan(scanId) {
        const scan = this.scans.find(s => s.id === scanId);
        if (!scan) return;

        if (confirm(`Riprovare la scansione?`)) {
            try {
                const response = await fetch(`${this.apiBase}/scans/${scanId}/retry`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const updatedScan = await response.json();
                    const index = this.scans.findIndex(s => s.id === scanId);
                    this.scans[index] = updatedScan;
                    this.renderScansTable();
                    this.showAlert('Scansione riavviata con successo!', 'success');
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Errore durante il riavvio della scansione');
                }
            } catch (error) {
                console.error('Error retrying scan:', error);
                this.showAlert(`Errore durante il riavvio della scansione: ${error.message}`, 'danger');
            }
        }
    }

    async cancelScan(scanId) {
        const scan = this.scans.find(s => s.id === scanId);
        if (!scan) return;

        if (confirm(`Annullare la scansione in corso?`)) {
            try {
                const response = await fetch(`${this.apiBase}/scans/${scanId}/cancel`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const updatedScan = await response.json();
                    const index = this.scans.findIndex(s => s.id === scanId);
                    this.scans[index] = updatedScan;
                    this.renderScansTable();
                    this.showAlert('Scansione annullata con successo!', 'success');
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Errore durante l\'annullamento della scansione');
                }
            } catch (error) {
                console.error('Error cancelling scan:', error);
                this.showAlert(`Errore durante l'annullamento della scansione: ${error.message}`, 'danger');
            }
        }
    }

    // ================================
    // SCHEDULER MANAGEMENT
    // ================================

    async loadSchedulerData() {
        try {
            await Promise.all([
                this.loadWorkerStats(),
                this.loadQueueStats(),
                this.loadScheduledScans(),
                this.loadActiveTasks(),
                this.loadRecentTasksLog()
            ]);
        } catch (error) {
            console.error('Error loading scheduler data:', error);
            this.showAlert('Errore nel caricamento dei dati dello scheduler', 'danger');
        }
    }

    async refreshSchedulerData() {
        await this.loadSchedulerData();
        this.showAlert('Dati scheduler aggiornati', 'success');
    }

    async loadWorkerStats() {
        try {
            const response = await fetch(`${this.apiBase}/scheduler/status`);
            const stats = await response.json();

            const statusElement = document.getElementById('worker-status');
            const countElement = document.getElementById('worker-count');

            if (stats.worker_status === 'online') {
                statusElement.innerHTML = '<span class="text-success">Online</span>';
            } else {
                statusElement.innerHTML = '<span class="text-danger">Offline</span>';
            }

            if (countElement) {
                countElement.querySelector('span').textContent = stats.worker_count;
            }
        } catch (error) {
            console.error('Error loading worker stats:', error);
            // Fallback to offline state
            document.getElementById('worker-status').innerHTML = '<span class="text-danger">Offline</span>';
            document.getElementById('worker-count').querySelector('span').textContent = '0';
        }
    }

    async loadQueueStats() {
        try {
            const response = await fetch(`${this.apiBase}/scheduler/status`);
            const stats = await response.json();

            const queueLengthElement = document.getElementById('queue-length');
            if (queueLengthElement) {
                queueLengthElement.textContent = stats.queue_length;
            }
        } catch (error) {
            console.error('Error loading queue stats:', error);
            document.getElementById('queue-length').textContent = '0';
        }
    }

    async loadScheduledScans() {
        try {
            const [scheduledResponse, statsResponse] = await Promise.all([
                fetch(`${this.apiBase}/scheduler/scheduled-scans`),
                fetch(`${this.apiBase}/scheduler/stats`)
            ]);
            
            const scheduledScans = await scheduledResponse.json();
            const stats = await statsResponse.json();
            
            const tableBody = document.getElementById('scheduled-scans-table');
            if (!tableBody) return;

            const rows = scheduledScans.map(scan => {
                const lastScan = scan.last_scan_at ? new Date(scan.last_scan_at) : null;
                const nextScan = new Date(scan.next_scan_time);

                const status = scan.is_overdue ? 
                    '<span class="badge bg-danger">In Ritardo</span>' : 
                    '<span class="badge bg-success">Programmata</span>';

                return `
                    <tr>
                        <td>
                            <strong>${scan.domain}</strong>
                            <br><small class="text-muted">${scan.name || 'N/A'}</small>
                        </td>
                        <td><span class="badge bg-info">${this.formatFrequency(scan.scan_frequency)}</span></td>
                        <td>${lastScan ? this.formatDateTime(lastScan) : '<span class="text-muted">Mai</span>'}</td>
                        <td>${this.formatDateTime(nextScan)}</td>
                        <td>${status}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="app.runImmediateScan(${scan.website_id})">
                                <i class="bi bi-play-circle"></i> Avvia Ora
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="app.editSchedule(${scan.website_id})">
                                <i class="bi bi-pencil"></i>
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');

            tableBody.innerHTML = rows;

            // Update stats
            document.getElementById('scans-today').textContent = stats.scans_completed_today;

            if (stats.next_scan_time && stats.next_scan_website) {
                const nextScanTime = new Date(stats.next_scan_time);
                document.getElementById('next-scan-time').textContent = this.formatDateTime(nextScanTime);
                document.getElementById('next-scan-website').innerHTML = `<i class="bi bi-clock"></i> ${stats.next_scan_website}`;
            }

        } catch (error) {
            console.error('Error loading scheduled scans:', error);
        }
    }

    async loadActiveTasks() {
        try {
            const response = await fetch(`${this.apiBase}/scheduler/active-tasks`);
            const activeTasks = await response.json();

            const container = document.getElementById('active-tasks-list');
            if (!container) return;

            if (activeTasks.length === 0) {
                container.innerHTML = '<p class="text-muted text-center">Nessun task attivo al momento</p>';
                return;
            }

            const tasksHtml = activeTasks.map(task => {
                const startedAt = task.started_at ? new Date(task.started_at) : new Date();
                const taskName = task.name.includes('scan_tasks') ? 
                    `Website Scan: ${task.args[0] || 'Unknown'}` : 
                    task.name;

                return `
                    <div class="card border-start border-3 border-info mb-3">
                        <div class="card-body py-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="card-title mb-1">${taskName}</h6>
                                    <small class="text-muted">
                                        <i class="bi bi-cpu"></i> ${task.worker} • 
                                        Avviato ${this.formatTimeAgo(startedAt)}
                                    </small>
                                </div>
                                <div class="text-end">
                                    <span class="badge bg-primary">In Corso</span>
                                </div>
                            </div>
                            <div class="progress mt-2" style="height: 4px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%"></div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = tasksHtml;

        } catch (error) {
            console.error('Error loading active tasks:', error);
            document.getElementById('active-tasks-list').innerHTML = '<p class="text-muted text-center">Errore nel caricamento task attivi</p>';
        }
    }

    async loadRecentTasksLog() {
        try {
            const response = await fetch(`${this.apiBase}/scheduler/recent-tasks?limit=10`);
            const recentTasks = await response.json();

            const container = document.getElementById('recent-tasks-log');
            if (!container) return;

            if (recentTasks.length === 0) {
                container.innerHTML = '<p class="text-muted text-center small">Nessun task recente</p>';
                return;
            }

            const logHtml = recentTasks.map(task => {
                const statusBadge = task.status === 'completed' ? 
                    '<span class="badge bg-success">Completato</span>' :
                    '<span class="badge bg-danger">Fallito</span>';

                const durationText = task.duration ? 
                    `${task.duration}s` : 
                    (task.error ? `Errore: ${task.error}` : '-');

                const completedAt = task.completed_at ? new Date(task.completed_at) : new Date();

                return `
                    <div class="border-bottom py-2">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <small class="fw-medium">${task.task_name}</small>
                                <div class="text-muted small">
                                    ${this.formatTimeAgo(completedAt)} • ${durationText}
                                </div>
                            </div>
                            <div>
                                ${statusBadge}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = logHtml;

        } catch (error) {
            console.error('Error loading recent tasks log:', error);
            document.getElementById('recent-tasks-log').innerHTML = '<p class="text-muted text-center small">Errore nel caricamento log</p>';
        }
    }

    // Scheduler Actions
    async purgeQueue() {
        if (confirm('Sei sicuro di voler pulire completamente la queue? Questa azione non può essere annullata.')) {
            try {
                const response = await fetch(`${this.apiBase}/scheduler/actions/purge-queue`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    this.showAlert('Queue pulita con successo', 'success');
                    await this.loadQueueStats();
                } else {
                    throw new Error('Errore durante la pulizia della queue');
                }
            } catch (error) {
                console.error('Error purging queue:', error);
                this.showAlert('Errore durante la pulizia della queue', 'danger');
            }
        }
    }

    async pauseScheduler() {
        try {
            const response = await fetch(`${this.apiBase}/scheduler/actions/pause`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showAlert('Scheduler messo in pausa', 'warning');
            } else {
                throw new Error('Errore durante la pausa dello scheduler');
            }
        } catch (error) {
            console.error('Error pausing scheduler:', error);
            this.showAlert('Errore durante la pausa dello scheduler', 'danger');
        }
    }

    async resumeScheduler() {
        try {
            const response = await fetch(`${this.apiBase}/scheduler/actions/resume`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showAlert('Scheduler riavviato', 'success');
            } else {
                throw new Error('Errore durante il riavvio dello scheduler');
            }
        } catch (error) {
            console.error('Error resuming scheduler:', error);
            this.showAlert('Errore durante il riavvio dello scheduler', 'danger');
        }
    }

    async showWorkerStats() {
        try {
            const response = await fetch(`${this.apiBase}/scheduler/worker-stats`);
            const stats = await response.json();
            
            if (stats.workers && stats.workers.length > 0) {
                const worker = stats.workers[0];
                alert(`Statistiche Worker:\n\n` +
                      `Worker Attivi: ${stats.total_workers}\n` +
                      `Task Processati: ${worker.total_tasks}\n` +
                      `Task Attivi: ${worker.active_tasks}\n` +
                      `Processi Pool: ${worker.pool_processes}\n` +
                      `Ultimo Aggiornamento: ${new Date(stats.last_updated).toLocaleString()}`);
            } else {
                alert('Nessun worker attivo al momento');
            }
        } catch (error) {
            console.error('Error loading worker stats:', error);
            alert('Errore nel caricamento delle statistiche worker');
        }
    }

    async runImmediateScan(websiteId) {
        try {
            const response = await fetch(`${this.apiBase}/scans/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    website_id: websiteId
                })
            });

            if (response.ok) {
                this.showAlert('Scansione avviata con successo', 'success');
                await this.loadScheduledScans();
            } else {
                throw new Error('Errore durante l\'avvio della scansione');
            }
        } catch (error) {
            console.error('Error starting immediate scan:', error);
            this.showAlert('Errore durante l\'avvio della scansione', 'danger');
        }
    }

    async editSchedule(websiteId) {
        try {
            // Find the website in our data
            const website = this.websites.find(w => w.id === websiteId);
            if (!website) {
                this.showAlert('Sito web non trovato', 'danger');
                return;
            }

            // Populate the edit form
            document.getElementById('editWebsiteId').value = website.id;
            document.getElementById('editWebsiteDomain').value = website.domain;
            document.getElementById('editScheduleFrequency').value = website.scan_frequency || 'monthly';
            document.getElementById('editScheduleMaxPages').value = website.max_pages || 1000;
            document.getElementById('editScheduleMaxDepth').value = website.max_depth || 5;
            document.getElementById('editScheduleRobotsRespect').checked = website.robots_respect !== false;
            document.getElementById('editScheduleIncludeExternal').checked = website.include_external || false;
            document.getElementById('editScheduleActive').checked = website.is_active !== false;

            // Show the modal
            const modal = new bootstrap.Modal(document.getElementById('editScheduleModal'));
            modal.show();
        } catch (error) {
            console.error('Error opening edit schedule modal:', error);
            this.showAlert('Errore nell\'apertura del modal di modifica', 'danger');
        }
    }

    showScheduleModal() {
        // Populate the website dropdown
        this.populateScheduleWebsiteDropdown();
        
        // Reset form
        document.getElementById('scheduleForm').reset();
        document.getElementById('scheduleFrequency').value = 'monthly';
        document.getElementById('scheduleMaxPages').value = 1000;
        document.getElementById('scheduleMaxDepth').value = 5;
        document.getElementById('scheduleRobotsRespect').checked = true;
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('scheduleModal'));
        modal.show();
    }

    populateScheduleWebsiteDropdown() {
        const dropdown = document.getElementById('scheduleWebsite');
        if (!dropdown) return;

        // Clear existing options except the first one
        dropdown.innerHTML = '<option value="">Seleziona sito web...</option>';

        // Add websites
        this.websites.forEach(website => {
            const option = document.createElement('option');
            option.value = website.id;
            option.textContent = `${website.domain} - ${website.name || 'N/A'}`;
            dropdown.appendChild(option);
        });
    }

    async createSchedule() {
        try {
            const websiteId = document.getElementById('scheduleWebsite').value;
            const frequency = document.getElementById('scheduleFrequency').value;
            const maxPages = parseInt(document.getElementById('scheduleMaxPages').value);
            const maxDepth = parseInt(document.getElementById('scheduleMaxDepth').value);
            const robotsRespect = document.getElementById('scheduleRobotsRespect').checked;
            const includeExternal = document.getElementById('scheduleIncludeExternal').checked;
            const startNow = document.getElementById('scheduleStartNow').checked;

            if (!websiteId) {
                this.showAlert('Seleziona un sito web', 'warning');
                return;
            }

            // Update website settings
            const response = await fetch(`${this.apiBase}/websites/${websiteId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scan_frequency: frequency,
                    max_pages: maxPages,
                    max_depth: maxDepth,
                    robots_respect: robotsRespect,
                    include_external: includeExternal,
                    is_active: true
                })
            });

            if (response.ok) {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('scheduleModal'));
                modal.hide();

                // Start immediate scan if requested
                if (startNow) {
                    await this.runImmediateScan(parseInt(websiteId));
                }

                // Refresh data
                await this.loadWebsites();
                await this.loadScheduledScans();
                
                this.showAlert('Programmazione creata con successo!', 'success');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Errore durante la creazione della programmazione');
            }
        } catch (error) {
            console.error('Error creating schedule:', error);
            this.showAlert(`Errore durante la creazione della programmazione: ${error.message}`, 'danger');
        }
    }

    async updateSchedule() {
        try {
            const websiteId = document.getElementById('editWebsiteId').value;
            const frequency = document.getElementById('editScheduleFrequency').value;
            const maxPages = parseInt(document.getElementById('editScheduleMaxPages').value);
            const maxDepth = parseInt(document.getElementById('editScheduleMaxDepth').value);
            const robotsRespect = document.getElementById('editScheduleRobotsRespect').checked;
            const includeExternal = document.getElementById('editScheduleIncludeExternal').checked;
            const isActive = document.getElementById('editScheduleActive').checked;

            const response = await fetch(`${this.apiBase}/websites/${websiteId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scan_frequency: frequency,
                    max_pages: maxPages,
                    max_depth: maxDepth,
                    robots_respect: robotsRespect,
                    include_external: includeExternal,
                    is_active: isActive
                })
            });

            if (response.ok) {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('editScheduleModal'));
                modal.hide();

                // Refresh data
                await this.loadWebsites();
                await this.loadScheduledScans();
                
                this.showAlert('Programmazione aggiornata con successo!', 'success');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Errore durante l\'aggiornamento della programmazione');
            }
        } catch (error) {
            console.error('Error updating schedule:', error);
            this.showAlert(`Errore durante l'aggiornamento della programmazione: ${error.message}`, 'danger');
        }
    }

    async deleteSchedule() {
        const websiteId = document.getElementById('editWebsiteId').value;
        const website = this.websites.find(w => w.id == websiteId);
        
        if (!website) {
            this.showAlert('Sito web non trovato', 'danger');
            return;
        }

        if (confirm(`Sei sicuro di voler disattivare la programmazione per ${website.domain}?\n\nIl sito web non verrà più scansionato automaticamente.`)) {
            try {
                const response = await fetch(`${this.apiBase}/websites/${websiteId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        is_active: false
                    })
                });

                if (response.ok) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editScheduleModal'));
                    modal.hide();

                    // Refresh data
                    await this.loadWebsites();
                    await this.loadScheduledScans();
                    
                    this.showAlert('Programmazione disattivata con successo!', 'success');
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Errore durante la disattivazione della programmazione');
                }
            } catch (error) {
                console.error('Error deleting schedule:', error);
                this.showAlert(`Errore durante la disattivazione della programmazione: ${error.message}`, 'danger');
            }
        }
    }

    // Helper methods for scheduler
    formatFrequency(frequency) {
        const frequencyMap = {
            'daily': 'Giornaliera',
            'weekly': 'Settimanale', 
            'monthly': 'Mensile'
        };
        return frequencyMap[frequency] || frequency;
    }

    formatTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);

        if (diffMins < 1) return 'ora';
        if (diffMins < 60) return `${diffMins}m fa`;
        if (diffHours < 24) return `${diffHours}h fa`;
        return `${Math.floor(diffHours / 24)}g fa`;
    }

    // ===== MODERN FEATURES ===== //
    
    setupModernFeatures() {
        // Add fade-in animations to cards
        this.addFadeInAnimations();
        
        // Setup smooth scrolling
        this.setupSmoothScrolling();
        
        // Add loading states
        this.setupLoadingStates();
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
    }
    
    addFadeInAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, { threshold: 0.1 });
        
        // Observe all cards
        document.querySelectorAll('.card').forEach(card => {
            observer.observe(card);
        });
    }
    
    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    setupLoadingStates() {
        // Add loading spinners to buttons on click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn') && !e.target.classList.contains('btn-no-loading')) {
                const btn = e.target;
                const originalText = btn.innerHTML;
                
                btn.innerHTML = '<span class="loading-spinner"></span> Caricamento...';
                btn.disabled = true;
                
                // Auto-restore after 2 seconds if not manually restored
                setTimeout(() => {
                    if (btn.innerHTML.includes('loading-spinner')) {
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                    }
                }, 2000);
            }
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for quick search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('input[type="search"], input[placeholder*="cerca"]');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // Ctrl/Cmd + N for new scan
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                this.showNewScanModal();
            }
            
            // Number keys for navigation
            if (e.altKey && !isNaN(e.key) && e.key >= '1' && e.key <= '5') {
                e.preventDefault();
                const sections = ['dashboard', 'clients', 'websites', 'scans', 'scheduler'];
                const sectionIndex = parseInt(e.key) - 1;
                if (sections[sectionIndex]) {
                    this.showSection(sections[sectionIndex]);
                }
            }
        });
    }
    
    startRealTimeUpdates() {
        // Update timestamp every minute
        this.updateTimestamp();
        setInterval(() => this.updateTimestamp(), 60000);
        
        // Auto-refresh data every 5 minutes
        setInterval(() => this.refreshData(), 300000);
        
        // Check for new scans every 30 seconds
        setInterval(() => this.checkForUpdates(), 30000);
    }
    
    updateTimestamp() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('it-IT', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const updateElement = document.getElementById('last-update');
        if (updateElement) {
            updateElement.textContent = timeString;
        }
    }
    
    async refreshData() {
        try {
            // Show subtle loading indicator
            this.showRefreshIndicator();
            
            // Reload current section data
            await this.loadInitialData();
            this.updateDashboard();
            
            // Reload current section if needed
            switch (this.currentSection) {
                case 'clients':
                    this.loadClients();
                    break;
                case 'websites':
                    this.loadWebsites();
                    break;
                case 'scans':
                    this.loadScans();
                    break;
                case 'scheduler':
                    this.loadSchedulerData();
                    break;
            }
            
            this.hideRefreshIndicator();
            
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.hideRefreshIndicator();
        }
    }
    
    showRefreshIndicator() {
        const indicator = document.querySelector('.pulse-animation');
        if (indicator) {
            indicator.style.animationDuration = '0.5s';
        }
    }
    
    hideRefreshIndicator() {
        const indicator = document.querySelector('.pulse-animation');
        if (indicator) {
            indicator.style.animationDuration = '2s';
        }
    }
    
    async checkForUpdates() {
        try {
            // Check if there are new scans or status changes
            const response = await fetch(`${this.apiBase}/scans?limit=1`);
            if (response.ok) {
                const latestScans = await response.json();
                if (latestScans.length > 0) {
                    const latestScan = latestScans[0];
                    const currentLatest = this.scans[0];
                    
                    // If we have a new scan or status change, refresh
                    if (!currentLatest || 
                        latestScan.id !== currentLatest.id || 
                        latestScan.status !== currentLatest.status) {
                        await this.loadScans();
                        this.updateDashboard();
                        
                        // Show notification for new scans
                        if (!currentLatest || latestScan.id !== currentLatest.id) {
                            this.showNotification('Nuova scansione rilevata!', 'info');
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error checking for updates:', error);
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: var(--shadow-xl);
            border-radius: 12px;
        `;
        
        notification.innerHTML = `
            <i class="bi bi-info-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SEOAuditingApp();
});