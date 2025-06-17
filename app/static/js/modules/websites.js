// SEO Auditing Solution - Websites Module
class WebsitesModule {
    constructor() {
        this.filteredWebsites = [];
        this.searchDebounced = utils.debounce(this.applyFilters.bind(this), 300);
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('website-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                appState.setFilter('websites', 'search', e.target.value);
                this.searchDebounced();
            });
        }

        // Filter selects
        const clientFilter = document.getElementById('website-client-filter');
        if (clientFilter) {
            clientFilter.addEventListener('change', (e) => {
                appState.setFilter('websites', 'client', e.target.value);
                this.applyFilters();
            });
        }

        const statusFilter = document.getElementById('website-status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                appState.setFilter('websites', 'status', e.target.value);
                this.applyFilters();
            });
        }

        const frequencyFilter = document.getElementById('website-frequency-filter');
        if (frequencyFilter) {
            frequencyFilter.addEventListener('change', (e) => {
                appState.setFilter('websites', 'frequency', e.target.value);
                this.applyFilters();
            });
        }

        // Per page select
        const perPageSelect = document.getElementById('websites-per-page');
        if (perPageSelect) {
            perPageSelect.addEventListener('change', (e) => {
                appState.setPagination('websites', { 
                    perPage: parseInt(e.target.value), 
                    page: 1 
                });
                this.renderTable();
            });
        }

        // Subscribe to data changes
        appState.subscribe('data.websites', () => {
            this.applyFilters();
            this.updateClientFilter();
        });

        appState.subscribe('data.clients', () => {
            this.updateClientFilter();
        });
    }

    async loadData() {
        try {
            appState.setLoading('websites', true);
            
            // Load both websites and clients to enrich website data
            const [websites, clients] = await Promise.all([
                apiClient.getWebsites(),
                apiClient.getClients()
            ]);
            
            // Enrich websites with client data
            const enrichedWebsites = websites.map(website => {
                const client = clients.find(c => c.id === website.client_id);
                return {
                    ...website,
                    client: client || null
                };
            });
            
            appState.setData('websites', enrichedWebsites);
            
            // Update header stats
            this.updateHeaderStats(enrichedWebsites);

        } catch (error) {
            console.error('Error loading websites:', error);
            utils.showToast('Errore nel caricamento dei siti web', 'error');
        } finally {
            appState.setLoading('websites', false);
        }
    }

    updateHeaderStats(websites) {
        const activeWebsites = websites.filter(w => w.is_active).length;
        const scanningWebsites = websites.filter(w => w.status === 'scanning').length;
        
        // Update header mini stats
        const elementsToUpdate = {
            'websites-count-header': websites.length,
            'scanning-websites-header': scanningWebsites,
            'total-websites-header': websites.length
        };

        Object.entries(elementsToUpdate).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });

        // Calculate next scan time (mock for now)
        const nextScanElement = document.getElementById('next-scan-header');
        if (nextScanElement) {
            nextScanElement.textContent = this.calculateNextScanTime(websites);
        }
    }

    calculateNextScanTime(websites) {
        // Simple calculation - find website with earliest next scan
        const now = new Date();
        let nextScan = null;
        
        websites.forEach(website => {
            if (website.is_active && website.scan_frequency) {
                // Mock calculation based on frequency
                const lastScan = website.last_scan_date ? new Date(website.last_scan_date) : now;
                let nextScanTime;
                
                switch (website.scan_frequency) {
                    case 'daily':
                        nextScanTime = new Date(lastScan.getTime() + 24 * 60 * 60 * 1000);
                        break;
                    case 'weekly':
                        nextScanTime = new Date(lastScan.getTime() + 7 * 24 * 60 * 60 * 1000);
                        break;
                    case 'monthly':
                        nextScanTime = new Date(lastScan.getTime() + 30 * 24 * 60 * 60 * 1000);
                        break;
                    default:
                        return;
                }
                
                if (!nextScan || nextScanTime < nextScan) {
                    nextScan = nextScanTime;
                }
            }
        });
        
        return nextScan ? utils.formatRelativeTime(nextScan) : '--';
    }

    updateClientFilter() {
        const clientFilter = document.getElementById('website-client-filter');
        if (!clientFilter) return;

        const clients = appState.getData('clients') || [];
        const currentValue = clientFilter.value;

        // Clear and rebuild options
        clientFilter.innerHTML = '<option value="">👥 Tutti i clienti</option>';
        
        clients.forEach(client => {
            const option = document.createElement('option');
            option.value = client.id;
            option.textContent = client.name;
            clientFilter.appendChild(option);
        });

        // Restore selection
        clientFilter.value = currentValue;
    }

    applyFilters() {
        const websites = appState.getData('websites') || [];
        const searchTerm = appState.getFilter('websites', 'search').toLowerCase();
        const clientFilter = appState.getFilter('websites', 'client');
        const statusFilter = appState.getFilter('websites', 'status');
        const frequencyFilter = appState.getFilter('websites', 'frequency');

        // Filter websites
        this.filteredWebsites = websites.filter(website => {
            const matchesSearch = !searchTerm || 
                website.domain.toLowerCase().includes(searchTerm) ||
                (website.name && website.name.toLowerCase().includes(searchTerm)) ||
                (website.client?.name && website.client.name.toLowerCase().includes(searchTerm));
            
            const matchesClient = !clientFilter || 
                website.client_id?.toString() === clientFilter;
            
            const matchesStatus = !statusFilter || 
                (statusFilter === 'active' && website.is_active) ||
                (statusFilter === 'scanning' && website.status === 'scanning') ||
                (statusFilter === 'error' && website.status === 'error');

            const matchesFrequency = !frequencyFilter || 
                website.scan_frequency === frequencyFilter;

            return matchesSearch && matchesClient && matchesStatus && matchesFrequency;
        });

        // Sort websites by domain
        this.filteredWebsites.sort((a, b) => a.domain.localeCompare(b.domain));

        // Update pagination
        appState.setPagination('websites', {
            ...appState.getPagination('websites'),
            total: this.filteredWebsites.length,
            page: 1
        });

        this.renderTable();
        this.updateCounters();
    }

    renderTable() {
        const tbody = document.getElementById('websites-table-body');
        if (!tbody) return;

        const pagination = appState.getPagination('websites');
        const startIndex = (pagination.page - 1) * pagination.perPage;
        const endIndex = startIndex + pagination.perPage;
        const pageWebsites = this.filteredWebsites.slice(startIndex, endIndex);

        if (pageWebsites.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-4">
                        <div class="text-muted">
                            <i class="bi bi-globe fs-1 opacity-50"></i>
                            <p class="mt-2">Nessun sito web trovato</p>
                            <button class="btn btn-primary btn-sm" onclick="websites.showAddModal()">
                                <i class="bi bi-plus"></i> Aggiungi Primo Sito
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = pageWebsites.map(website => `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="website-favicon me-3">
                            <i class="bi bi-globe text-success fs-4"></i>
                        </div>
                        <div>
                            <div class="fw-bold">
                                <a href="${website.domain}" target="_blank" class="text-decoration-none">
                                    ${website.domain}
                                    <i class="bi bi-box-arrow-up-right ms-1 small"></i>
                                </a>
                            </div>
                            ${website.description ? `<small class="text-muted">${website.description}</small>` : ''}
                        </div>
                    </div>
                </td>
                <td>
                    ${website.name ? 
                        `<span class="fw-medium">${website.name}</span>` : 
                        '<span class="text-muted">-</span>'
                    }
                </td>
                <td>
                    ${website.client ? 
                        `<span class="badge bg-info">
                            <i class="bi bi-person"></i> ${website.client.name}
                        </span>` : 
                        '<span class="text-muted">Nessun cliente</span>'
                    }
                </td>
                <td>
                    ${this.getFrequencyBadge(website.scan_frequency)}
                </td>
                <td>
                    <div class="text-muted small">
                        ${website.last_scan_date ? 
                            utils.formatRelativeTime(website.last_scan_date) : 
                            'Mai scansionato'
                        }
                    </div>
                </td>
                <td>
                    ${this.getWebsiteStatusBadge(website)}
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-success" onclick="websites.startScan(${website.id})" title="Avvia Scansione">
                            <i class="bi bi-play-circle"></i>
                        </button>
                        <button class="btn btn-outline-primary" onclick="websites.editWebsite(${website.id})" title="Modifica">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="websites.deleteWebsite(${website.id})" title="Elimina">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        this.renderPagination();
    }

    getFrequencyBadge(frequency) {
        const frequencyMap = {
            'daily': { class: 'bg-success', text: '🌅 Giornaliera', icon: 'calendar-day' },
            'weekly': { class: 'bg-info', text: '📅 Settimanale', icon: 'calendar-week' },
            'monthly': { class: 'bg-warning', text: '🗓️ Mensile', icon: 'calendar-month' }
        };
        
        const config = frequencyMap[frequency] || { class: 'bg-secondary', text: 'Non impostata', icon: 'dash' };
        return `<span class="badge ${config.class}">
            <i class="bi bi-${config.icon}"></i> ${config.text}
        </span>`;
    }

    getWebsiteStatusBadge(website) {
        if (!website.is_active) {
            return '<span class="badge bg-secondary"><i class="bi bi-pause-circle"></i> Inattivo</span>';
        }
        
        if (website.status === 'scanning') {
            return '<span class="badge bg-info"><i class="bi bi-arrow-clockwise"></i> In Scansione</span>';
        }
        
        if (website.status === 'error') {
            return '<span class="badge bg-danger"><i class="bi bi-exclamation-triangle"></i> Errore</span>';
        }
        
        return '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Attivo</span>';
    }

    renderPagination() {
        const container = document.getElementById('websites-pagination');
        if (!container) return;

        const pagination = appState.getPagination('websites');
        const totalPages = Math.ceil(pagination.total / pagination.perPage);

        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        const pages = [];
        const maxVisible = 5;
        let startPage = Math.max(1, pagination.page - Math.floor(maxVisible / 2));
        let endPage = Math.min(totalPages, startPage + maxVisible - 1);

        if (endPage - startPage + 1 < maxVisible) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }

        // Previous button
        pages.push(`
            <button class="btn btn-outline-primary ${pagination.page === 1 ? 'disabled' : ''}" 
                    onclick="websites.goToPage(${pagination.page - 1})"
                    ${pagination.page === 1 ? 'disabled' : ''}>
                <i class="bi bi-chevron-left"></i>
            </button>
        `);

        // Page numbers
        for (let i = startPage; i <= endPage; i++) {
            pages.push(`
                <button class="btn ${i === pagination.page ? 'btn-primary' : 'btn-outline-primary'}" 
                        onclick="websites.goToPage(${i})">
                    ${i}
                </button>
            `);
        }

        // Next button
        pages.push(`
            <button class="btn btn-outline-primary ${pagination.page === totalPages ? 'disabled' : ''}" 
                    onclick="websites.goToPage(${pagination.page + 1})"
                    ${pagination.page === totalPages ? 'disabled' : ''}>
                <i class="bi bi-chevron-right"></i>
            </button>
        `);

        container.innerHTML = pages.join('');
    }

    updateCounters() {
        const shownElement = document.getElementById('websites-shown');
        const totalElement = document.getElementById('websites-total');
        
        if (shownElement) shownElement.textContent = this.filteredWebsites.length;
        if (totalElement) totalElement.textContent = appState.getData('websites').length;
    }

    goToPage(page) {
        const pagination = appState.getPagination('websites');
        const totalPages = Math.ceil(pagination.total / pagination.perPage);
        
        if (page < 1 || page > totalPages) return;
        
        appState.setPagination('websites', { ...pagination, page });
        this.renderTable();
    }

    clearFilters() {
        document.getElementById('website-search').value = '';
        document.getElementById('website-client-filter').value = '';
        document.getElementById('website-status-filter').value = '';
        document.getElementById('website-frequency-filter').value = '';
        
        appState.update('ui.filters.websites', { 
            search: '', 
            client: '', 
            status: '', 
            frequency: '' 
        });
        this.applyFilters();
    }

    refreshData() {
        return this.loadData();
    }

    // Bulk operations
    async bulkScanWebsites() {
        const activeWebsites = this.filteredWebsites.filter(w => w.is_active);
        
        if (activeWebsites.length === 0) {
            utils.showToast('Nessun sito attivo da scansionare', 'warning');
            return;
        }

        if (!confirm(`Vuoi avviare la scansione di ${activeWebsites.length} siti web attivi?`)) {
            return;
        }

        try {
            const promises = activeWebsites.map(website => 
                apiClient.createScan({ website_id: website.id })
            );
            
            await Promise.all(promises);
            
            utils.showToast(`Avviate ${activeWebsites.length} scansioni`, 'success');
            await this.loadData();
            
        } catch (error) {
            console.error('Error starting bulk scans:', error);
            utils.showToast('Errore nell\'avvio delle scansioni', 'error');
        }
    }

    // Modal Methods
    showAddModal() {
        // Populate client dropdown
        this.populateClientDropdown();
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(document.getElementById('addWebsiteModal'));
            modal.show();
        } else {
            // Fallback
            const modalElement = document.getElementById('addWebsiteModal');
            if (modalElement) {
                modalElement.classList.add('show');
                modalElement.style.display = 'block';
                modalElement.setAttribute('aria-hidden', 'false');
                // Add backdrop
                if (!document.getElementById('modal-backdrop-fallback')) {
                    const backdrop = document.createElement('div');
                    backdrop.className = 'modal-backdrop fade show';
                    backdrop.id = 'modal-backdrop-fallback';
                    document.body.appendChild(backdrop);
                    document.body.classList.add('modal-open');
                }
            }
        }
    }

    populateClientDropdown() {
        const select = document.getElementById('websiteClient');
        if (!select) return;

        const clients = appState.getData('clients') || [];
        
        select.innerHTML = '<option value="">Seleziona cliente...</option>';
        clients.forEach(client => {
            const option = document.createElement('option');
            option.value = client.id;
            option.textContent = client.name;
            select.appendChild(option);
        });
    }

    async addWebsite() {
        const form = document.getElementById('addWebsiteForm');
        if (!form) return;

        const formData = new FormData(form);
        const websiteData = {
            domain: utils.sanitizeURL(formData.get('domain') || document.getElementById('websiteDomain').value),
            name: formData.get('name') || document.getElementById('websiteName').value,
            client_id: parseInt(formData.get('client_id') || document.getElementById('websiteClient').value),
            description: formData.get('description') || document.getElementById('websiteDescription').value,
            scan_frequency: formData.get('scan_frequency') || document.getElementById('scanFrequency').value,
            max_pages: parseInt(formData.get('max_pages') || document.getElementById('maxPages').value) || 1000
        };

        // Validate
        const isValid = utils.validateForm('addWebsiteForm', {
            websiteDomain: { 
                required: true, 
                requiredMessage: 'Il dominio è obbligatorio',
                pattern: /^https?:\/\/.+/,
                patternMessage: 'URL non valido'
            },
            websiteClient: { 
                required: true, 
                requiredMessage: 'Seleziona un cliente' 
            }
        });

        if (!isValid) return;

        try {
            await apiClient.createWebsite(websiteData);
            
            utils.showToast('Sito web aggiunto con successo', 'success');
            
            // Close modal and refresh
            bootstrap.Modal.getInstance(document.getElementById('addWebsiteModal')).hide();
            await this.loadData();
            
        } catch (error) {
            console.error('Error adding website:', error);
            utils.showToast('Errore nell\'aggiunta del sito web', 'error');
        }
    }

    async editWebsite(websiteId) {
        try {
            const website = await apiClient.getWebsite(websiteId);
            
            // Simple prompt-based edit for now
            const newDomain = prompt('Dominio:', website.domain);
            if (newDomain === null) return;
            
            const newName = prompt('Nome sito:', website.name || '');
            if (newName === null) return;
            
            const websiteData = {
                domain: utils.sanitizeURL(newDomain.trim()),
                name: newName.trim(),
                description: website.description || ''
            };
            
            if (!websiteData.domain) {
                utils.showToast('Il dominio è obbligatorio', 'error');
                return;
            }
            
            await apiClient.updateWebsite(websiteId, websiteData);
            utils.showToast('Sito web aggiornato con successo', 'success');
            await this.loadData();
            
        } catch (error) {
            console.error('Error updating website:', error);
            utils.showToast('Errore nell\'aggiornamento del sito web', 'error');
        }
    }

    async deleteWebsite(websiteId) {
        if (!confirm('Sei sicuro di voler eliminare questo sito web? Questa azione eliminerà anche tutte le scansioni associate.')) {
            return;
        }

        try {
            await apiClient.deleteWebsite(websiteId);
            
            utils.showToast('Sito web eliminato con successo', 'success');
            await this.loadData();
            
        } catch (error) {
            console.error('Error deleting website:', error);
            utils.showToast('Errore nell\'eliminazione del sito web', 'error');
        }
    }

    async startScan(websiteId) {
        try {
            const scanData = { website_id: websiteId };
            const scan = await apiClient.createScan(scanData);
            
            utils.showToast('Scansione avviata con successo', 'success');
            
            // Optionally navigate to scans section
            if (window.app) {
                window.app.showSection('scans');
            }
            
        } catch (error) {
            console.error('Error starting scan:', error);
            utils.showToast('Errore nell\'avvio della scansione', 'error');
        }
    }
}

// Export module
window.websites = new WebsitesModule();