// SEO Auditing Solution - Modular Frontend Application
class SEOAuditingApp {
    constructor() {
        this.currentSection = 'dashboard';
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupModernFeatures();
        await this.loadInitialData();
        
        // Don't force dashboard for templated pages
        if (!window.location.pathname.startsWith('/templated/')) {
            this.showSection('dashboard');
        }
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                // Don't prevent default for templated navigation links
                const linkElement = e.target.closest('[data-section]');
                const href = linkElement.getAttribute('href');
                
                // If it's a templated URL, allow normal navigation
                if (href && href.startsWith('/templated/')) {
                    return; // Let the browser handle the navigation
                }
                
                // For old SPA navigation (href="#"), prevent default
                e.preventDefault();
                const section = linkElement.dataset.section;
                this.showSection(section);
            });
        });

        // Modal reset listeners
        this.setupModalListeners();
    }

    setupModalListeners() {
        const modals = [
            'addClientModal',
            'addWebsiteModal', 
            'newScanModal',
            'scheduleModal',
            'editScheduleModal'
        ];

        modals.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.addEventListener('hidden.bs.modal', () => {
                    utils.resetModal(modalId);
                });
            }
        });
    }

    setupModernFeatures() {
        // Add loading states and animations
        document.body.classList.add('app-loaded');
        
        // Setup toast container
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1050';
            document.body.appendChild(container);
        }

        // Setup keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case '1':
                        e.preventDefault();
                        this.showSection('dashboard');
                        break;
                    case '2':
                        e.preventDefault();
                        this.showSection('clients');
                        break;
                    case '3':
                        e.preventDefault();
                        this.showSection('websites');
                        break;
                    case '4':
                        e.preventDefault();
                        this.showSection('scans');
                        break;
                    case '5':
                        e.preventDefault();
                        this.showSection('scheduler');
                        break;
                }
            }
        });
    }

    async loadInitialData() {
        try {
            appState.setLoading('global', true);
            
            // Load data for all modules
            await Promise.all([
                dashboard.loadData(),
                clients.loadData(),
                websites.loadData()
            ]);

        } catch (error) {
            console.error('Error loading initial data:', error);
            utils.showToast('Errore nel caricamento dei dati iniziali', 'error');
        } finally {
            appState.setLoading('global', false);
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
        document.querySelectorAll('.nav-link, .mobile-nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        document.querySelectorAll(`[data-section="${sectionName}"]`).forEach(link => {
            link.classList.add('active');
        });

        // Update state
        appState.setCurrentSection(sectionName);
        this.currentSection = sectionName;

        // Load section-specific data
        this.loadSectionData(sectionName);
    }

    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'dashboard':
                await dashboard.loadData();
                break;
            case 'clients':
                await clients.loadData();
                break;
            case 'websites':
                await websites.loadData();
                break;
            case 'scans':
                await scans.loadData();
                break;
            case 'scheduler':
                await scheduler.loadData();
                break;
        }
    }

    // Global refresh function
    async refreshData() {
        try {
            appState.setLoading('global', true);
            await this.loadSectionData(this.currentSection);
            utils.showToast('Dati aggiornati con successo', 'success');
        } catch (error) {
            console.error('Error refreshing data:', error);
            utils.showToast('Errore nell\'aggiornamento dei dati', 'error');
        } finally {
            appState.setLoading('global', false);
        }
    }

    // Modal methods for backward compatibility
    showAddClientModal() {
        clients.showAddModal();
    }

    showAddWebsiteModal() {
        websites.showAddModal();
    }

    showNewScanModal() {
        scans.showNewScanModal();
    }

    showScheduleModal() {
        scheduler.showScheduleModal();
    }

    // Client methods for backward compatibility
    async addClient() {
        return clients.addClient();
    }

    async updateClient(clientId) {
        return clients.updateClient(clientId);
    }

    async deleteClient(clientId) {
        return clients.deleteClient(clientId);
    }

    // Utility methods
    formatDate(dateString) {
        return utils.formatDate(dateString);
    }

    formatRelativeTime(dateString) {
        return utils.formatRelativeTime(dateString);
    }

    getStatusBadge(status) {
        return utils.getStatusBadge(status);
    }

    getSEOScoreBadge(score) {
        return utils.getSEOScoreBadge(score);
    }

    // Module delegation methods for backward compatibility
    refreshClientsData() {
        // For templated pages, just reload the page
        if (window.location.pathname.startsWith('/templated/')) {
            window.location.reload();
            return;
        }
        return clients.refreshData();
    }

    refreshWebsitesData() {
        // For templated pages, just reload the page
        if (window.location.pathname.startsWith('/templated/')) {
            window.location.reload();
            return;
        }
        return websites.refreshData();
    }

    refreshScansData() {
        // For templated pages, just reload the page
        if (window.location.pathname.startsWith('/templated/')) {
            window.location.reload();
            return;
        }
        // For SPA, use the old method
        return scans.refreshData();
    }

    refreshSchedulerData() {
        return scheduler.refreshData();
    }

    clearClientsFilters() {
        return clients.clearFilters();
    }

    clearWebsitesFilters() {
        return websites.clearFilters();
    }

    // Scan action methods for templated compatibility
    async cancelScan(scanId) {
        try {
            await scans.cancelScan(scanId);
            // For templated pages, reload to show updated data
            if (window.location.pathname.startsWith('/templated/')) {
                window.location.reload();
            }
        } catch (error) {
            console.error('Error cancelling scan:', error);
        }
    }

    async retryScan(scanId) {
        try {
            await scans.retryScan(scanId);
            // For templated pages, reload to show updated data
            if (window.location.pathname.startsWith('/templated/')) {
                window.location.reload();
            }
        } catch (error) {
            console.error('Error retrying scan:', error);
        }
    }

    async deleteScan(scanId) {
        try {
            await scans.deleteScan(scanId);
            // For templated pages, reload to show updated data
            if (window.location.pathname.startsWith('/templated/')) {
                window.location.reload();
            }
        } catch (error) {
            console.error('Error deleting scan:', error);
        }
    }

    clearScansFilters() {
        return scans.clearFilters();
    }

    bulkScanWebsites() {
        return websites.bulkScanWebsites();
    }

    downloadAllReports() {
        return scans.downloadAllReports();
    }

    purgeQueue() {
        return scheduler.purgeQueue();
    }

    pauseScheduler() {
        return scheduler.pauseScheduler();
    }

    resumeScheduler() {
        return scheduler.resumeScheduler();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    window.app = new SEOAuditingApp();
    
    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        utils.showToast('Si è verificato un errore imprevisto', 'error');
    });

    // Global unhandled promise rejection handler
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        utils.showToast('Errore nella comunicazione con il server', 'error');
    });

    console.log('🚀 SEO Auditing Solution - Modular Version Loaded');
    console.log('📊 Modules available:', {
        apiClient: !!window.apiClient,
        appState: !!window.appState,
        utils: !!window.utils,
        dashboard: !!window.dashboard,
        clients: !!window.clients,
        websites: !!window.websites,
        scans: !!window.scans,
        scanResults: !!window.scanResults,
        scheduler: !!window.scheduler
    });
});