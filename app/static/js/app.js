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
        await this.loadInitialData();
        this.updateDashboard();
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
        document.getElementById('total-clients').textContent = this.clients.length;
        document.getElementById('total-websites').textContent = this.websites.length;
        document.getElementById('total-scans').textContent = this.scans.length;
        
        // Calculate active issues (placeholder)
        const activeIssues = this.scans.reduce((total, scan) => total + (scan.total_issues || 0), 0);
        document.getElementById('active-issues').textContent = activeIssues;
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
            
            // Count issues by severity
            this.issueCounts = { critical: 0, high: 0, medium: 0, low: 0, minor: 0 };
            this.issueTypes = new Set();
            
            issues.forEach(issue => {
                const severity = issue.severity;
                if (this.issueCounts.hasOwnProperty(severity)) {
                    this.issueCounts[severity]++;
                }
                this.issueTypes.add(issue.type);
            });
            
            // Update accordion badges
            document.getElementById('critical-count').textContent = this.issueCounts.critical;
            document.getElementById('high-count').textContent = this.issueCounts.high;
            document.getElementById('medium-count').textContent = this.issueCounts.medium;
            document.getElementById('low-count').textContent = this.issueCounts.low + this.issueCounts.minor;
            
            // Create issues distribution chart
            this.createIssuesDistributionChart();
            
            // Populate filter dropdowns
            this.populateIssueTypeFilters();
            
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
    
    populateIssueTypeFilters() {
        const filterIds = ['critical-type-filter', 'high-type-filter', 'medium-type-filter', 'low-type-filter'];
        
        filterIds.forEach(filterId => {
            const filter = document.getElementById(filterId);
            if (filter) {
                filter.innerHTML = '<option value="">Tutti i tipi</option>' +
                    Array.from(this.issueTypes).map(type => 
                        `<option value="${type}">${this.formatIssueType(type)}</option>`
                    ).join('');
            }
        });
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
            'images_missing_alt': 'Immagini Senza Alt',
            'images_bad_filename': 'Nome File Immagini',
            'oversized_images': 'Immagini Troppo Grandi',
            'http_error_404': 'Errore 404',
            'http_error_500': 'Errore 500'
        };
        return typeMap[type] || type;
    }

    // Legacy function - no longer used with accordion interface
    renderIssuesTable(issues) {
        // This function is deprecated in favor of renderAccordionIssuesTable
        console.warn('renderIssuesTable is deprecated, use renderAccordionIssuesTable instead');
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
        // Setup filtering for each severity level
        const severityLevels = ['critical', 'high', 'medium', 'low'];
        
        severityLevels.forEach(severity => {
            const typeFilter = document.getElementById(`${severity}-type-filter`);
            const searchInput = document.getElementById(`${severity}-search`);
            
            if (typeFilter) {
                typeFilter.addEventListener('change', () => this.filterAccordionIssues(severity));
            }
            if (searchInput) {
                searchInput.addEventListener('input', () => this.filterAccordionIssues(severity));
            }
        });
        
        // Pages filtering
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
        
        // Setup accordion expand listeners to load data when opened
        const accordionButtons = document.querySelectorAll('#issuesAccordion .accordion-button');
        accordionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const target = e.target.dataset.bsTarget;
                if (target) {
                    const severity = this.getSeverityFromTarget(target);
                    if (severity) {
                        setTimeout(() => this.loadAccordionIssues(severity, 1), 100);
                    }
                }
            });
        });
    }
    
    getSeverityFromTarget(target) {
        if (target.includes('critical')) return 'critical';
        if (target.includes('high')) return 'high';
        if (target.includes('medium')) return 'medium';
        if (target.includes('low')) return 'low';
        return null;
    }
    
    async loadAccordionIssues(severity, page = 1) {
        try {
            const { limit } = this.accordionPagination[severity];
            
            // Filter issues by severity
            let filteredIssues = this.allIssues.filter(issue => {
                if (severity === 'low') {
                    return issue.severity === 'low' || issue.severity === 'minor';
                }
                return issue.severity === severity;
            });
            
            // Apply additional filters
            const typeFilter = document.getElementById(`${severity}-type-filter`);
            const searchInput = document.getElementById(`${severity}-search`);
            
            if (typeFilter && typeFilter.value) {
                filteredIssues = filteredIssues.filter(issue => issue.type === typeFilter.value);
            }
            
            if (searchInput && searchInput.value.trim()) {
                const searchTerm = searchInput.value.toLowerCase();
                filteredIssues = filteredIssues.filter(issue => 
                    issue.title.toLowerCase().includes(searchTerm) ||
                    issue.description.toLowerCase().includes(searchTerm) ||
                    (issue.page?.url || '').toLowerCase().includes(searchTerm)
                );
            }
            
            // Pagination
            const startIndex = (page - 1) * limit;
            const paginatedIssues = filteredIssues.slice(startIndex, startIndex + limit);
            
            // Update pagination info
            this.accordionPagination[severity].page = page;
            this.accordionPagination[severity].total = filteredIssues.length;
            
            // Render issues table for this severity
            this.renderAccordionIssuesTable(severity, paginatedIssues);
            this.renderAccordionPagination(severity);
            
        } catch (error) {
            console.error(`Error loading ${severity} issues:`, error);
        }
    }
    
    renderAccordionIssuesTable(severity, issues) {
        const tableBody = document.getElementById(`${severity}-issues-table`);
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        issues.forEach(issue => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>
                    <strong>${issue.title || 'N/A'}</strong>
                    <br><small class="text-muted">${this.formatIssueType(issue.type)}</small>
                </td>
                <td>${issue.description || 'N/A'}</td>
                <td>
                    <a href="${issue.page?.url || '#'}" target="_blank" class="text-decoration-none">
                        ${this.truncateUrl(issue.page?.url || 'N/A', 30)}
                    </a>
                    ${issue.page?.title ? `<br><small class="text-muted">${issue.page.title}</small>` : ''}
                </td>
                <td>
                    <small class="text-muted">
                        ${issue.recommendation ? issue.recommendation.substring(0, 100) + '...' : 'N/A'}
                    </small>
                    ${issue.element ? `<br><code style="font-size: 0.8em;">${issue.element}</code>` : ''}
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
        if (issues.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Nessun problema trovato</td></tr>';
        }
    }
    
    renderAccordionPagination(severity) {
        const container = document.getElementById(`${severity}-pagination`);
        if (!container) return;
        
        const { page, limit, total } = this.accordionPagination[severity];
        const totalPages = Math.ceil(total / limit);
        
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let paginationHtml = '<nav><ul class="pagination pagination-sm justify-content-center">';
        
        // Previous button
        paginationHtml += `
            <li class="page-item ${page === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="app.loadAccordionIssues('${severity}', ${page - 1})" ${page === 1 ? 'tabindex="-1"' : ''}>
                    Precedente
                </a>
            </li>
        `;
        
        // Page numbers
        const startPage = Math.max(1, page - 2);
        const endPage = Math.min(totalPages, page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHtml += `
                <li class="page-item ${i === page ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="app.loadAccordionIssues('${severity}', ${i})">${i}</a>
                </li>
            `;
        }
        
        // Next button
        paginationHtml += `
            <li class="page-item ${page === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="app.loadAccordionIssues('${severity}', ${page + 1})" ${page === totalPages ? 'tabindex="-1"' : ''}>
                    Successivo
                </a>
            </li>
        `;
        
        paginationHtml += '</ul></nav>';
        container.innerHTML = paginationHtml;
    }
    
    filterAccordionIssues(severity) {
        // Reload issues with current filters
        this.loadAccordionIssues(severity, 1);
    }

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
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SEOAuditingApp();
});