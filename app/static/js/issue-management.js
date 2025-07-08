/**
 * Issue Management JavaScript Module
 * Handles CRUD operations for the Issue Registry Management page
 */

const IssueManagement = {
    
    // Current issue being viewed/edited
    currentIssue: null,
    
    // API endpoints
    endpoints: {
        getIssue: (issueType) => `/api/v1/issue-registry/${issueType}`,
        updateIssue: (issueType) => `/api/v1/issue-registry/${issueType}`,
        createIssue: '/api/v1/issue-registry/',
        deleteIssue: (issueType) => `/api/v1/issue-registry/${issueType}`,
        getAllIssues: '/api/v1/issue-registry/',
        getStats: '/api/v1/issue-registry/stats/summary'
    },
    
    // Issue being deleted
    issueToDelete: null,
    
    /**
     * Initialize the issue management functionality
     */
    init() {
        this.bindEvents();
        this.initializeCollapsibles();
        console.log('Issue Management module initialized');
    },
    
    /**
     * Bind event listeners
     */
    bindEvents() {
        // Edit from view modal
        document.getElementById('editIssueFromView')?.addEventListener('click', () => {
            if (this.currentIssue) {
                this.hideViewModal();
                setTimeout(() => this.showEditModal(this.currentIssue.issue_type), 300);
            }
        });
        
        // Form submissions
        document.getElementById('issueEditForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSaveIssue();
        });
        
        document.getElementById('issueCreateForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCreateIssue();
        });
        
        // Escalation collapse toggle
        document.getElementById('escalationCollapse')?.addEventListener('shown.bs.collapse', () => {
            document.getElementById('escalationChevron').className = 'bi bi-chevron-down me-2';
        });
        
        document.getElementById('escalationCollapse')?.addEventListener('hidden.bs.collapse', () => {
            document.getElementById('escalationChevron').className = 'bi bi-chevron-right me-2';
        });
        
        // Create modal events
        document.getElementById('createIssueName')?.addEventListener('keyup', () => {
            this.updateCreateIconPreview();
        });
        
        document.getElementById('createEscalationCollapse')?.addEventListener('shown.bs.collapse', () => {
            document.getElementById('createEscalationChevron').className = 'bi bi-chevron-down me-2';
        });
        
        document.getElementById('createEscalationCollapse')?.addEventListener('hidden.bs.collapse', () => {
            document.getElementById('createEscalationChevron').className = 'bi bi-chevron-right me-2';
        });
    },
    
    /**
     * Initialize collapsible sections
     */
    initializeCollapsibles() {
        // All categories start collapsed except first
        const categories = document.querySelectorAll('.category-section');
        categories.forEach((category, index) => {
            const categoryId = category.getAttribute('data-category');
            if (index === 0) {
                // First category open by default
                const content = document.getElementById(`content-${categoryId}`);
                const chevron = document.getElementById(`chevron-${categoryId}`);
                if (content) content.style.display = 'block';
                if (chevron) chevron.className = 'bi bi-chevron-down';
            }
        });
    },
    
    /**
     * Show issue details in view modal
     */
    async showViewModal(issueType) {
        const modal = new bootstrap.Modal(document.getElementById('issueViewModal'));
        
        // Show loading state
        this.showViewLoading();
        modal.show();
        
        try {
            const response = await fetch(this.endpoints.getIssue(issueType));
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const issue = await response.json();
            this.currentIssue = issue;
            
            // Populate view modal
            this.populateViewModal(issue);
            this.showViewContent();
            
        } catch (error) {
            console.error('Error loading issue details:', error);
            this.showViewError(error.message);
        }
    },
    
    /**
     * Show issue edit modal
     */
    async showEditModal(issueType) {
        const modal = new bootstrap.Modal(document.getElementById('issueEditModal'));
        
        // Show loading state
        this.showEditLoading();
        modal.show();
        
        try {
            const response = await fetch(this.endpoints.getIssue(issueType));
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const issue = await response.json();
            this.currentIssue = issue;
            
            // Populate edit modal
            this.populateEditModal(issue);
            this.showEditContent();
            
        } catch (error) {
            console.error('Error loading issue details:', error);
            this.showEditError(error.message);
        }
    },
    
    /**
     * Populate view modal with issue data
     */
    populateViewModal(issue) {
        document.getElementById('viewIssueType').textContent = issue.issue_type;
        document.getElementById('viewIssueName').textContent = issue.name_it;
        document.getElementById('viewIssueDescription').textContent = issue.description_it;
        
        // Category badge
        const categoryBadge = document.getElementById('viewIssueCategory');
        categoryBadge.textContent = issue.category.replace('_', ' ').toUpperCase();
        categoryBadge.className = `badge bg-${this.getCategoryColor(issue.category)}`;
        
        // Severity badge
        const severityBadge = document.getElementById('viewIssueSeverity');
        severityBadge.textContent = issue.severity.toUpperCase();
        severityBadge.className = `badge bg-${this.getSeverityColor(issue.severity)}`;
        
        // Format badge
        const formatBadge = document.getElementById('viewIssueFormat');
        formatBadge.textContent = issue.format_type.toUpperCase();
        formatBadge.className = `badge bg-${issue.format_type === 'granular' ? 'success' : 'secondary'}`;
        
        // Icon
        const iconElement = document.querySelector('#viewIssueIcon i');
        const iconNameElement = document.getElementById('viewIssueIconName');
        iconElement.className = `bi ${issue.icon} me-2`;
        iconNameElement.textContent = issue.icon;
        
        // Recommendations
        this.populateRecommendations(issue.recommendations);
        
        // Escalation rules
        if (issue.escalation_rules && typeof issue.escalation_rules === 'object' && Object.keys(issue.escalation_rules).length > 0) {
            document.getElementById('viewEscalationSection').style.display = 'block';
            document.getElementById('viewEscalationRules').textContent = JSON.stringify(issue.escalation_rules, null, 2);
        } else {
            document.getElementById('viewEscalationSection').style.display = 'none';
        }
    },
    
    /**
     * Populate edit modal with issue data
     */
    populateEditModal(issue) {
        document.getElementById('editIssueType').value = issue.issue_type;
        document.getElementById('editIssueTypeDisplay').value = issue.issue_type;
        document.getElementById('editIssueName').value = issue.name_it;
        document.getElementById('editIssueDescription').value = issue.description_it;
        document.getElementById('editIssueCategory').value = issue.category;
        document.getElementById('editIssueSeverity').value = issue.severity;
        document.getElementById('editIssueFormat').value = issue.format_type;
        document.getElementById('editIssueIcon').value = issue.icon;
        
        // Update icon preview
        this.updateIconPreview();
        
        // Populate recommendations
        this.populateEditRecommendations(issue.recommendations);
        
        // Escalation rules
        if (issue.escalation_rules && typeof issue.escalation_rules === 'object' && Object.keys(issue.escalation_rules).length > 0) {
            document.getElementById('editEscalationRules').value = JSON.stringify(issue.escalation_rules, null, 2);
        } else {
            document.getElementById('editEscalationRules').value = '';
        }
    },
    
    /**
     * Populate recommendations list in view modal
     */
    populateRecommendations(recommendations) {
        const container = document.getElementById('viewIssueRecommendations');
        const countElement = document.getElementById('viewRecommendationsCount');
        
        countElement.textContent = recommendations.length;
        container.innerHTML = '';
        
        if (recommendations.length === 0) {
            container.innerHTML = '<li class="list-group-item text-muted">Nessuna raccomandazione definita</li>';
            return;
        }
        
        recommendations.forEach((rec, index) => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.innerHTML = `
                <div class="d-flex align-items-start">
                    <span class="badge bg-primary me-2">${index + 1}</span>
                    <span>${rec}</span>
                </div>
            `;
            container.appendChild(li);
        });
    },
    
    /**
     * Populate recommendations in edit modal
     */
    populateEditRecommendations(recommendations) {
        const container = document.getElementById('recommendationsContainer');
        container.innerHTML = '';
        
        recommendations.forEach((rec, index) => {
            this.addRecommendationField(rec, index);
        });
        
        // Add one empty field if no recommendations
        if (recommendations.length === 0) {
            this.addRecommendationField('', 0);
        }
    },
    
    /**
     * Add recommendation input field
     */
    addRecommendationField(value = '', index = null) {
        const container = document.getElementById('recommendationsContainer');
        const fieldIndex = index !== null ? index : container.children.length;
        
        const div = document.createElement('div');
        div.className = 'input-group mb-2';
        div.innerHTML = `
            <span class="input-group-text">${fieldIndex + 1}</span>
            <input type="text" class="form-control" name="recommendations[]" 
                   value="${value}" placeholder="Raccomandazione...">
            <button type="button" class="btn btn-outline-danger" onclick="IssueManagement.removeRecommendation(this)">
                <i class="bi bi-trash"></i>
            </button>
        `;
        
        container.appendChild(div);
    },
    
    /**
     * Add recommendation field in create modal
     */
    addCreateRecommendationField() {
        const container = document.getElementById('createRecommendationsContainer');
        const fieldIndex = container.children.length;
        
        const div = document.createElement('div');
        div.className = 'input-group mb-2';
        div.innerHTML = `
            <span class="input-group-text">${fieldIndex + 1}</span>
            <input type="text" class="form-control" name="recommendations[]" 
                   placeholder="Raccomandazione...">
            <button type="button" class="btn btn-outline-danger" onclick="IssueManagement.removeCreateRecommendation(this)">
                <i class="bi bi-trash"></i>
            </button>
        `;
        
        container.appendChild(div);
    },
    
    /**
     * Remove recommendation field in create modal
     */
    removeCreateRecommendation(button) {
        const container = document.getElementById('createRecommendationsContainer');
        button.closest('.input-group').remove();
        
        // Update numbering
        const fields = container.querySelectorAll('.input-group');
        fields.forEach((field, index) => {
            field.querySelector('.input-group-text').textContent = index + 1;
        });
        
        // Ensure at least one field
        if (fields.length === 0) {
            this.addCreateRecommendationField();
        }
    },
    
    /**
     * Update icon preview in create modal
     */
    updateCreateIconPreview() {
        const iconInput = document.getElementById('createIssueIcon');
        const iconPreview = document.getElementById('createIssueIconPreview');
        const iconLarge = document.getElementById('createIssueIconLarge');
        
        if (iconInput && iconPreview && iconLarge) {
            const iconClass = iconInput.value || 'bi-exclamation-triangle';
            iconPreview.className = `bi ${iconClass}`;
            iconLarge.className = `bi ${iconClass} me-2`;
        }
        
        // Update name preview
        const nameInput = document.getElementById('createIssueName');
        const namePreview = document.getElementById('createIssueNamePreview');
        if (nameInput && namePreview) {
            namePreview.textContent = nameInput.value || 'Nome Issue';
        }
    },
    
    /**
     * Remove recommendation field
     */
    removeRecommendation(button) {
        const container = document.getElementById('recommendationsContainer');
        button.closest('.input-group').remove();
        
        // Update numbering
        const fields = container.querySelectorAll('.input-group');
        fields.forEach((field, index) => {
            field.querySelector('.input-group-text').textContent = index + 1;
        });
        
        // Ensure at least one field
        if (fields.length === 0) {
            this.addRecommendationField('', 0);
        }
    },
    
    /**
     * Update icon preview in edit modal
     */
    updateIconPreview() {
        const iconInput = document.getElementById('editIssueIcon');
        const iconPreview = document.getElementById('editIssueIconPreview');
        
        if (iconInput && iconPreview) {
            const iconClass = iconInput.value || 'bi-question-circle';
            iconPreview.className = `bi ${iconClass}`;
        }
    },
    
    /**
     * Show create new issue modal
     */
    showCreateModal() {
        const modal = new bootstrap.Modal(document.getElementById('issueCreateModal'));
        
        // Reset form
        document.getElementById('issueCreateForm').reset();
        document.getElementById('createIssueFormat').value = 'granular';
        document.getElementById('createIssueIcon').value = 'bi-exclamation-triangle';
        this.updateCreateIconPreview();
        
        // Reset recommendations
        const container = document.getElementById('createRecommendationsContainer');
        container.innerHTML = `
            <div class="input-group mb-2">
                <span class="input-group-text">1</span>
                <input type="text" class="form-control" name="recommendations[]" 
                       placeholder="Prima raccomandazione...">
                <button type="button" class="btn btn-outline-danger" onclick="IssueManagement.removeCreateRecommendation(this)">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        
        modal.show();
    },
    
    /**
     * Show delete confirmation modal
     */
    async showDeleteModal(issueType) {
        const modal = new bootstrap.Modal(document.getElementById('issueDeleteModal'));
        
        try {
            const response = await fetch(this.endpoints.getIssue(issueType));
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const issue = await response.json();
            this.issueToDelete = issue;
            
            // Populate delete confirmation
            this.populateDeleteModal(issue);
            
            // Reset confirmation checkbox
            document.getElementById('confirmDeletion').checked = false;
            
            modal.show();
            
        } catch (error) {
            console.error('Error loading issue for deletion:', error);
            alert('Errore nel caricamento dei dettagli issue: ' + error.message);
        }
    },
    
    /**
     * Populate delete modal with issue data
     */
    populateDeleteModal(issue) {
        document.getElementById('deleteIssueName').textContent = issue.name_it;
        document.getElementById('deleteIssueType').textContent = issue.issue_type;
        
        // Icon
        const iconElement = document.getElementById('deleteIssueIcon');
        iconElement.className = `bi ${issue.icon} me-3 text-muted`;
        
        // Category badge
        const categoryBadge = document.getElementById('deleteIssueCategory');
        categoryBadge.textContent = issue.category.replace('_', ' ').toUpperCase();
        categoryBadge.className = `badge bg-${this.getCategoryColor(issue.category)}`;
        
        // Severity badge
        const severityBadge = document.getElementById('deleteIssueSeverity');
        severityBadge.textContent = issue.severity.toUpperCase();
        severityBadge.className = `badge bg-${this.getSeverityColor(issue.severity)}`;
    },
    
    /**
     * Handle create issue form submission
     */
    async handleCreateIssue() {
        const form = document.getElementById('issueCreateForm');
        const formData = new FormData(form);
        
        // Validate issue type uniqueness
        const issueType = formData.get('issue_type');
        if (!issueType || !issueType.match(/^[a-z_]+$/)) {
            alert('Il tipo issue deve contenere solo lettere minuscole e underscore');
            return;
        }
        
        // Collect recommendations
        const recommendations = Array.from(form.querySelectorAll('input[name="recommendations[]"]'))
            .map(input => input.value.trim())
            .filter(value => value.length > 0);
        
        // Parse escalation rules
        let escalationRules = null;
        const escalationText = document.getElementById('createEscalationRules').value.trim();
        if (escalationText) {
            try {
                escalationRules = JSON.parse(escalationText);
            } catch (error) {
                alert('Errore: Le regole di escalation devono essere in formato JSON valido');
                return;
            }
        }
        
        // Build create data
        const createData = {
            issue_type: issueType,
            name_it: formData.get('name_it'),
            description_it: formData.get('description_it'),
            category: formData.get('category'),
            severity: formData.get('severity'),
            format_type: formData.get('format_type'),
            icon: formData.get('icon') || 'bi-exclamation-triangle',
            recommendations: recommendations,
            escalation_rules: escalationRules
        };
        
        const createBtn = document.getElementById('createIssueBtn');
        createBtn.disabled = true;
        createBtn.innerHTML = '<i class="bi bi-spinner-border me-2"></i>Creando...';
        
        try {
            // NOTE: Since the registry is currently static, we simulate the creation
            console.log('Create data:', createData);
            
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Show success message
            this.showSuccessMessage(`Issue "${createData.name_it}" creata con successo!`);
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('issueCreateModal')).hide();
            
            // Optionally refresh the page
            // window.location.reload();
            
        } catch (error) {
            console.error('Error creating issue:', error);
            alert('Errore nella creazione: ' + error.message);
        } finally {
            createBtn.disabled = false;
            createBtn.innerHTML = '<i class="bi bi-plus-circle me-2"></i>Crea Issue';
        }
    },
    
    /**
     * Confirm and execute issue deletion
     */
    async confirmDelete() {
        const confirmCheckbox = document.getElementById('confirmDeletion');
        if (!confirmCheckbox.checked) {
            alert('Devi confermare la cancellazione spuntando la casella');
            return;
        }
        
        if (!this.issueToDelete) {
            alert('Errore: Nessuna issue selezionata per l\'eliminazione');
            return;
        }
        
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<i class="bi bi-spinner-border me-2"></i>Eliminando...';
        
        // Show loading state
        document.getElementById('issueDeleteContent').style.display = 'none';
        document.getElementById('issueDeleteLoading').style.display = 'block';
        
        try {
            // NOTE: Since the registry is currently static, we simulate the deletion
            console.log('Deleting issue:', this.issueToDelete.issue_type);
            
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // Show success message
            this.showSuccessMessage(`Issue "${this.issueToDelete.name_it}" eliminata con successo!`);
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('issueDeleteModal')).hide();
            
            // Optionally refresh the page
            // window.location.reload();
            
        } catch (error) {
            console.error('Error deleting issue:', error);
            document.getElementById('issueDeleteContent').style.display = 'block';
            document.getElementById('issueDeleteLoading').style.display = 'none';
            document.getElementById('issueDeleteError').style.display = 'block';
            document.getElementById('issueDeleteErrorMessage').textContent = error.message;
        } finally {
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = '<i class="bi bi-trash me-2"></i>Elimina Issue';
            this.issueToDelete = null;
        }
    },
    
    /**
     * Handle save issue form submission
     */
    async handleSaveIssue() {
        const form = document.getElementById('issueEditForm');
        const formData = new FormData(form);
        
        // Collect recommendations
        const recommendations = Array.from(form.querySelectorAll('input[name="recommendations[]"]'))
            .map(input => input.value.trim())
            .filter(value => value.length > 0);
        
        // Parse escalation rules
        let escalationRules = {};
        const escalationText = document.getElementById('editEscalationRules').value.trim();
        if (escalationText) {
            try {
                escalationRules = JSON.parse(escalationText);
            } catch (error) {
                alert('Errore: Le regole di escalation devono essere in formato JSON valido');
                return;
            }
        }
        
        // Build update data
        const updateData = {
            name_it: formData.get('name_it'),
            description_it: formData.get('description_it'),
            category: formData.get('category'),
            severity: formData.get('severity'),
            format_type: formData.get('format_type'),
            icon: formData.get('icon'),
            recommendations: recommendations,
            escalation_rules: escalationRules
        };
        
        const saveBtn = document.getElementById('saveIssueBtn');
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="bi bi-spinner-border me-2"></i>Salvando...';
        
        try {
            // NOTE: Since the registry is currently static, we simulate the save
            // In a real implementation, this would send a PUT request to update the issue
            console.log('Update data:', updateData);
            
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Show success message
            this.showSuccessMessage('Issue aggiornata con successo!');
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('issueEditModal')).hide();
            
            // Optionally refresh the page data
            // window.location.reload();
            
        } catch (error) {
            console.error('Error saving issue:', error);
            alert('Errore nel salvataggio: ' + error.message);
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Salva Modifiche';
        }
    },
    
    /**
     * Show success message
     */
    showSuccessMessage(message) {
        // Create and show a toast notification
        const toast = document.createElement('div');
        toast.className = 'toast position-fixed top-0 end-0 m-3';
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            <div class="toast-header bg-success text-white">
                <i class="bi bi-check-circle me-2"></i>
                <strong class="me-auto">Successo</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },
    
    /**
     * Show/hide modal states
     */
    showViewLoading() {
        document.getElementById('issueViewLoading').style.display = 'block';
        document.getElementById('issueViewContent').style.display = 'none';
        document.getElementById('issueViewError').style.display = 'none';
    },
    
    showViewContent() {
        document.getElementById('issueViewLoading').style.display = 'none';
        document.getElementById('issueViewContent').style.display = 'block';
        document.getElementById('issueViewError').style.display = 'none';
    },
    
    showViewError(message) {
        document.getElementById('issueViewLoading').style.display = 'none';
        document.getElementById('issueViewContent').style.display = 'none';
        document.getElementById('issueViewError').style.display = 'block';
        document.getElementById('issueViewErrorMessage').textContent = message;
    },
    
    showEditLoading() {
        document.getElementById('issueEditLoading').style.display = 'block';
        document.getElementById('issueEditContent').style.display = 'none';
        document.getElementById('issueEditError').style.display = 'none';
    },
    
    showEditContent() {
        document.getElementById('issueEditLoading').style.display = 'none';
        document.getElementById('issueEditContent').style.display = 'block';
        document.getElementById('issueEditError').style.display = 'none';
    },
    
    showEditError(message) {
        document.getElementById('issueEditLoading').style.display = 'none';
        document.getElementById('issueEditContent').style.display = 'none';
        document.getElementById('issueEditError').style.display = 'block';
        document.getElementById('issueEditErrorMessage').textContent = message;
    },
    
    hideViewModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('issueViewModal'));
        if (modal) modal.hide();
    },
    
    /**
     * Utility functions
     */
    getCategoryColor(category) {
        const colors = {
            'technical_seo': 'primary',
            'on_page': 'info',
            'content': 'success',
            'accessibility': 'warning',
            'performance': 'danger',
            'mobile': 'secondary',
            'social': 'light',
            'security': 'dark'
        };
        return colors[category] || 'secondary';
    },
    
    getSeverityColor(severity) {
        const colors = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'secondary'
        };
        return colors[severity] || 'secondary';
    }
};

// Global functions for onclick handlers
window.viewIssue = (issueType) => IssueManagement.showViewModal(issueType);
window.editIssue = (issueType) => IssueManagement.showEditModal(issueType);
window.deleteIssue = (issueType) => IssueManagement.showDeleteModal(issueType);
window.addRecommendation = () => IssueManagement.addRecommendationField();
window.addCreateRecommendation = () => IssueManagement.addCreateRecommendationField();
window.updateIconPreview = () => IssueManagement.updateIconPreview();
window.updateCreateIconPreview = () => IssueManagement.updateCreateIconPreview();
window.showAddIssueModal = () => IssueManagement.showCreateModal();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    IssueManagement.init();
});