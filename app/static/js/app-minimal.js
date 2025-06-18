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

// Simple namespace objects for modal compatibility
const clients = {
    createClient: function() {
        const form = document.getElementById('addClientForm');
        if (form) {
            const formData = new FormData(form);
            const data = {
                name: formData.get('clientName'),
                contact_email: formData.get('clientEmail'),
                contact_phone: formData.get('clientPhone') || null,
                notes: formData.get('clientNotes') || null
            };
            
            fetch('/api/v1/clients/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result) {
                    showToast('Cliente creato con successo', 'success');
                    closeModal('addClientModal');
                    window.location.reload();
                } else {
                    showToast('Errore nella creazione del cliente', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Errore nella comunicazione con il server', 'error');
            });
        }
    },
    
    updateClient: function() {
        const form = document.getElementById('editClientForm');
        const clientId = document.getElementById('editClientId').value;
        
        if (form && clientId) {
            const formData = new FormData(form);
            const data = {
                name: formData.get('editClientName'),
                contact_email: formData.get('editClientEmail'),
                contact_phone: formData.get('editClientPhone') || null,
                notes: formData.get('editClientNotes') || null
            };
            
            fetch(`/api/v1/clients/${clientId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result) {
                    showToast('Cliente aggiornato con successo', 'success');
                    closeModal('editClientModal');
                    window.location.reload();
                } else {
                    showToast('Errore nell\'aggiornamento del cliente', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Errore nella comunicazione con il server', 'error');
            });
        }
    },
    
    deleteClientFromModal: function() {
        const clientId = document.getElementById('editClientId').value;
        if (clientId && confirm('Sei sicuro di voler eliminare questo cliente?')) {
            fetch(`/api/v1/clients/${clientId}`, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    showToast('Cliente eliminato con successo', 'success');
                    closeModal('editClientModal');
                    window.location.reload();
                } else {
                    showToast('Errore nell\'eliminazione del cliente', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Errore nella comunicazione con il server', 'error');
            });
        }
    }
};

const websites = {
    createWebsite: function() {
        const form = document.getElementById('addWebsiteForm');
        if (form) {
            const formData = new FormData(form);
            const data = {
                name: formData.get('websiteName'),
                domain: formData.get('websiteUrl'),
                client_id: parseInt(formData.get('websiteClient')),
                description: formData.get('websiteDescription') || null,
                is_active: formData.get('websiteActive') === 'on'
            };
            
            fetch('/api/v1/websites/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result) {
                    showToast('Sito web creato con successo', 'success');
                    closeModal('addWebsiteModal');
                    window.location.reload();
                } else {
                    showToast('Errore nella creazione del sito web', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Errore nella comunicazione con il server', 'error');
            });
        }
    },
    
    updateWebsite: function() {
        const form = document.getElementById('editWebsiteForm');
        const websiteId = document.getElementById('editWebsiteId').value;
        
        if (form && websiteId) {
            const formData = new FormData(form);
            const data = {
                name: formData.get('editWebsiteName'),
                domain: formData.get('editWebsiteUrl'),
                client_id: parseInt(formData.get('editWebsiteClient')),
                description: formData.get('editWebsiteDescription') || null,
                is_active: formData.get('editWebsiteActive') === 'on'
            };
            
            fetch(`/api/v1/websites/${websiteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result) {
                    showToast('Sito web aggiornato con successo', 'success');
                    closeModal('editWebsiteModal');
                    window.location.reload();
                } else {
                    showToast('Errore nell\'aggiornamento del sito web', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Errore nella comunicazione con il server', 'error');
            });
        }
    },
    
    deleteWebsiteFromModal: function() {
        const websiteId = document.getElementById('editWebsiteId').value;
        if (websiteId && confirm('Sei sicuro di voler eliminare questo sito web?')) {
            fetch(`/api/v1/websites/${websiteId}`, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    showToast('Sito web eliminato con successo', 'success');
                    closeModal('editWebsiteModal');
                    window.location.reload();
                } else {
                    showToast('Errore nell\'eliminazione del sito web', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Errore nella comunicazione con il server', 'error');
            });
        }
    }
};

const scans = {
    startNewScan: function() {
        const form = document.getElementById('newScanForm');
        if (form) {
            const formData = new FormData(form);
            const data = {
                website_id: parseInt(formData.get('scanWebsite')),
                scan_type: formData.get('scanType') || 'full',
                depth: parseInt(formData.get('scanDepth')) || 5,
                options: {
                    images: formData.get('scanImages') === 'on',
                    links: formData.get('scanLinks') === 'on',
                    performance: formData.get('scanPerformance') === 'on',
                    mobile: formData.get('scanMobile') === 'on'
                },
                notes: formData.get('scanNotes') || null
            };
            
            fetch('/api/v1/scans/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result) {
                    showToast('Scansione avviata con successo', 'success');
                    closeModal('newScanModal');
                    window.location.reload();
                } else {
                    showToast('Errore nell\'avvio della scansione', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Errore nella comunicazione con il server', 'error');
            });
        }
    }
};

const scheduler = {
    createSchedule: function() {
        const form = document.getElementById('newScheduleForm');
        if (form) {
            const formData = new FormData(form);
            const data = {
                website_id: parseInt(formData.get('scheduleWebsite')),
                frequency: formData.get('scheduleFrequency'),
                time: formData.get('scheduleTime'),
                day: formData.get('scheduleDay') ? parseInt(formData.get('scheduleDay')) : null,
                scan_type: formData.get('scheduleScanType') || 'full',
                email_notify: formData.get('scheduleEmailNotify') === 'on',
                alert_issues: formData.get('scheduleAlertIssues') === 'on',
                is_active: formData.get('scheduleActive') === 'on',
                notes: formData.get('scheduleNotes') || null
            };
            
            fetch('/api/v1/scheduler/schedules/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result) {
                    showToast('Programmazione creata con successo', 'success');
                    closeModal('newScheduleModal');
                    window.location.reload();
                } else {
                    showToast('Errore nella creazione della programmazione', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Errore nella comunicazione con il server', 'error');
            });
        }
    }
};

// Global functions for easy access
function showAddClientModal() { showModal('addClientModal'); }
function showAddWebsiteModal() { showModal('addWebsiteModal'); }
function showNewScanModal() { showModal('newScanModal'); }
function showScheduleModal() { showModal('newScheduleModal'); }

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
    
    // Client management
    editClient: function(clientId) {
        fetch(`/api/v1/clients/${clientId}`)
            .then(response => response.json())
            .then(client => {
                // Populate edit modal with client data
                const editModal = document.getElementById('editClientModal');
                if (editModal) {
                    document.getElementById('editClientId').value = client.id;
                    document.getElementById('editClientName').value = client.name;
                    document.getElementById('editClientEmail').value = client.contact_email;
                    document.getElementById('editClientPhone').value = client.contact_phone || '';
                    document.getElementById('editClientNotes').value = client.notes || '';
                    showModal('editClientModal');
                } else {
                    showToast('Modal di modifica non trovato', 'error');
                }
            })
            .catch(err => showToast('Errore nel caricamento del cliente', 'error'));
    },
    deleteClient: function(clientId) {
        if (confirm('Sei sicuro di voler eliminare questo cliente?')) {
            fetch(`/api/v1/clients/${clientId}`, { method: 'DELETE' })
                .then(() => {
                    showToast('Cliente eliminato con successo', 'success');
                    window.location.reload();
                })
                .catch(err => showToast('Errore nell\'eliminazione del cliente', 'error'));
        }
    },
    
    // Website management
    editWebsite: function(websiteId) {
        fetch(`/api/v1/websites/${websiteId}`)
            .then(response => response.json())
            .then(website => {
                // Populate edit modal with website data
                const editModal = document.getElementById('editWebsiteModal');
                if (editModal) {
                    document.getElementById('editWebsiteId').value = website.id;
                    document.getElementById('editWebsiteName').value = website.name;
                    document.getElementById('editWebsiteUrl').value = website.domain;
                    document.getElementById('editWebsiteClient').value = website.client_id;
                    document.getElementById('editWebsiteDescription').value = website.description || '';
                    document.getElementById('editWebsiteActive').checked = website.is_active;
                    showModal('editWebsiteModal');
                } else {
                    showToast('Modal di modifica non trovato', 'error');
                }
            })
            .catch(err => showToast('Errore nel caricamento del sito web', 'error'));
    },
    deleteWebsite: function(websiteId) {
        if (confirm('Sei sicuro di voler eliminare questo sito web?')) {
            fetch(`/api/v1/websites/${websiteId}`, { method: 'DELETE' })
                .then(() => {
                    showToast('Sito web eliminato con successo', 'success');
                    window.location.reload();
                })
                .catch(err => showToast('Errore nell\'eliminazione del sito web', 'error'));
        }
    },
    startScanForWebsite: function(websiteId) {
        const data = {
            website_id: websiteId,
            scan_type: 'full',
            depth: 5,
            options: {
                images: true,
                links: true,
                performance: true,
                mobile: false
            }
        };
        
        fetch('/api/v1/scans/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result) {
                showToast('Scansione avviata con successo', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showToast('Errore nell\'avvio della scansione', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Errore nella comunicazione con il server', 'error');
        });
    },
    
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
    
    // Scheduler management
    editSchedule: function(scheduleId) {
        fetch(`/api/v1/scheduler/schedules/${scheduleId}`)
            .then(response => response.json())
            .then(schedule => {
                // Populate edit modal with schedule data
                const editModal = document.getElementById('editScheduleModal');
                if (editModal) {
                    document.getElementById('editScheduleId').value = schedule.id;
                    document.getElementById('editScheduleWebsite').value = schedule.website_id;
                    document.getElementById('editScheduleFrequency').value = schedule.frequency;
                    document.getElementById('editScheduleTime').value = schedule.time;
                    document.getElementById('editScheduleDay').value = schedule.day || '';
                    document.getElementById('editScheduleScanType').value = schedule.scan_type;
                    document.getElementById('editScheduleEmailNotify').checked = schedule.email_notify;
                    document.getElementById('editScheduleAlertIssues').checked = schedule.alert_issues;
                    document.getElementById('editScheduleActive').checked = schedule.is_active;
                    document.getElementById('editScheduleNotes').value = schedule.notes || '';
                    showModal('editScheduleModal');
                } else {
                    showToast('Modal di modifica non trovato', 'error');
                }
            })
            .catch(err => showToast('Errore nel caricamento della programmazione', 'error'));
    },
    pauseSchedule: function(scheduleId) {
        fetch(`/api/v1/scheduler/schedules/${scheduleId}/pause`, { method: 'POST' })
            .then(response => {
                if (response.ok) {
                    showToast('Programmazione messa in pausa', 'success');
                    window.location.reload();
                } else {
                    showToast('Errore nella pausa della programmazione', 'error');
                }
            })
            .catch(err => showToast('Errore nella comunicazione con il server', 'error'));
    },
    deleteSchedule: function(scheduleId) {
        if (confirm('Sei sicuro di voler eliminare questa programmazione?')) {
            fetch(`/api/v1/scheduler/schedules/${scheduleId}`, { method: 'DELETE' })
                .then(response => {
                    if (response.ok) {
                        showToast('Programmazione eliminata con successo', 'success');
                        window.location.reload();
                    } else {
                        showToast('Errore nell\'eliminazione della programmazione', 'error');
                    }
                })
                .catch(err => showToast('Errore nella comunicazione con il server', 'error'));
        }
    },
    pauseAllSchedules: function() {
        if (confirm('Sei sicuro di voler mettere in pausa tutte le programmazioni?')) {
            fetch(`/api/v1/scheduler/actions/pause`, { method: 'POST' })
                .then(response => {
                    if (response.ok) {
                        showToast('Tutte le programmazioni sono state messe in pausa', 'success');
                        window.location.reload();
                    } else {
                        showToast('Errore nella pausa delle programmazioni', 'error');
                    }
                })
                .catch(err => showToast('Errore nella comunicazione con il server', 'error'));
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