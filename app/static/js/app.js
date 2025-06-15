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
                case 'failed':
                    statusBadge = '<span class="badge bg-danger">Fallita</span>';
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
                            <button class="btn btn-outline-info" onclick="app.viewScanResults(${scan.id})" title="Visualizza risultati">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-outline-primary" onclick="app.downloadReport(${scan.id})" title="Scarica report">
                                <i class="bi bi-download"></i>
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

    startScan(websiteId) {
        this.showAlert('Avvio scansione in sviluppo', 'info');
    }

    startNewScan() {
        this.showAlert('Selezione sito per nuova scansione in sviluppo', 'info');
    }

    viewScanResults(scanId) {
        this.showAlert('Visualizzazione risultati in sviluppo', 'info');
    }

    downloadReport(scanId) {
        this.showAlert('Download report in sviluppo', 'info');
    }
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SEOAuditingApp();
});