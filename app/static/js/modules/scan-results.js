// SEO Auditing Solution - Scan Results Module
class ScanResultsModule {
    constructor() {
        this.currentScan = null;
        this.currentIssues = [];
        this.currentPages = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Back to scans button
        const backBtn = document.getElementById('back-to-scans');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                window.app.showSection('scans');
            });
        }

        // Filter listeners for issues
        const issueFilter = document.getElementById('issue-filter');
        if (issueFilter) {
            issueFilter.addEventListener('change', () => {
                this.applyIssueFilters();
            });
        }

        const severityFilter = document.getElementById('severity-filter');
        if (severityFilter) {
            severityFilter.addEventListener('change', () => {
                this.applyIssueFilters();
            });
        }
    }

    async loadScanData(scanId) {
        try {
            appState.setLoading('scanResults', true);
            
            // Load scan details, issues, and pages
            const [scan, issues, pages] = await Promise.all([
                apiClient.getScan(scanId),
                apiClient.getScanIssues(scanId),
                apiClient.getScanPages(scanId)
            ]);


            this.currentScan = scan;
            this.currentIssues = issues;
            this.currentPages = pages;

            // Store current scan ID for downloads
            window.app.currentScanId = scanId;

            this.renderScanDetails();
            
            this.renderIssuesAccordion();
            
            
            this.renderPagesTable();


        } catch (error) {
            console.error('❌ Error loading scan data:', error);
            utils.showToast('Errore nel caricamento dei risultati', 'error');
        } finally {
            appState.setLoading('scanResults', false);
        }
    }

    renderScanDetails() {
        if (!this.currentScan) return;

        // Update scan header info  
        const elements = {
            'scan-website-name': this.currentScan.website?.domain || 'Sito sconosciuto',
            'scan-date': utils.formatDate(this.currentScan.created_at),
            'scan-status': this.getScanStatusBadge(this.currentScan.status),
            'scan-pages-count': this.currentScan.pages_found || this.currentScan.pages_scanned || 0,
            'scan-total-issues': this.currentScan.total_issues || 0,
            'scan-seo-score': this.currentScan.seo_score ? utils.getSEOScoreBadge(this.currentScan.seo_score) : '-'
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                if (id === 'scan-status' || id === 'scan-seo-score') {
                    element.innerHTML = value;
                } else {
                    element.textContent = value;
                }
            }
        });

        // Update progress info if available
        if (this.currentScan.scan_duration) {
            const durationElement = document.getElementById('scan-duration');
            if (durationElement) {
                durationElement.textContent = `${this.currentScan.scan_duration}s`;
            }
        }
    }

    getScanStatusBadge(status) {
        const statusMap = {
            'running': { class: 'bg-info', text: 'In Corso', icon: 'arrow-clockwise' },
            'completed': { class: 'bg-success', text: 'Completata', icon: 'check-circle' },
            'failed': { class: 'bg-danger', text: 'Fallita', icon: 'x-circle' },
            'cancelled': { class: 'bg-secondary', text: 'Annullata', icon: 'dash-circle' }
        };
        
        const config = statusMap[status] || { class: 'bg-secondary', text: status, icon: 'question' };
        return `<span class="badge ${config.class}">
            <i class="bi bi-${config.icon}"></i> ${config.text}
        </span>`;
    }

    renderIssuesAccordion() {
        if (!this.currentIssues || this.currentIssues.length === 0) {
            // Update all counters to 0
            ['critical-count', 'high-count', 'medium-count', 'low-count'].forEach(id => {
                const element = document.getElementById(id);
                if (element) element.textContent = '0';
            });
            return;
        }

        // Group issues by severity
        const groupedIssues = this.groupIssuesBySeverity(this.currentIssues);
        
        // Update counters for each severity level
        const severityMapping = {
            'critical': 'critical-count',
            'high': 'high-count', 
            'medium': 'medium-count',
            'low': 'low-count',
            'minor': 'low-count' // Map minor to low
        };

        // Reset all counters first
        Object.values(severityMapping).forEach(id => {
            const element = document.getElementById(id);
            if (element) element.textContent = '0';
        });

        // Update counters with actual data
        Object.entries(groupedIssues).forEach(([severity, issues]) => {
            const countElementId = severityMapping[severity];
            if (countElementId) {
                const element = document.getElementById(countElementId);
                if (element) element.textContent = issues.length.toString();
            }
        });

        // Populate the sub-accordions with actual issues
        this.populateSubAccordions(groupedIssues);
    }

    groupIssuesBySeverity(issues) {
        const grouped = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'minor': []
        };

        issues.forEach(issue => {
            const severity = issue.severity || 'medium';
            if (grouped[severity]) {
                grouped[severity].push(issue);
            }
        });

        // Remove empty groups
        Object.keys(grouped).forEach(key => {
            if (grouped[key].length === 0) {
                delete grouped[key];
            }
        });

        return grouped;
    }

    getSeverityIcon(severity) {
        const icons = {
            'critical': '<i class="bi bi-exclamation-triangle-fill text-danger"></i>',
            'high': '<i class="bi bi-exclamation-triangle text-warning"></i>',
            'medium': '<i class="bi bi-info-circle text-info"></i>',
            'low': '<i class="bi bi-check-circle text-success"></i>',
            'minor': '<i class="bi bi-dot text-muted"></i>'
        };
        return icons[severity] || icons['medium'];
    }

    getSeverityTitle(severity) {
        const titles = {
            'critical': 'Problemi Critici',
            'high': 'Problemi Importanti',
            'medium': 'Problemi Medi',
            'low': 'Problemi Minori',
            'minor': 'Suggerimenti'
        };
        return titles[severity] || 'Problemi';
    }

    getSeverityBadgeClass(severity) {
        const classes = {
            'critical': 'bg-danger',
            'high': 'bg-warning',
            'medium': 'bg-info',
            'low': 'bg-success',
            'minor': 'bg-secondary'
        };
        return classes[severity] || 'bg-info';
    }

    populateSubAccordions(groupedIssues) {
        const subAccordionMapping = {
            'critical': 'criticalSubAccordion',
            'high': 'highSubAccordion',
            'medium': 'mediumSubAccordion', 
            'low': 'lowSubAccordion',
            'minor': 'lowSubAccordion'
        };

        Object.entries(groupedIssues).forEach(([severity, issues]) => {
            const subAccordionId = subAccordionMapping[severity];
            if (subAccordionId) {
                const container = document.getElementById(subAccordionId);
                if (container) {
                    // Group issues by type within this severity level
                    const issuesByType = this.groupIssuesByType(issues);
                    container.innerHTML = this.renderNestedAccordion(issuesByType, severity);
                }
            }
        });
    }

    groupIssuesByType(issues) {
        const grouped = {};
        
        // Map issue types to user-friendly titles
        const typeToTitle = {
            'broken_heading_hierarchy': '🏗️ Gerarchia Heading Interrotta',
            'meta_desc_too_short': '📝 Meta Description Troppo Corte', 
            'thin_content': '📄 Contenuto Insufficiente',
            'title_too_long': '📏 Title Troppo Lunghi',
            'title_too_short': '📏 Title Troppo Corti',
            'missing_h1': '🎯 H1 Mancanti',
            'duplicate_title': '🔄 Title Duplicati',
            'missing_meta_desc': '📝 Meta Description Mancanti',
            'images_without_alt': '🖼️ Immagini Senza Alt Text',
            'broken_links': '🔗 Link Interrotti'
        };
        
        issues.forEach(issue => {
            const type = issue.type || 'unknown';
            const friendlyTitle = typeToTitle[type] || issue.title || 'Problema sconosciuto';
            
            if (!grouped[type]) {
                grouped[type] = {
                    title: friendlyTitle,
                    issues: []
                };
            }
            grouped[type].issues.push(issue);
        });
        
        return grouped;
    }

    renderNestedAccordion(issuesByType, severity) {
        return Object.entries(issuesByType).map(([type, typeData], index) => {
            const accordionId = `${severity}-${type}-accordion`;
            const collapseId = `${severity}-${type}-collapse`;
            
            // Get first issue to extract common description and recommendation
            const firstIssue = typeData.issues[0];
            const commonDescription = firstIssue?.description || '';
            const commonRecommendation = firstIssue?.recommendation || '';
            
            return `
                <div class="accordion-item">
                    <h3 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" 
                                data-bs-toggle="collapse" 
                                data-bs-target="#${collapseId}" 
                                aria-expanded="false">
                            <div class="d-flex justify-content-between align-items-center w-100 me-3">
                                <span>${typeData.title}</span>
                                <span class="badge ${this.getSeverityBadgeClass(severity)} ms-2">${typeData.issues.length}</span>
                            </div>
                        </button>
                    </h3>
                    <div id="${collapseId}" class="accordion-collapse collapse" data-bs-parent="#${severity}SubAccordion">
                        <div class="accordion-body">
                            ${commonDescription || commonRecommendation ? `
                                <div class="mb-3 p-3 bg-light rounded border-start border-primary border-3">
                                    ${commonDescription ? `
                                        <div class="mb-2">
                                            <strong class="text-dark">📋 Problema:</strong>
                                            <span class="text-muted">${commonDescription}</span>
                                        </div>
                                    ` : ''}
                                    ${commonRecommendation ? `
                                        <div>
                                            <strong class="text-primary">💡 Best Practice:</strong>
                                            <span class="text-primary">${commonRecommendation}</span>
                                        </div>
                                    ` : ''}
                                </div>
                                <div class="mb-2"><strong>Pagine interessate:</strong></div>
                            ` : ''}
                            ${this.renderIssuesListCompact(typeData.issues)}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderIssuesList(issues) {
        return issues.map((issue, index) => `
            <div class="border-bottom py-2 ${index === issues.length - 1 ? 'border-0' : ''}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="fw-medium mb-1" style="font-size: 0.9rem;">${issue.title || 'Problema SEO'}</div>
                        <div class="text-muted small mb-1">${issue.description || 'Nessuna descrizione disponibile'}</div>
                        ${issue.recommendation ? `
                            <div class="bg-light border-start border-primary border-2 px-2 py-1 mb-1 rounded-end">
                                <small class="text-primary"><i class="bi bi-lightbulb"></i> ${issue.recommendation}</small>
                            </div>
                        ` : ''}
                        ${issue.page && issue.page.url ? `
                            <div class="mt-1">
                                <small class="text-muted">
                                    <i class="bi bi-link-45deg"></i>
                                    <a href="${issue.page.url}" target="_blank" class="text-decoration-none">
                                        ${this.truncateUrl(issue.page.url, 40)}
                                    </a>
                                </small>
                            </div>
                        ` : ''}
                    </div>
                    <div class="text-end ms-2">
                        <span class="badge ${this.getSeverityBadgeClass(issue.severity)}" style="font-size: 0.7rem;">
                            ${issue.severity}
                        </span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderIssuesListCompact(issues) {
        return issues.map((issue, index) => `
            <div class="border-bottom py-2 ${index === issues.length - 1 ? 'border-0' : ''}">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="flex-grow-1">
                        ${issue.page && issue.page.url ? `
                            <div>
                                <i class="bi bi-link-45deg text-muted"></i>
                                <a href="${issue.page.url}" target="_blank" class="text-decoration-none">
                                    ${this.truncateUrl(issue.page.url, 60)}
                                </a>
                            </div>
                        ` : `
                            <div class="text-muted">
                                ${issue.title || 'Problema SEO'}
                            </div>
                        `}
                    </div>
                    <div class="text-end ms-2">
                        <small class="text-muted">${issue.severity}</small>
                    </div>
                </div>
            </div>
        `).join('');
    }

    truncateUrl(url, maxLength = 50) {
        if (url.length <= maxLength) return url;
        return url.substring(0, maxLength) + '...';
    }

    renderPagesTable() {
        const tbody = document.getElementById('pages-table-body');
        if (!tbody) return;

        if (!this.currentPages || this.currentPages.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center py-4">
                        <div class="text-muted">
                            <i class="bi bi-file-earmark fs-1 opacity-50"></i>
                            <p class="mt-2">Nessuna pagina trovata</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.currentPages.slice(0, 100).map(page => `
            <tr>
                <td>
                    <a href="${page.url}" target="_blank" class="text-decoration-none">
                        ${this.truncateUrl(page.url, 60)}
                        <i class="bi bi-box-arrow-up-right ms-1 small"></i>
                    </a>
                </td>
                <td>
                    <span class="badge ${this.getStatusCodeBadge(page.status_code).class}">
                        ${page.status_code}
                    </span>
                </td>
                <td>
                    ${page.title ? page.title.substring(0, 50) + (page.title.length > 50 ? '...' : '') : '-'}
                </td>
                <td>
                    ${page.word_count || '-'}
                </td>
                <td>
                    ${page.response_time ? page.response_time + 'ms' : '-'}
                </td>
                <td>
                    <span class="badge bg-info">${page.issues_count || 0}</span>
                </td>
            </tr>
        `).join('');

        // Show message if there are more pages
        if (this.currentPages.length > 100) {
            const moreRow = document.createElement('tr');
            moreRow.innerHTML = `
                <td colspan="6" class="text-center text-muted py-2">
                    <small>Mostrate prime 100 pagine di ${this.currentPages.length} totali</small>
                </td>
            `;
            tbody.appendChild(moreRow);
        }
    }

    getStatusCodeBadge(statusCode) {
        if (statusCode >= 200 && statusCode < 300) {
            return { class: 'bg-success' };
        } else if (statusCode >= 300 && statusCode < 400) {
            return { class: 'bg-warning' };
        } else if (statusCode >= 400) {
            return { class: 'bg-danger' };
        }
        return { class: 'bg-secondary' };
    }

    applyIssueFilters() {
        // This could be enhanced to filter the displayed issues
        // For now, we'll just re-render with the current data
        this.renderIssuesAccordion();
    }
}

// Export module
window.scanResults = new ScanResultsModule();