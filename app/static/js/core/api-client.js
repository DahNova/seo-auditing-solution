// SEO Auditing Solution - API Client
class APIClient {
    constructor() {
        this.baseURL = '/api/v1';
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    async request(method, endpoint, data = null, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;
        const config = {
            method,
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        if (data && ['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // Handle different content types
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else if (contentType && contentType.includes('application/pdf')) {
                return await response.blob();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error(`API Error [${method} ${endpoint}]:`, error);
            throw error;
        }
    }

    // HTTP Methods
    async get(endpoint, options = {}) {
        return this.request('GET', endpoint, null, options);
    }

    async post(endpoint, data, options = {}) {
        return this.request('POST', endpoint, data, options);
    }

    async put(endpoint, data, options = {}) {
        return this.request('PUT', endpoint, data, options);
    }

    async delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    }

    // ===== CLIENTS API =====
    async getClients(skip = 0, limit = 100) {
        return this.get(`/clients/?skip=${skip}&limit=${limit}`);
    }

    async getClient(clientId) {
        return this.get(`/clients/${clientId}`);
    }

    async createClient(clientData) {
        return this.post('/clients/', clientData);
    }

    async updateClient(clientId, clientData) {
        return this.put(`/clients/${clientId}`, clientData);
    }

    async deleteClient(clientId) {
        return this.delete(`/clients/${clientId}`);
    }

    // ===== WEBSITES API =====
    async getWebsites(skip = 0, limit = 100) {
        return this.get(`/websites/?skip=${skip}&limit=${limit}`);
    }

    async getWebsite(websiteId) {
        return this.get(`/websites/${websiteId}`);
    }

    async createWebsite(websiteData) {
        return this.post('/websites/', websiteData);
    }

    async updateWebsite(websiteId, websiteData) {
        return this.put(`/websites/${websiteId}`, websiteData);
    }

    async deleteWebsite(websiteId) {
        return this.delete(`/websites/${websiteId}`);
    }

    // ===== SCANS API =====
    async getScans(skip = 0, limit = 100) {
        return this.get(`/scans/?skip=${skip}&limit=${limit}`);
    }

    async getScan(scanId) {
        return this.get(`/scans/${scanId}`);
    }

    async createScan(scanData) {
        return this.post('/scans/', scanData);
    }

    async deleteScan(scanId) {
        return this.delete(`/scans/${scanId}`);
    }

    async retryScan(scanId) {
        return this.post(`/scans/${scanId}/retry`);
    }

    async cancelScan(scanId) {
        return this.post(`/scans/${scanId}/cancel`);
    }

    async getScanPages(scanId, skip = 0, limit = 25) {
        return this.get(`/scans/${scanId}/pages?skip=${skip}&limit=${limit}`);
    }

    async getScanIssues(scanId, skip = 0, limit = 1000) {
        return this.get(`/scans/${scanId}/issues?skip=${skip}&limit=${limit}`);
    }

    async downloadScanReport(scanId) {
        return this.get(`/scans/${scanId}/report`);
    }

    // ===== SCHEDULER API =====
    async getSchedulerStatus() {
        return this.get('/scheduler/status');
    }

    async getActiveTasks() {
        return this.get('/scheduler/active-tasks');
    }

    async getRecentTasks() {
        return this.get('/scheduler/recent-tasks');
    }

    async getScheduledScans() {
        return this.get('/scheduler/scheduled-scans');
    }

    async getSchedulerStats() {
        return this.get('/scheduler/stats');
    }

    async getWorkerStats() {
        return this.get('/scheduler/worker-stats');
    }

    async purgeQueue() {
        return this.post('/scheduler/actions/purge-queue');
    }

    async pauseScheduler() {
        return this.post('/scheduler/actions/pause');
    }

    async resumeScheduler() {
        return this.post('/scheduler/actions/resume');
    }

    // ===== SCHEDULES API =====
    async getSchedules(skip = 0, limit = 100) {
        return this.get(`/schedules/?skip=${skip}&limit=${limit}`);
    }

    async getSchedule(scheduleId) {
        return this.get(`/schedules/${scheduleId}`);
    }

    async createSchedule(scheduleData) {
        return this.post('/schedules/', scheduleData);
    }

    async updateSchedule(scheduleId, scheduleData) {
        return this.put(`/schedules/${scheduleId}`, scheduleData);
    }

    async deleteSchedule(scheduleId) {
        return this.delete(`/schedules/${scheduleId}`);
    }

    async runScheduleNow(scheduleId) {
        return this.post(`/schedules/${scheduleId}/run-now`);
    }

    async getDueSchedules() {
        return this.get('/schedules/due/list');
    }

    async createBulkSchedules(frequency = 'monthly', onlyUnscheduled = true) {
        return this.post(`/schedules/bulk/create?frequency=${frequency}&only_unscheduled=${onlyUnscheduled}`);
    }
}

// Export singleton instance
window.apiClient = new APIClient();