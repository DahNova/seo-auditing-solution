// SEO Auditing Solution - Minimal HTMX + Alpine.js Application
// Modern 2025 approach with minimal JavaScript

// HTMX Configuration
document.addEventListener('DOMContentLoaded', function() {
    
    // Configure HTMX
    htmx.config.defaultSwapStyle = 'outerHTML';
    htmx.config.defaultSwapDelay = 200;
    htmx.config.scrollBehavior = 'smooth';
    
    // Global HTMX event handlers
    document.body.addEventListener('htmx:configRequest', function(evt) {
        // Add CSRF token if needed
        evt.detail.headers['X-Requested-With'] = 'XMLHttpRequest';
    });
    
    document.body.addEventListener('htmx:responseError', function(evt) {
        showToast('Errore nella comunicazione con il server', 'error');
    });
    
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        // Re-initialize Bootstrap tooltips after HTMX updates
        initializeTooltips();
    });
    
    // Handle HTMX modal trigger events
    document.body.addEventListener('showModal', function(evt) {
        // Find the modal in the swapped content and show it
        setTimeout(() => {
            const modal = document.querySelector('.modal');
            if (modal) {
                const bootstrapModal = new bootstrap.Modal(modal, {
                    backdrop: true,
                    keyboard: true,
                    focus: true
                });
                bootstrapModal.show();
            }
        }, 100);
    });
    
    console.log('🚀 SEO Auditing Solution - HTMX Version Loaded');
});

// Modal Management
function showModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement, {
            backdrop: true,
            keyboard: true,
            focus: true
        });
        modal.show();
    }
}

function closeModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
    }
}

// Toast Notifications (Minimal Implementation)
function showToast(message, type = 'info') {
    const toastContainer = getOrCreateToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const iconClass = getToastIcon(type);
    const bgClass = getToastBackground(type);
    
    const toastHTML = `
        <div class="toast ${bgClass} text-white" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="bi ${iconClass} me-2"></i>
                <strong class="me-auto">SEOAudit</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();
    
    // Auto remove after hide
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
    }
    return container;
}

function getToastIcon(type) {
    const icons = {
        'success': 'bi-check-circle',
        'error': 'bi-x-circle',
        'warning': 'bi-exclamation-triangle',
        'info': 'bi-info-circle'
    };
    return icons[type] || icons['info'];
}

function getToastBackground(type) {
    const backgrounds = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-primary'
    };
    return backgrounds[type] || backgrounds['info'];
}

// Bootstrap Components Initialization
function initializeTooltips() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Search functionality with Alpine.js
window.searchData = function(searchTerm, items, searchFields) {
    if (!searchTerm) return items;
    
    const term = searchTerm.toLowerCase();
    return items.filter(item => {
        return searchFields.some(field => {
            const value = getNestedProperty(item, field);
            return value && value.toString().toLowerCase().includes(term);
        });
    });
}

function getNestedProperty(obj, path) {
    return path.split('.').reduce((current, key) => current && current[key], obj);
}

// Form validation helpers
window.validateEmail = function(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

window.validateUrl = function(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// Global functions for button actions (HTMX compatible)
window.showAddClientModal = function() {
    htmx.ajax('GET', '/htmx/modals/add-client', {
        target: '#modal-container',
        swap: 'innerHTML'
    }).then(() => {
        showModal('clientModal');
    });
}

window.showAddWebsiteModal = function() {
    htmx.ajax('GET', '/htmx/modals/add-website', {
        target: '#modal-container',
        swap: 'innerHTML'
    }).then(() => {
        showModal('websiteModal');
    });
}

window.showAddScanModal = function() {
    htmx.ajax('GET', '/htmx/modals/add-scan', {
        target: '#modal-container',
        swap: 'innerHTML'
    }).then(() => {
        showModal('scanModal');
    });
}

// Scheduler functions for backward compatibility
window.scheduler = {
    showScheduleModal: function() {
        console.log('Schedule modal - TODO: Implement with HTMX');
        showToast('Funzionalità in sviluppo', 'info');
    },
    showBulkScheduleModal: function() {
        console.log('Bulk schedule modal - TODO: Implement with HTMX');
        showToast('Funzionalità in sviluppo', 'info');
    },
    refreshData: function() {
        window.location.reload();
    }
};

// App object for backward compatibility with existing templates
window.app = {
    // Modal functions
    showAddClientModal: function() { showAddClientModal(); },
    showAddWebsiteModal: function() { showAddWebsiteModal(); },
    showNewScanModal: function() { showAddScanModal(); },
    
    // Scan actions
    cancelScan: function(scanId) {
        if (confirm('Sei sicuro di voler annullare questa scansione?')) {
            fetch(`/api/v1/scans/${scanId}/cancel`, { method: 'POST' })
                .then(() => window.location.reload())
                .catch(err => showToast('Errore nell\'annullamento della scansione', 'error'));
        }
    },
    retryScan: function(scanId) {
        fetch(`/api/v1/scans/${scanId}/retry`, { method: 'POST' })
            .then(() => window.location.reload())
            .catch(err => showToast('Errore nel riavvio della scansione', 'error'));
    },
    deleteScan: function(scanId) {
        if (confirm('Sei sicuro di voler eliminare questa scansione?')) {
            fetch(`/api/v1/scans/${scanId}`, { method: 'DELETE' })
                .then(() => window.location.reload())
                .catch(err => showToast('Errore nell\'eliminazione della scansione', 'error'));
        }
    },
    
    // Filter/navigation functions
    clearScansFilters: function() { window.location.reload(); },
    clearClientsFilters: function() { window.location.reload(); },
    showSection: function(section) { 
        window.location.href = `/templated/${section}`;
    },
    viewAllReports: function() {
        showToast('Funzionalità in sviluppo', 'info');
    },
    showWorkerStats: function() {
        showToast('Funzionalità in sviluppo', 'info');
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    
    // Success message for development
    setTimeout(() => {
        console.log('✅ HTMX Application Ready');
    }, 500);
});

// Update timestamp functionality
function updateTimestamp() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('it-IT', { 
        hour: '2-digit', 
        minute: '2-digit'
    });
    const element = document.getElementById('last-update');
    if (element) {
        element.textContent = timeString;
    }
}

// Auto-update timestamp every minute
setInterval(updateTimestamp, 60000);
updateTimestamp(); // Initial call