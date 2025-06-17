// SEO Auditing Solution - Scheduler Module
class SchedulerModule {
    constructor() {
        this.filteredSchedules = [];
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('scheduler-refresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // Queue action buttons
        const purgeBtn = document.getElementById('purge-queue-btn');
        if (purgeBtn) {
            purgeBtn.addEventListener('click', () => {
                this.purgeQueue();
            });
        }

        const pauseBtn = document.getElementById('pause-scheduler-btn');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                this.pauseScheduler();
            });
        }

        const resumeBtn = document.getElementById('resume-scheduler-btn');
        if (resumeBtn) {
            resumeBtn.addEventListener('click', () => {
                this.resumeScheduler();
            });
        }

        // Filter inputs
        const searchInput = document.getElementById('schedule-search');
        if (searchInput) {
            searchInput.addEventListener('input', utils.debounce(() => {
                this.applyFilters();
            }, 300));
        }

        const statusFilter = document.getElementById('schedule-status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                this.applyFilters();
            });
        }

        const frequencyFilter = document.getElementById('schedule-frequency-filter');
        if (frequencyFilter) {
            frequencyFilter.addEventListener('change', () => {
                this.applyFilters();
            });
        }

        // Subscribe to data changes
        appState.subscribe('data.scheduledScans', () => {
            this.applyFilters();
        });

        appState.subscribe('data.schedulerStats', () => {
            this.updateStatsDisplay();
        });
    }

    startRealTimeUpdates() {
        // Update every 10 seconds
        this.refreshInterval = setInterval(() => {
            this.loadSchedulerStats();
            this.loadActiveTasks();
            // Refresh schedules every minute to update next_run_at times
            if (Date.now() % 60000 < 10000) {
                this.loadScheduledScans();
            }
        }, 10000);
    }

    stopRealTimeUpdates() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    async loadData() {
        try {
            appState.setLoading('scheduler', true);
            
            // Load all scheduler data
            await Promise.all([
                this.loadSchedulerStats(),
                this.loadScheduledScans(),
                this.loadActiveTasks(),
                this.loadRecentTasks()
            ]);

        } catch (error) {
            console.error('Error loading scheduler data:', error);
            utils.showToast('Errore nel caricamento del scheduler', 'error');
        } finally {
            appState.setLoading('scheduler', false);
        }
    }

    async loadSchedulerStats() {
        try {
            const stats = await apiClient.getSchedulerStats();
            appState.setData('schedulerStats', stats);
            this.updateStatsDisplay();
        } catch (error) {
            console.error('Error loading scheduler stats:', error);
        }
    }

    async loadScheduledScans() {
        try {
            // Load real schedules from new API
            const [schedules, websites, clients] = await Promise.all([
                apiClient.getSchedules(),
                apiClient.getWebsites(),
                apiClient.getClients()
            ]);
            
            // Enrich schedules with website and client data
            const enrichedSchedules = schedules.map(schedule => {
                const website = websites.find(w => w.id === schedule.website_id);
                let enrichedWebsite = website || null;
                
                if (enrichedWebsite && enrichedWebsite.client_id) {
                    const client = clients.find(c => c.id === enrichedWebsite.client_id);
                    enrichedWebsite = {
                        ...enrichedWebsite,
                        client: client || null
                    };
                }
                
                return {
                    ...schedule,
                    website: enrichedWebsite
                };
            });
            
            appState.setData('scheduledScans', enrichedSchedules);
        } catch (error) {
            console.error('Error loading scheduled scans:', error);
        }
    }

    async loadActiveTasks() {
        try {
            const activeTasks = await apiClient.getActiveTasks();
            appState.setData('activeTasks', activeTasks);
            this.updateActiveTasksDisplay(activeTasks);
        } catch (error) {
            console.error('Error loading active tasks:', error);
        }
    }

    async loadRecentTasks() {
        try {
            const recentTasks = await apiClient.getRecentTasks();
            appState.setData('recentTasks', recentTasks);
            this.updateRecentTasksDisplay(recentTasks);
        } catch (error) {
            console.error('Error loading recent tasks:', error);
        }
    }

    updateStatsDisplay() {
        const stats = appState.getData('schedulerStats');
        if (!stats) return;

        // Update main stats cards
        const elementsToUpdate = {
            'queue-size': stats.queue_size || 0,
            'active-workers': stats.active_workers || 0,
            'scheduled-scans-count': stats.scheduled_scans || 0,
            'processed-today': stats.processed_today || 0,
            'failed-today': stats.failed_today || 0
        };

        Object.entries(elementsToUpdate).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });

        // Update status indicator
        const statusElement = document.getElementById('scheduler-status');
        if (statusElement) {
            const isHealthy = stats.active_workers > 0 && stats.queue_size < 100;
            statusElement.className = `badge ${isHealthy ? 'bg-success' : 'bg-warning'}`;
            statusElement.innerHTML = `<i class="bi bi-${isHealthy ? 'check-circle' : 'exclamation-triangle'}"></i> ${isHealthy ? 'Operativo' : 'Attenzione'}`;
        }

        // Update progress bars
        this.updateWorkerProgress(stats);
    }

    updateWorkerProgress(stats) {
        const workerProgress = document.getElementById('worker-progress');
        if (workerProgress && stats.worker_stats) {
            const maxWorkers = stats.max_workers || 4;
            const activeWorkers = stats.active_workers || 0;
            const percentage = (activeWorkers / maxWorkers) * 100;
            
            workerProgress.style.width = `${percentage}%`;
            workerProgress.textContent = `${activeWorkers}/${maxWorkers}`;
        }

        const queueProgress = document.getElementById('queue-progress');
        if (queueProgress && stats.queue_size !== undefined) {
            const maxQueue = 100; // Threshold for "busy"
            const percentage = Math.min((stats.queue_size / maxQueue) * 100, 100);
            
            queueProgress.style.width = `${percentage}%`;
            queueProgress.className = `progress-bar ${percentage > 80 ? 'bg-danger' : percentage > 50 ? 'bg-warning' : 'bg-success'}`;
        }
    }

    updateActiveTasksDisplay(tasks) {
        const container = document.getElementById('active-tasks-list');
        if (!container) return;

        if (!tasks || tasks.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="bi bi-clock fs-1 opacity-50"></i>
                    <p class="mt-2">Nessun task attivo</p>
                </div>
            `;
            return;
        }

        container.innerHTML = tasks.map(task => `
            <div class="card mb-2">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title mb-1">${task.name || 'Scansione SEO'}</h6>
                            <small class="text-muted">
                                ${task.website_domain || 'Dominio sconosciuto'}
                            </small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-info">
                                <i class="bi bi-arrow-clockwise"></i> In corso
                            </span>
                            <div class="small text-muted mt-1">
                                ${utils.formatRelativeTime(task.started_at)}
                            </div>
                        </div>
                    </div>
                    ${task.progress ? `
                        <div class="progress mt-2" style="height: 4px;">
                            <div class="progress-bar bg-info" 
                                 role="progressbar" 
                                 style="width: ${task.progress}%"
                                 aria-valuenow="${task.progress}" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                            </div>
                        </div>
                        <small class="text-muted">${task.progress}% completato</small>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    updateRecentTasksDisplay(tasks) {
        const container = document.getElementById('recent-tasks-list');
        if (!container) return;

        if (!tasks || tasks.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="bi bi-list-task fs-1 opacity-50"></i>
                    <p class="mt-2">Nessun task recente</p>
                </div>
            `;
            return;
        }

        container.innerHTML = tasks.slice(0, 10).map(task => `
            <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                <div>
                    <div class="fw-medium">${task.website_domain || 'Scansione'}</div>
                    <small class="text-muted">${utils.formatRelativeTime(task.completed_at)}</small>
                </div>
                <div class="text-end">
                    ${this.getTaskStatusBadge(task.status)}
                    ${task.duration ? `<div class="small text-muted">${task.duration}s</div>` : ''}
                </div>
            </div>
        `).join('');
    }

    getTaskStatusBadge(status) {
        const statusMap = {
            'success': { class: 'bg-success', text: 'Completato', icon: 'check-circle' },
            'failure': { class: 'bg-danger', text: 'Fallito', icon: 'x-circle' },
            'retry': { class: 'bg-warning', text: 'Riprovato', icon: 'arrow-clockwise' },
            'revoked': { class: 'bg-secondary', text: 'Annullato', icon: 'stop-circle' }
        };
        
        const config = statusMap[status] || { class: 'bg-secondary', text: status, icon: 'question' };
        return `<span class="badge ${config.class}">
            <i class="bi bi-${config.icon}"></i> ${config.text}
        </span>`;
    }

    applyFilters() {
        const scheduledScans = appState.getData('scheduledScans') || [];
        const searchInput = document.getElementById('schedule-search');
        const statusFilter = document.getElementById('schedule-status-filter');
        const frequencyFilter = document.getElementById('schedule-frequency-filter');
        
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const statusValue = statusFilter ? statusFilter.value : '';
        const frequencyValue = frequencyFilter ? frequencyFilter.value : '';

        this.filteredSchedules = scheduledScans.filter(schedule => {
            const matchesSearch = !searchTerm || 
                (schedule.website?.domain && schedule.website.domain.toLowerCase().includes(searchTerm)) ||
                (schedule.website?.client?.name && schedule.website.client.name.toLowerCase().includes(searchTerm));
            
            const matchesStatus = !statusValue || 
                (statusValue === 'active' && schedule.is_active) ||
                (statusValue === 'inactive' && !schedule.is_active) ||
                (statusValue === 'error' && schedule.last_error);

            const matchesFrequency = !frequencyValue || schedule.frequency === frequencyValue;

            return matchesSearch && matchesStatus && matchesFrequency;
        });

        // Sort by next_run_at (soonest first)
        this.filteredSchedules.sort((a, b) => {
            if (!a.next_run_at) return 1;
            if (!b.next_run_at) return -1;
            return new Date(a.next_run_at) - new Date(b.next_run_at);
        });

        this.renderScheduledScansTable();
        this.updateScheduleStats();
    }

    renderScheduledScansTable() {
        const tbody = document.getElementById('scheduled-scans-table-body');
        if (!tbody) return;

        if (this.filteredSchedules.length === 0) {
            const totalSchedules = appState.getData('scheduledScans')?.length || 0;
            const message = totalSchedules === 0 ? 
                'Nessuna programmazione configurata' : 
                'Nessuna programmazione corrisponde ai filtri';
            const buttonText = totalSchedules === 0 ? 
                'Nuova Programmazione' : 
                'Reset Filtri';
            const buttonAction = totalSchedules === 0 ? 
                'scheduler.showScheduleModal()' : 
                'scheduler.clearFilters()';
            
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center py-4">
                        <div class="text-muted">
                            <i class="bi bi-calendar-x fs-1 opacity-50"></i>
                            <p class="mt-2">${message}</p>
                            <button class="btn btn-primary btn-sm me-2" onclick="${buttonAction}">
                                <i class="bi bi-${totalSchedules === 0 ? 'plus' : 'x-circle'}"></i> ${buttonText}
                            </button>
                            ${totalSchedules === 0 ? `
                                <button class="btn btn-warning btn-sm" onclick="scheduler.showBulkScheduleModal()">
                                    <i class="bi bi-lightning"></i> Programmazione Bulk
                                </button>
                            ` : ''}
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.filteredSchedules.map(schedule => `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="me-3">
                            <i class="bi bi-globe text-success fs-4"></i>
                        </div>
                        <div>
                            <div class="fw-bold">${schedule.website?.domain || 'Sito sconosciuto'}</div>
                            ${schedule.website?.client?.name ? 
                                `<small class="text-muted">Cliente: ${schedule.website.client.name}</small>` : 
                                ''
                            }
                        </div>
                    </div>
                </td>
                <td>
                    ${this.getFrequencyBadge(schedule.frequency)}
                </td>
                <td>
                    <div class="text-muted small">
                        ${schedule.last_run_at ? 
                            utils.formatRelativeTime(schedule.last_run_at) : 
                            'Mai eseguita'
                        }
                    </div>
                </td>
                <td>
                    <div class="text-muted small">
                        ${schedule.next_run_at ? 
                            this.formatNextRun(schedule.next_run_at) : 
                            'Non programmata'
                        }
                    </div>
                </td>
                <td>
                    ${this.getScheduleStatusBadge(schedule)}
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="scheduler.editSchedule(${schedule.id})" title="Modifica">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="scheduler.runNow(${schedule.id})" title="Esegui Ora">
                            <i class="bi bi-play-circle"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="scheduler.deleteSchedule(${schedule.id})" title="Elimina">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    getFrequencyBadge(frequency) {
        const frequencyMap = {
            'daily': { class: 'bg-success', text: '🌅 Giornaliera', icon: 'calendar-day' },
            'weekly': { class: 'bg-info', text: '📅 Settimanale', icon: 'calendar-week' },
            'monthly': { class: 'bg-warning', text: '🗓️ Mensile', icon: 'calendar-month' },
            'hourly': { class: 'bg-primary', text: '⏰ Oraria', icon: 'clock' }
        };
        
        const config = frequencyMap[frequency] || { class: 'bg-secondary', text: frequency, icon: 'dash' };
        return `<span class="badge ${config.class}">
            <i class="bi bi-${config.icon}"></i> ${config.text}
        </span>`;
    }

    getScheduleStatusBadge(schedule) {
        if (!schedule.is_active) {
            return '<span class="badge bg-secondary"><i class="bi bi-pause-circle"></i> Inattiva</span>';
        }
        
        if (schedule.last_error) {
            return '<span class="badge bg-danger"><i class="bi bi-exclamation-triangle"></i> Errore</span>';
        }
        
        return '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Attiva</span>';
    }

    refreshData() {
        return this.loadData();
    }

    // Queue Management Actions
    async purgeQueue() {
        if (!confirm('Sei sicuro di voler svuotare la coda? Questo annullerà tutti i task in attesa.')) {
            return;
        }

        try {
            await apiClient.purgeQueue();
            utils.showToast('Coda svuotata con successo', 'success');
            await this.loadSchedulerStats();
        } catch (error) {
            console.error('Error purging queue:', error);
            utils.showToast('Errore nello svuotamento della coda', 'error');
        }
    }

    async pauseScheduler() {
        if (!confirm('Sei sicuro di voler mettere in pausa lo scheduler?')) {
            return;
        }

        try {
            await apiClient.pauseScheduler();
            utils.showToast('Scheduler messo in pausa', 'success');
            await this.loadSchedulerStats();
        } catch (error) {
            console.error('Error pausing scheduler:', error);
            utils.showToast('Errore nel mettere in pausa lo scheduler', 'error');
        }
    }

    async resumeScheduler() {
        try {
            await apiClient.resumeScheduler();
            utils.showToast('Scheduler riavviato', 'success');
            await this.loadSchedulerStats();
        } catch (error) {
            console.error('Error resuming scheduler:', error);
            utils.showToast('Errore nel riavvio dello scheduler', 'error');
        }
    }

    // Schedule Management
    showScheduleModal() {
        // Populate website dropdown
        this.populateWebsiteDropdown();
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(document.getElementById('scheduleModal'));
            modal.show();
        } else {
            // Fallback
            const modalElement = document.getElementById('scheduleModal');
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
        const select = document.getElementById('scheduleWebsite');
        if (!select) return;

        const websites = appState.getData('websites') || [];
        const schedules = appState.getData('scheduledScans') || [];
        const scheduledWebsiteIds = new Set(schedules.map(s => s.website_id));
        
        // Filter out websites that already have schedules
        const unscheduledWebsites = websites.filter(w => 
            w.is_active && !scheduledWebsiteIds.has(w.id)
        );
        
        select.innerHTML = '<option value="">Seleziona sito web...</option>';
        
        if (unscheduledWebsites.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'Tutti i siti sono già programmati';
            option.disabled = true;
            select.appendChild(option);
            return;
        }
        
        unscheduledWebsites.forEach(website => {
            const option = document.createElement('option');
            option.value = website.id;
            option.textContent = `${website.domain} ${website.client ? `(${website.client.name})` : ''}`;
            select.appendChild(option);
        });
    }

    async createSchedule() {
        const websiteSelect = document.getElementById('scheduleWebsite');
        const frequencySelect = document.getElementById('scheduleFrequency');
        
        if (!websiteSelect || !frequencySelect) return;

        const scheduleData = {
            website_id: parseInt(websiteSelect.value),
            frequency: frequencySelect.value,
            is_active: true
        };

        // Validate
        if (!scheduleData.website_id) {
            utils.showToast('Seleziona un sito web', 'error');
            return;
        }

        if (!scheduleData.frequency) {
            utils.showToast('Seleziona una frequenza', 'error');
            return;
        }

        try {
            await apiClient.createSchedule(scheduleData);
            
            utils.showToast('Programmazione creata con successo', 'success');
            
            // Close modal and refresh
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                bootstrap.Modal.getInstance(document.getElementById('scheduleModal')).hide();
            }
            await this.loadScheduledScans();
            this.applyFilters();
            
        } catch (error) {
            console.error('Error creating schedule:', error);
            const errorMsg = error.message.includes('already exists') ? 
                'Programmazione già esistente per questo sito' : 
                'Errore nella creazione della programmazione';
            utils.showToast(errorMsg, 'error');
        }
    }

    async editSchedule(scheduleId) {
        try {
            const schedule = await apiClient.getSchedule(scheduleId);
            const schedules = appState.getData('scheduledScans') || [];
            const scheduleWithWebsite = schedules.find(s => s.id === scheduleId);
            
            // Populate edit modal
            document.getElementById('editWebsiteId').value = schedule.website_id;
            document.getElementById('editWebsiteDomain').value = scheduleWithWebsite?.website?.domain || 'Sito sconosciuto';
            document.getElementById('editScheduleFrequency').value = schedule.frequency;
            document.getElementById('editScheduleActive').checked = schedule.is_active;
            
            // Store schedule ID for later use
            this.currentEditScheduleId = scheduleId;
            
            // Show modal
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                const modal = new bootstrap.Modal(document.getElementById('editScheduleModal'));
                modal.show();
            }
            
        } catch (error) {
            console.error('Error loading schedule for edit:', error);
            utils.showToast('Errore nel caricamento della programmazione', 'error');
        }
    }

    async updateSchedule() {
        if (!this.currentEditScheduleId) return;
        
        const frequencySelect = document.getElementById('editScheduleFrequency');
        const activeCheck = document.getElementById('editScheduleActive');
        
        const scheduleData = {
            frequency: frequencySelect.value,
            is_active: activeCheck.checked
        };
        
        try {
            await apiClient.updateSchedule(this.currentEditScheduleId, scheduleData);
            utils.showToast('Programmazione aggiornata con successo', 'success');
            
            // Close modal and refresh
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                bootstrap.Modal.getInstance(document.getElementById('editScheduleModal')).hide();
            }
            await this.loadScheduledScans();
            this.applyFilters();
            
        } catch (error) {
            console.error('Error updating schedule:', error);
            utils.showToast('Errore nell\'aggiornamento della programmazione', 'error');
        }
    }

    async deleteScheduleFromModal() {
        if (!this.currentEditScheduleId) return;
        
        if (!confirm('Sei sicuro di voler eliminare questa programmazione?')) {
            return;
        }
        
        try {
            await apiClient.deleteSchedule(this.currentEditScheduleId);
            utils.showToast('Programmazione eliminata con successo', 'success');
            
            // Close modal and refresh
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                bootstrap.Modal.getInstance(document.getElementById('editScheduleModal')).hide();
            }
            await this.loadScheduledScans();
            this.applyFilters();
            
        } catch (error) {
            console.error('Error deleting schedule:', error);
            utils.showToast('Errore nell\'eliminazione della programmazione', 'error');
        }
    }

    async runNow(scheduleId) {
        if (!confirm('Vuoi eseguire subito questa scansione programmata?')) {
            return;
        }

        try {
            await apiClient.runScheduleNow(scheduleId);
            utils.showToast('Scansione avviata manualmente', 'success');
            await this.loadActiveTasks();
        } catch (error) {
            console.error('Error running schedule now:', error);
            utils.showToast('Errore nell\'avvio della scansione', 'error');
        }
    }

    async deleteSchedule(scheduleId) {
        if (!confirm('Sei sicuro di voler eliminare questa programmazione?')) {
            return;
        }

        try {
            await apiClient.deleteSchedule(scheduleId);
            
            utils.showToast('Programmazione eliminata con successo', 'success');
            await this.loadScheduledScans();
            
        } catch (error) {
            console.error('Error deleting schedule:', error);
            utils.showToast('Errore nell\'eliminazione della programmazione', 'error');
        }
    }

    // Bulk Operations
    async showBulkScheduleModal() {
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(document.getElementById('bulkScheduleModal'));
            modal.show();
        } else {
            alert('Funzionalità bulk scheduling non disponibile');
        }
    }

    async createBulkSchedules() {
        const frequencySelect = document.getElementById('bulkFrequency');
        const onlyUnscheduledCheck = document.getElementById('bulkOnlyUnscheduled');
        
        if (!frequencySelect) {
            utils.showToast('Elementi del form non trovati', 'error');
            return;
        }

        const frequency = frequencySelect.value || 'monthly';
        const onlyUnscheduled = onlyUnscheduledCheck ? onlyUnscheduledCheck.checked : true;

        if (!confirm(`Sei sicuro di voler programmare tutti i siti web con frequenza ${frequency}?`)) {
            return;
        }

        try {
            utils.showToast('Creazione programmazioni in corso...', 'info');
            
            const result = await apiClient.createBulkSchedules(frequency, onlyUnscheduled);
            
            utils.showToast(
                `Operazione completata: ${result.created} create, ${result.skipped} saltate`, 
                'success'
            );
            
            // Close modal and refresh
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                bootstrap.Modal.getInstance(document.getElementById('bulkScheduleModal')).hide();
            }
            
            await this.loadScheduledScans();
            this.applyFilters();
            
        } catch (error) {
            console.error('Error creating bulk schedules:', error);
            utils.showToast('Errore nella creazione delle programmazioni', 'error');
        }
    }

    updateScheduleStats() {
        const totalSchedules = appState.getData('scheduledScans')?.length || 0;
        const filteredCount = this.filteredSchedules.length;
        const activeSchedules = this.filteredSchedules.filter(s => s.is_active).length;
        const inactiveSchedules = this.filteredSchedules.filter(s => !s.is_active).length;
        const errorSchedules = this.filteredSchedules.filter(s => s.last_error).length;

        // Update header stats if elements exist
        const elements = {
            'scheduled-scans-count': totalSchedules,
            'active-schedules-count': activeSchedules,
            'inactive-schedules-count': inactiveSchedules,
            'error-schedules-count': errorSchedules
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });

        // Update status in page title or somewhere visible
        console.log(`📊 Schedules Stats: ${filteredCount}/${totalSchedules} shown, ${activeSchedules} active, ${errorSchedules} errors`);
    }

    formatNextRun(nextRunAt) {
        const now = new Date();
        const nextRun = new Date(nextRunAt);
        const diff = nextRun - now;
        
        if (diff < 0) {
            return '<span class="text-danger">🔴 In ritardo</span>';
        }
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) {
            return `📅 In ${days} giorni`;
        } else if (hours > 0) {
            return `⏰ In ${hours} ore`;
        } else if (minutes > 0) {
            return `⏱️ In ${minutes} minuti`;
        } else {
            return '<span class="text-warning">🟡 Imminente</span>';
        }
    }

    clearFilters() {
        const searchInput = document.getElementById('schedule-search');
        const statusFilter = document.getElementById('schedule-status-filter');
        const frequencyFilter = document.getElementById('schedule-frequency-filter');

        if (searchInput) searchInput.value = '';
        if (statusFilter) statusFilter.value = '';
        if (frequencyFilter) frequencyFilter.value = '';

        this.applyFilters();
    }

    // Cleanup when switching sections
    destroy() {
        this.stopRealTimeUpdates();
    }
}

// Export module
window.scheduler = new SchedulerModule();