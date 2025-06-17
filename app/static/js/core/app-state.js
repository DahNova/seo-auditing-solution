// SEO Auditing Solution - Application State Management
class AppState extends EventTarget {
    constructor() {
        super();
        this.state = {
            // Current section
            currentSection: 'dashboard',
            
            // Loading states
            loading: {
                global: false,
                clients: false,
                websites: false,
                scans: false,
                scheduler: false
            },
            
            // Data
            data: {
                clients: [],
                websites: [],
                scans: [],
                schedulerStatus: null,
                activeTasks: [],
                recentTasks: [],
                scheduledScans: [],
                schedulerStats: null
            },
            
            // UI State
            ui: {
                selectedItems: {
                    client: null,
                    website: null,
                    scan: null
                },
                filters: {
                    clients: { search: '', status: '' },
                    websites: { search: '', client: '', status: '', frequency: '' },
                    scans: { search: '', status: '', date: '', score: '' }
                },
                pagination: {
                    clients: { page: 1, perPage: 25, total: 0 },
                    websites: { page: 1, perPage: 25, total: 0 },
                    scans: { page: 1, perPage: 25, total: 0 }
                },
                modals: {
                    addClient: false,
                    addWebsite: false,
                    newScan: false,
                    schedule: false,
                    editSchedule: false
                }
            },
            
            // Current scan results
            scanResults: {
                scanId: null,
                pages: [],
                issues: [],
                totalPages: 0,
                totalIssues: 0,
                currentPage: 1
            }
        };
        
        // Subscribe to state changes for debugging
        this.addEventListener('stateChange', (event) => {
            console.log('State changed:', event.detail);
        });
    }

    // Get state value
    get(path) {
        return this.getDeepValue(this.state, path);
    }

    // Set state value and emit event
    set(path, value) {
        const oldValue = this.get(path);
        this.setDeepValue(this.state, path, value);
        
        this.dispatchEvent(new CustomEvent('stateChange', {
            detail: { path, value, oldValue }
        }));
    }

    // Update state (shallow merge for objects)
    update(path, updates) {
        const currentValue = this.get(path);
        if (typeof currentValue === 'object' && currentValue !== null) {
            this.set(path, { ...currentValue, ...updates });
        } else {
            this.set(path, updates);
        }
    }

    // Helper methods
    getDeepValue(obj, path) {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    }

    setDeepValue(obj, path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((current, key) => {
            if (!(key in current)) current[key] = {};
            return current[key];
        }, obj);
        target[lastKey] = value;
    }

    // Convenience methods for common operations
    setLoading(module, isLoading) {
        this.set(`loading.${module}`, isLoading);
    }

    setCurrentSection(section) {
        this.set('currentSection', section);
    }

    setData(dataType, data) {
        this.set(`data.${dataType}`, data);
    }

    getData(dataType) {
        return this.get(`data.${dataType}`);
    }

    setFilter(module, filterType, value) {
        this.set(`ui.filters.${module}.${filterType}`, value);
    }

    getFilter(module, filterType) {
        return this.get(`ui.filters.${module}.${filterType}`);
    }

    setPagination(module, paginationData) {
        this.update(`ui.pagination.${module}`, paginationData);
    }

    getPagination(module) {
        return this.get(`ui.pagination.${module}`);
    }

    setModalState(modalName, isOpen) {
        this.set(`ui.modals.${modalName}`, isOpen);
    }

    getModalState(modalName) {
        return this.get(`ui.modals.${modalName}`);
    }

    setSelectedItem(itemType, item) {
        this.set(`ui.selectedItems.${itemType}`, item);
    }

    getSelectedItem(itemType) {
        return this.get(`ui.selectedItems.${itemType}`);
    }

    // Scan results methods
    setScanResults(scanId, pages = [], issues = []) {
        this.update('scanResults', {
            scanId,
            pages,
            issues,
            totalPages: pages.length,
            totalIssues: issues.length
        });
    }

    getScanResults() {
        return this.get('scanResults');
    }

    // Subscribe to state changes
    subscribe(path, callback) {
        const handler = (event) => {
            if (event.detail.path === path || event.detail.path.startsWith(path + '.')) {
                callback(event.detail.value, event.detail.oldValue);
            }
        };
        this.addEventListener('stateChange', handler);
        
        // Return unsubscribe function
        return () => this.removeEventListener('stateChange', handler);
    }

    // Clear all data (useful for logout/reset)
    reset() {
        this.state.data = {
            clients: [],
            websites: [],
            scans: [],
            schedulerStatus: null,
            activeTasks: [],
            recentTasks: [],
            scheduledScans: [],
            schedulerStats: null
        };
        
        this.state.ui.selectedItems = {
            client: null,
            website: null,
            scan: null
        };
        
        this.dispatchEvent(new CustomEvent('stateChange', {
            detail: { path: 'reset', value: null, oldValue: null }
        }));
    }
}

// Export singleton instance
window.appState = new AppState();