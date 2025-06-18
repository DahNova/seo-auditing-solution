// SEO Auditing Solution - Scans Module
class ScansModule {
    constructor() {
        this.filteredScans = [];
        this.searchDebounced = utils.debounce(this.applyFilters.bind(this), 300);
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('scan-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                appState.setFilter('scans', 'search', e.target.value);
                this.searchDebounced();
            });
        }

        // Filter selects
        const statusFilter = document.getElementById('scan-status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                appState.setFilter('scans', 'status', e.target.value);
                this.applyFilters();
            });
        }

        const dateFilter = document.getElementById('scan-date-filter');
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                appState.setFilter('scans', 'date', e.target.value);
                this.applyFilters();
            });
        }

        const scoreFilter = document.getElementById('scan-score-filter');
        if (scoreFilter) {
            scoreFilter.addEventListener('change', (e) => {
                appState.setFilter('scans', 'score', e.target.value);
                this.applyFilters();
            });
        }

        // Per page select
        const perPageSelect = document.getElementById('scans-per-page');
        if (perPageSelect) {
            perPageSelect.addEventListener('change', (e) => {
                appState.setPagination('scans', { 
                    perPage: parseInt(e.target.value), 
                    page: 1 
                });
                this.renderTable();
            });
        }

        // Subscribe to data changes
        appState.subscribe('data.scans', () => {
            this.applyFilters();
        });
    }

    async loadData() {
        try {
            appState.setLoading('scans', true);
            
            // Load scans, websites, and clients to fully enrich scan data
            const [scans, websites, clients] = await Promise.all([
                apiClient.getScans(),
                apiClient.getWebsites(),
                apiClient.getClients()
            ]);
            
            // Enrich scans with website and client data
            const enrichedScans = scans.map(scan => {
                const website = websites.find(w => w.id === scan.website_id);
                let enrichedWebsite = website || null;
                
                if (enrichedWebsite && enrichedWebsite.client_id) {
                    const client = clients.find(c => c.id === enrichedWebsite.client_id);
                    enrichedWebsite = {
                        ...enrichedWebsite,
                        client: client || null
                    };
                }
                
                return {
                    ...scan,
                    website: enrichedWebsite
                };
            });
            
            appState.setData('scans', enrichedScans);
            
            // Update header stats
            this.updateHeaderStats(enrichedScans);

        } catch (error) {
            console.error('Error loading scans:', error);
            utils.showToast('Errore nel caricamento delle scansioni', 'error');
        } finally {
            appState.setLoading('scans', false);
        }
    }

    updateHeaderStats(scans) {
        const completedScans = scans.filter(s => s.status === 'completed').length;
        const runningScans = scans.filter(s => s.status === 'running').length;
        const totalIssues = scans.reduce((total, scan) => {
            return total + (scan.total_issues || 0);
        }, 0);

        // Update header mini stats
        const elementsToUpdate = {
            'completed-scans-header': completedScans,
            'running-scans-header': runningScans,
            'total-issues-header': totalIssues
        };

        Object.entries(elementsToUpdate).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });
    }

    applyFilters() {
        const scans = appState.getData('scans') || [];
        const searchTerm = appState.getFilter('scans', 'search').toLowerCase();
        const statusFilter = appState.getFilter('scans', 'status');
        const dateFilter = appState.getFilter('scans', 'date');
        const scoreFilter = appState.getFilter('scans', 'score');

        // Filter scans
        this.filteredScans = scans.filter(scan => {
            const matchesSearch = !searchTerm || 
                (scan.website?.domain && scan.website.domain.toLowerCase().includes(searchTerm)) ||
                (scan.website?.name && scan.website.name.toLowerCase().includes(searchTerm)) ||
                (scan.website?.client?.name && scan.website.client.name.toLowerCase().includes(searchTerm));
            
            const matchesStatus = !statusFilter || scan.status === statusFilter;
            
            const matchesDate = this.filterByDate(scan, dateFilter);
            
            const matchesScore = this.filterByScore(scan, scoreFilter);

            return matchesSearch && matchesStatus && matchesDate && matchesScore;
        });

        // Sort scans by created date (newest first)
        this.filteredScans.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        // Update pagination
        appState.setPagination('scans', {
            ...appState.getPagination('scans'),
            total: this.filteredScans.length,
            page: 1
        });

        this.renderTable();
        this.updateCounters();
    }

    filterByDate(scan, dateFilter) {
        if (!dateFilter) return true;
        
        const scanDate = new Date(scan.created_at);
        const now = new Date();
        
        switch (dateFilter) {
            case 'today':
                const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                return scanDate >= today;
            case 'week':
                const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                return scanDate >= weekAgo;
            case 'month':
                const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                return scanDate >= monthAgo;
            default:
                return true;
        }
    }

    filterByScore(scan, scoreFilter) {
        if (!scoreFilter || !scan.seo_score) return true;
        
        const score = scan.seo_score;
        switch (scoreFilter) {
            case 'excellent':
                return score >= 90;
            case 'good':
                return score >= 70 && score < 90;
            case 'fair':
                return score >= 50 && score < 70;
            case 'poor':
                return score < 50;
            default:
                return true;
        }
    }

    renderTable() {
        const tbody = document.getElementById('scans-table-body');
        if (!tbody) return;

        const pagination = appState.getPagination('scans');
        const startIndex = (pagination.page - 1) * pagination.perPage;
        const endIndex = startIndex + pagination.perPage;
        const pageScans = this.filteredScans.slice(startIndex, endIndex);

        if (pageScans.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-4">
                        <div class="text-muted">
                            <i class="bi bi-search fs-1 opacity-50"></i>
                            <p class="mt-2">Nessuna scansione trovata</p>
                            <button class="btn btn-primary btn-sm" onclick="scans.showNewScanModal()">
                                <i class="bi bi-plus"></i> Avvia Prima Scansione
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = pageScans.map(scan => `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="scan-favicon me-3">
                            <i class="bi bi-globe text-primary fs-4"></i>
                        </div>
                        <div>
                            <div class="fw-bold">
                                ${scan.website?.domain || 'Sito sconosciuto'}
                            </div>
                            ${scan.website?.client?.name ? 
                                `<small class="text-muted">Cliente: ${scan.website.client.name}</small>` : 
                                ''
                            }
                        </div>
                    </div>
                </td>
                <td>
                    <div class="text-muted small">
                        ${utils.formatDate(scan.created_at)}
                    </div>
                </td>
                <td>
                    ${this.getScanStatusBadge(scan)}
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <span class="fw-bold me-2">${scan.pages_found || scan.pages_scanned || 0}</span>
                        ${(scan.pages_found || scan.pages_scanned) > 0 ? '<i class="bi bi-file-earmark text-info"></i>' : ''}
                    </div>
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <span class="fw-bold me-2 ${this.getIssuesColorClass(scan.total_issues)}">${scan.total_issues || 0}</span>
                        ${scan.total_issues > 0 ? '<i class="bi bi-exclamation-triangle text-warning"></i>' : ''}
                    </div>
                </td>
                <td>
                    ${scan.seo_score ? utils.getSEOScoreBadge(scan.seo_score) : '<span class="text-muted">-</span>'}
                </td>
                <td>
                    ${this.getScanActions(scan)}
                </td>
            </tr>
        `).join('');

        this.renderPagination();
    }

    getScanStatusBadge(scan) {
        const statusMap = {
            'running': { class: 'bg-info', text: 'In Corso', icon: 'arrow-clockwise' },
            'completed': { class: 'bg-success', text: 'Completata', icon: 'check-circle' },
            'failed': { class: 'bg-danger', text: 'Fallita', icon: 'x-circle' },
            'cancelled': { class: 'bg-secondary', text: 'Annullata', icon: 'dash-circle' },
            'pending': { class: 'bg-warning', text: 'In Attesa', icon: 'clock' }
        };
        
        const config = statusMap[scan.status] || { class: 'bg-secondary', text: scan.status, icon: 'question' };
        return `<span class="badge ${config.class}">
            <i class="bi bi-${config.icon}"></i> ${config.text}
        </span>`;
    }

    getIssuesColorClass(issuesCount) {
        if (!issuesCount) return 'text-success';
        if (issuesCount >= 10) return 'text-danger';
        if (issuesCount >= 5) return 'text-warning';
        return 'text-info';
    }

    getScanActions(scan) {
        const actions = [];
        
        // View results (always available)
        if (scan.status === 'completed') {
            actions.push(`
                <button class="btn btn-outline-primary btn-sm" onclick="scans.viewResults(${scan.id})" title="Visualizza Risultati">
                    <i class="bi bi-eye"></i>
                </button>
            `);
            
            actions.push(`
                <button class="btn btn-outline-success btn-sm" onclick="scans.downloadReport(${scan.id})" title="Scarica Report">
                    <i class="bi bi-download"></i>
                </button>
            `);
        }
        
        // Retry (for failed scans)
        if (scan.status === 'failed') {
            actions.push(`
                <button class="btn btn-outline-warning btn-sm" onclick="scans.retryScan(${scan.id})" title="Riprova">
                    <i class="bi bi-arrow-clockwise"></i>
                </button>
            `);
        }
        
        // Cancel (for running scans)
        if (scan.status === 'running') {
            actions.push(`
                <button class="btn btn-outline-danger btn-sm" onclick="scans.cancelScan(${scan.id})" title="Annulla">
                    <i class="bi bi-stop-circle"></i>
                </button>
            `);
        }
        
        // Delete (always available)
        actions.push(`
            <button class="btn btn-outline-danger btn-sm" onclick="scans.deleteScan(${scan.id})" title="Elimina">
                <i class="bi bi-trash"></i>
            </button>
        `);
        
        return `<div class="btn-group btn-group-sm">${actions.join('')}</div>`;
    }

    renderPagination() {
        const container = document.getElementById('scans-pagination');
        if (!container) return;

        const pagination = appState.getPagination('scans');
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
                    onclick="scans.goToPage(${pagination.page - 1})"
                    ${pagination.page === 1 ? 'disabled' : ''}>
                <i class="bi bi-chevron-left"></i>
            </button>
        `);

        // Page numbers
        for (let i = startPage; i <= endPage; i++) {
            pages.push(`
                <button class="btn ${i === pagination.page ? 'btn-primary' : 'btn-outline-primary'}" 
                        onclick="scans.goToPage(${i})">
                    ${i}
                </button>
            `);
        }

        // Next button
        pages.push(`
            <button class="btn btn-outline-primary ${pagination.page === totalPages ? 'disabled' : ''}" 
                    onclick="scans.goToPage(${pagination.page + 1})"
                    ${pagination.page === totalPages ? 'disabled' : ''}>
                <i class="bi bi-chevron-right"></i>
            </button>
        `);

        container.innerHTML = pages.join('');
    }

    updateCounters() {
        const shownElement = document.getElementById('scans-shown');
        const totalElement = document.getElementById('scans-total');
        
        if (shownElement) shownElement.textContent = this.filteredScans.length;
        if (totalElement) totalElement.textContent = appState.getData('scans').length;
    }

    goToPage(page) {
        const pagination = appState.getPagination('scans');
        const totalPages = Math.ceil(pagination.total / pagination.perPage);
        
        if (page < 1 || page > totalPages) return;
        
        appState.setPagination('scans', { ...pagination, page });
        this.renderTable();
    }

    clearFilters() {
        document.getElementById('scan-search').value = '';
        document.getElementById('scan-status-filter').value = '';
        document.getElementById('scan-date-filter').value = '';
        document.getElementById('scan-score-filter').value = '';
        
        appState.update('ui.filters.scans', { 
            search: '', 
            status: '', 
            date: '', 
            score: '' 
        });
        this.applyFilters();
    }

    refreshData() {
        return this.loadData();
    }

    // Bulk operations
    async downloadAllReports() {
        const completedScans = this.filteredScans.filter(s => s.status === 'completed');
        
        if (completedScans.length === 0) {
            utils.showToast('Nessuna scansione completata da scaricare', 'warning');
            return;
        }

        if (!confirm(`Vuoi scaricare ${completedScans.length} report PDF?`)) {
            return;
        }

        try {
            utils.showToast('Avvio download...', 'info');
            
            for (const scan of completedScans) {
                await this.downloadReport(scan.id);
                // Small delay to avoid overwhelming the server
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            utils.showToast('Download completati', 'success');
            
        } catch (error) {
            console.error('Error downloading reports:', error);
            utils.showToast('Errore nel download dei report', 'error');
        }
    }

    // Modal Methods
    showNewScanModal() {
        // Populate website dropdown
        this.populateWebsiteDropdown();
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(document.getElementById('newScanModal'));
            modal.show();
        } else {
            // Fallback
            const modalElement = document.getElementById('newScanModal');
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

    populateWebsiteDropdown() {
        const select = document.getElementById('scanWebsite');
        if (!select) return;

        const websites = appState.getData('websites') || [];
        const activeWebsites = websites.filter(w => w.is_active);
        
        select.innerHTML = '<option value="">Seleziona sito web...</option>';
        activeWebsites.forEach(website => {
            const option = document.createElement('option');
            option.value = website.id;
            option.textContent = `${website.domain} ${website.client ? `(${website.client.name})` : ''}`;
            select.appendChild(option);
        });
    }

    async startNewScan() {
        const websiteSelect = document.getElementById('scanWebsite');
        if (!websiteSelect || !websiteSelect.value) {
            utils.showToast('Seleziona un sito web', 'error');
            return;
        }

        try {
            const scanData = { 
                website_id: parseInt(websiteSelect.value) 
            };
            
            const scan = await apiClient.createScan(scanData);
            
            utils.showToast('Scansione avviata con successo', 'success');
            
            // Close modal and refresh
            bootstrap.Modal.getInstance(document.getElementById('newScanModal')).hide();
            await this.loadData();
            
        } catch (error) {
            console.error('Error starting scan:', error);
            utils.showToast('Errore nell\'avvio della scansione', 'error');
        }
    }

    // Scan Actions
    async viewResults(scanId) {
        try {
            // Load scan results and navigate to results section
            if (window.scanResults) {
                await window.scanResults.loadScanData(scanId);
                window.app.showSection('scan-results');
            } else {
                utils.showToast('Modulo risultati scansioni non ancora implementato', 'warning');
            }
            
        } catch (error) {
            console.error('Error viewing scan results:', error);
            utils.showToast('Errore nel caricamento dei risultati', 'error');
        }
    }

    async downloadReport(scanId) {
        try {
            const blob = await apiClient.downloadScanReport(scanId);
            
            // Get scan info for filename
            const scans = appState.getData('scans') || [];
            const scan = scans.find(s => s.id === scanId);
            const domain = scan?.website?.domain?.replace(/[^a-zA-Z0-9]/g, '_') || 'scan';
            const date = new Date().toISOString().split('T')[0];
            const filename = `SEO_Report_${domain}_${date}.pdf`;
            
            utils.downloadBlob(blob, filename);
            utils.showToast('Report scaricato', 'success');
            
        } catch (error) {
            console.error('Error downloading report:', error);
            utils.showToast('Errore nel download del report', 'error');
        }
    }

    async retryScan(scanId) {
        if (!confirm('Vuoi riprovare questa scansione?')) return;

        try {
            await apiClient.retryScan(scanId);
            
            utils.showToast('Scansione riavviata', 'success');
            await this.loadData();
            
        } catch (error) {
            console.error('Error retrying scan:', error);
            utils.showToast('Errore nel riavvio della scansione', 'error');
        }
    }

    async cancelScan(scanId) {
        if (!confirm('Vuoi annullare questa scansione?')) return;

        try {
            await apiClient.cancelScan(scanId);
            
            utils.showToast('Scansione annullata', 'success');
            await this.loadData();
            
        } catch (error) {
            console.error('Error cancelling scan:', error);
            utils.showToast('Errore nell\'annullamento della scansione', 'error');
        }
    }

    async deleteScan(scanId) {
        if (!confirm('Sei sicuro di voler eliminare questa scansione? Questa azione non può essere annullata.')) {
            return;
        }

        try {
            await apiClient.deleteScan(scanId);
            
            utils.showToast('Scansione eliminata', 'success');
            await this.loadData();
            
        } catch (error) {
            console.error('Error deleting scan:', error);
            utils.showToast('Errore nell\'eliminazione della scansione', 'error');
        }
    }

    // Alias method for templated version compatibility
    async createScan() {
        return this.startNewScan();
    }
}

// Export module
window.scans = new ScansModule();