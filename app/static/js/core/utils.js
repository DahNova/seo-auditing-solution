// SEO Auditing Solution - Utility Functions

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Format date functions
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatRelativeTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'ora';
    if (diffInMinutes < 60) return `${diffInMinutes} min fa`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} ore fa`;
    return `${Math.floor(diffInMinutes / 1440)} giorni fa`;
}

// Status badge helpers
function getStatusBadge(status) {
    const statusMap = {
        'running': { class: 'bg-info', text: 'In Corso', icon: 'clock' },
        'completed': { class: 'bg-success', text: 'Completata', icon: 'check-circle' },
        'failed': { class: 'bg-danger', text: 'Fallita', icon: 'x-circle' },
        'cancelled': { class: 'bg-secondary', text: 'Annullata', icon: 'slash-circle' },
        'pending': { class: 'bg-warning', text: 'In Attesa', icon: 'clock-history' },
        'active': { class: 'bg-success', text: 'Attivo', icon: 'check-circle' },
        'inactive': { class: 'bg-secondary', text: 'Inattivo', icon: 'dash-circle' }
    };
    
    const config = statusMap[status] || { class: 'bg-secondary', text: status, icon: 'question' };
    return `<span class="badge ${config.class}">
        <i class="bi bi-${config.icon}"></i> ${config.text}
    </span>`;
}

// SEO Score helpers
function getSEOScoreClass(score) {
    if (score >= 90) return 'excellent';
    if (score >= 70) return 'good';
    if (score >= 50) return 'fair';
    return 'poor';
}

function getSEOScoreBadge(score) {
    if (!score && score !== 0) return '<span class="badge bg-secondary">N/A</span>';
    
    const scoreClass = getSEOScoreClass(score);
    const colorMap = {
        'excellent': 'success',
        'good': 'info', 
        'fair': 'warning',
        'poor': 'danger'
    };
    
    return `<span class="badge bg-${colorMap[scoreClass]} seo-score ${scoreClass}">${score}/100</span>`;
}

// Loading states
function showLoading(elementId, message = 'Caricamento...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">${message}</span>
                </div>
                <p class="mt-2 text-muted">${message}</p>
            </div>
        `;
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

// Toast notifications
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const iconMap = {
        'success': 'check-circle',
        'error': 'x-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-${iconMap[type]}"></i> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, { delay: duration });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// Form validation
function validateForm(formId, rules) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    const errors = {};
    
    Object.keys(rules).forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"], #${fieldName}`);
        const rule = rules[fieldName];
        
        if (!field) return;
        
        // Clear previous errors
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) errorDiv.remove();
        
        // Validate required
        if (rule.required && !field.value.trim()) {
            errors[fieldName] = rule.requiredMessage || 'Campo obbligatorio';
            isValid = false;
        }
        
        // Validate pattern
        if (field.value && rule.pattern && !rule.pattern.test(field.value)) {
            errors[fieldName] = rule.patternMessage || 'Formato non valido';
            isValid = false;
        }
        
        // Validate min length
        if (field.value && rule.minLength && field.value.length < rule.minLength) {
            errors[fieldName] = rule.minLengthMessage || `Minimo ${rule.minLength} caratteri`;
            isValid = false;
        }
        
        // Show error
        if (errors[fieldName]) {
            field.classList.add('is-invalid');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = errors[fieldName];
            field.parentNode.appendChild(errorDiv);
        }
    });
    
    return isValid;
}

// URL helpers
function isValidURL(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function sanitizeURL(url) {
    if (!url) return '';
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        return 'https://' + url;
    }
    return url;
}

// Number formatting
function formatNumber(num) {
    if (num === null || num === undefined) return '-';
    return new Intl.NumberFormat('it-IT').format(num);
}

// Download helpers
function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Modal helpers
function resetModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    // Reset all form fields
    const forms = modal.querySelectorAll('form');
    forms.forEach(form => form.reset());
    
    // Clear validation states
    const invalidFields = modal.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => field.classList.remove('is-invalid'));
    
    const errorDivs = modal.querySelectorAll('.invalid-feedback');
    errorDivs.forEach(div => div.remove());
}

// Export functions to global scope
window.utils = {
    debounce,
    formatDate,
    formatRelativeTime,
    getStatusBadge,
    getSEOScoreClass,
    getSEOScoreBadge,
    showLoading,
    hideLoading,
    showToast,
    validateForm,
    isValidURL,
    sanitizeURL,
    formatNumber,
    downloadBlob,
    resetModal
};