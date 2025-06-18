// SEO Auditing Solution - Clients Module
class ClientsModule {
    constructor() {
        this.filteredClients = [];
        this.searchDebounced = utils.debounce(this.applyFilters.bind(this), 300);
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('client-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                appState.setFilter('clients', 'search', e.target.value);
                this.searchDebounced();
            });
        }

        // Filter select
        const filterSelect = document.getElementById('client-filter');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                appState.setFilter('clients', 'status', e.target.value);
                this.applyFilters();
            });
        }

        // Sort select
        const sortSelect = document.getElementById('client-sort');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => {
                this.applyFilters();
            });
        }

        // Per page select
        const perPageSelect = document.getElementById('clients-per-page');
        if (perPageSelect) {
            perPageSelect.addEventListener('change', (e) => {
                appState.setPagination('clients', { 
                    perPage: parseInt(e.target.value), 
                    page: 1 
                });
                this.renderTable();
            });
        }

        // Subscribe to data changes
        appState.subscribe('data.clients', () => {
            this.applyFilters();
        });
    }

    async loadData() {
        try {
            appState.setLoading('clients', true);
            
            // Load both clients and websites to calculate relationships
            const [clients, websites] = await Promise.all([
                apiClient.getClients(),
                apiClient.getWebsites()
            ]);
            
            // Enrich clients with website count and active status
            const enrichedClients = clients.map(client => ({
                ...client,
                websites: websites.filter(w => w.client_id === client.id),
                is_active: true // All clients are considered active by default
            }));
            
            appState.setData('clients', enrichedClients);
            
            // Update header stats
            const element = document.getElementById('clients-count-header');
            if (element) element.textContent = enrichedClients.length;

        } catch (error) {
            console.error('Error loading clients:', error);
            utils.showToast('Errore nel caricamento dei clienti', 'error');
        } finally {
            appState.setLoading('clients', false);
        }
    }

    applyFilters() {
        const clients = appState.getData('clients') || [];
        const searchTerm = appState.getFilter('clients', 'search').toLowerCase();
        const statusFilter = appState.getFilter('clients', 'status');
        const sortSelect = document.getElementById('client-sort');
        const sortBy = sortSelect ? sortSelect.value : 'name';

        // Filter clients
        this.filteredClients = clients.filter(client => {
            const matchesSearch = !searchTerm || 
                client.name.toLowerCase().includes(searchTerm) ||
                (client.contact_email && client.contact_email.toLowerCase().includes(searchTerm));
            
            const matchesStatus = !statusFilter || 
                (statusFilter === 'active' && client.is_active) ||
                (statusFilter === 'inactive' && !client.is_active);

            return matchesSearch && matchesStatus;
        });

        // Sort clients
        this.filteredClients.sort((a, b) => {
            switch (sortBy) {
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'created':
                    return new Date(b.created_at) - new Date(a.created_at);
                case 'websites':
                    return (b.websites?.length || 0) - (a.websites?.length || 0);
                default:
                    return 0;
            }
        });

        // Update pagination
        appState.setPagination('clients', {
            ...appState.getPagination('clients'),
            total: this.filteredClients.length,
            page: 1
        });

        this.renderTable();
        this.updateCounters();
    }

    renderTable() {
        const tbody = document.getElementById('clients-table-body');
        if (!tbody) return;

        const pagination = appState.getPagination('clients');
        const startIndex = (pagination.page - 1) * pagination.perPage;
        const endIndex = startIndex + pagination.perPage;
        const pageClients = this.filteredClients.slice(startIndex, endIndex);

        if (pageClients.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center py-4">
                        <div class="text-muted">
                            <i class="bi bi-people fs-1 opacity-50"></i>
                            <p class="mt-2">Nessun cliente trovato</p>
                            <button class="btn btn-primary btn-sm" onclick="clients.showAddModal()">
                                <i class="bi bi-plus"></i> Aggiungi Primo Cliente
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = pageClients.map(client => `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="client-avatar me-3">
                            <i class="bi bi-person-circle fs-4 text-primary"></i>
                        </div>
                        <div>
                            <div class="fw-bold">${client.name}</div>
                            ${client.description ? `<small class="text-muted">${client.description}</small>` : ''}
                        </div>
                    </div>
                </td>
                <td>
                    ${client.contact_email ? 
                        `<a href="mailto:${client.contact_email}" class="text-decoration-none">
                            <i class="bi bi-envelope me-1"></i>${client.contact_email}
                        </a>` : 
                        '<span class="text-muted">-</span>'
                    }
                </td>
                <td>
                    <span class="badge bg-info">
                        <i class="bi bi-globe"></i> ${client.websites?.length || 0}
                    </span>
                </td>
                <td>
                    <span class="badge ${client.is_active ? 'bg-success' : 'bg-secondary'}">
                        <i class="bi bi-${client.is_active ? 'check-circle' : 'dash-circle'}"></i>
                        ${client.is_active ? 'Attivo' : 'Inattivo'}
                    </span>
                </td>
                <td>
                    <div class="text-muted small">
                        ${utils.formatDate(client.updated_at)}
                    </div>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="clients.editClient(${client.id})" title="Modifica">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="clients.deleteClient(${client.id})" title="Elimina">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        this.renderPagination();
    }

    renderPagination() {
        const container = document.getElementById('clients-pagination');
        if (!container) return;

        const pagination = appState.getPagination('clients');
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
                    onclick="clients.goToPage(${pagination.page - 1})"
                    ${pagination.page === 1 ? 'disabled' : ''}>
                <i class="bi bi-chevron-left"></i>
            </button>
        `);

        // Page numbers
        for (let i = startPage; i <= endPage; i++) {
            pages.push(`
                <button class="btn ${i === pagination.page ? 'btn-primary' : 'btn-outline-primary'}" 
                        onclick="clients.goToPage(${i})">
                    ${i}
                </button>
            `);
        }

        // Next button
        pages.push(`
            <button class="btn btn-outline-primary ${pagination.page === totalPages ? 'disabled' : ''}" 
                    onclick="clients.goToPage(${pagination.page + 1})"
                    ${pagination.page === totalPages ? 'disabled' : ''}>
                <i class="bi bi-chevron-right"></i>
            </button>
        `);

        container.innerHTML = pages.join('');
    }

    updateCounters() {
        const shownElement = document.getElementById('clients-shown');
        const totalElement = document.getElementById('clients-total');
        
        if (shownElement) shownElement.textContent = this.filteredClients.length;
        if (totalElement) totalElement.textContent = appState.getData('clients').length;
    }

    goToPage(page) {
        const pagination = appState.getPagination('clients');
        const totalPages = Math.ceil(pagination.total / pagination.perPage);
        
        if (page < 1 || page > totalPages) return;
        
        appState.setPagination('clients', { ...pagination, page });
        this.renderTable();
    }

    clearFilters() {
        document.getElementById('client-search').value = '';
        document.getElementById('client-filter').value = '';
        document.getElementById('client-sort').value = 'name';
        
        appState.update('ui.filters.clients', { search: '', status: '' });
        this.applyFilters();
    }

    refreshData() {
        return this.loadData();
    }

    // Modal Methods
    showAddModal() {
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(document.getElementById('addClientModal'));
            modal.show();
        } else {
            // Fallback - try to show modal directly
            const modalElement = document.getElementById('addClientModal');
            if (modalElement) {
                modalElement.classList.add('show');
                modalElement.style.display = 'block';
                modalElement.setAttribute('aria-hidden', 'false');
                // Add backdrop
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                backdrop.id = 'modal-backdrop-fallback';
                document.body.appendChild(backdrop);
                document.body.classList.add('modal-open');
            }
        }
    }

    async addClient() {
        const form = document.getElementById('addClientForm');
        if (!form) return;

        const formData = new FormData(form);
        const clientData = {
            name: formData.get('name') || document.getElementById('clientName').value,
            contact_email: formData.get('email') || document.getElementById('clientEmail').value,
            description: formData.get('description') || document.getElementById('clientDescription').value
        };

        // Validate
        const isValid = utils.validateForm('addClientForm', {
            clientName: { 
                required: true, 
                requiredMessage: 'Il nome del cliente è obbligatorio' 
            },
            clientEmail: { 
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, 
                patternMessage: 'Email non valida' 
            }
        });

        if (!isValid) return;

        try {
            await apiClient.createClient(clientData);
            
            utils.showToast('Cliente aggiunto con successo', 'success');
            
            // Close modal and refresh
            bootstrap.Modal.getInstance(document.getElementById('addClientModal')).hide();
            await this.loadData();
            
        } catch (error) {
            console.error('Error adding client:', error);
            utils.showToast('Errore nell\'aggiunta del cliente', 'error');
        }
    }

    async editClient(clientId) {
        try {
            const client = await apiClient.getClient(clientId);
            
            // For now, use a simple prompt-based edit (TODO: create proper edit modal)
            const newName = prompt('Nome cliente:', client.name);
            if (newName === null) return; // User cancelled
            
            const newEmail = prompt('Email cliente:', client.contact_email || '');
            if (newEmail === null) return; // User cancelled
            
            const newDescription = prompt('Descrizione:', client.description || '');
            if (newDescription === null) return; // User cancelled
            
            const clientData = {
                name: newName.trim(),
                contact_email: newEmail.trim(),
                description: newDescription.trim()
            };
            
            if (!clientData.name) {
                utils.showToast('Il nome del cliente è obbligatorio', 'error');
                return;
            }
            
            await apiClient.updateClient(clientId, clientData);
            utils.showToast('Cliente aggiornato con successo', 'success');
            await this.loadData();
            
        } catch (error) {
            console.error('Error updating client:', error);
            utils.showToast('Errore nell\'aggiornamento del cliente', 'error');
        }
    }

    async updateClient() {
        const clientId = window.editingClientId;
        if (!clientId) return;

        const form = document.getElementById('editClientForm');
        if (!form) return;

        const formData = new FormData(form);
        const clientData = {
            name: formData.get('name') || document.getElementById('editClientName').value,
            contact_email: formData.get('email') || document.getElementById('editClientEmail').value,
            description: formData.get('description') || document.getElementById('editClientDescription').value
        };

        try {
            await apiClient.updateClient(clientId, clientData);
            
            utils.showToast('Cliente aggiornato con successo', 'success');
            
            // Close modal and refresh
            bootstrap.Modal.getInstance(document.getElementById('editClientModal')).hide();
            await this.loadData();
            
        } catch (error) {
            console.error('Error updating client:', error);
            utils.showToast('Errore nell\'aggiornamento del cliente', 'error');
        }
    }

    async deleteClient(clientId) {
        if (!confirm('Sei sicuro di voler eliminare questo cliente? Questa azione non può essere annullata.')) {
            return;
        }

        try {
            await apiClient.deleteClient(clientId);
            
            utils.showToast('Cliente eliminato con successo', 'success');
            await this.loadData();
            
        } catch (error) {
            console.error('Error deleting client:', error);
            utils.showToast('Errore nell\'eliminazione del cliente', 'error');
        }
    }

    // Alias method for templated version compatibility
    async createClient() {
        return this.addClient();
    }
}

// Export module
window.clients = new ClientsModule();