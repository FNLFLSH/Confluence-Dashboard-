// Dashboard JavaScript
class ConfluenceDashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5001/api';
        this.charts = {};
        this.currentFilters = {
            category: 'all',
            quarter: 'all',
            module: 'all'
        };
        this.currentPage = 0;
        this.pageSize = 20;
        this.searchQuery = '';
        
        this.init();
    }

    async init() {
        try {
            // Check API health
            await this.checkHealth();
            
            // Load initial data
            await this.loadSummaryStats();
            await this.loadFilters();
            await this.loadCharts();
            await this.loadTable();
            
            // Set up event listeners
            this.setupEventListeners();
            
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.showError('Failed to initialize dashboard');
        }
    }

    async checkHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy' && data.data_loaded) {
                this.updateStatus('success', `✅ Data loaded successfully (${data.data_count} releases)`);
            } else {
                this.updateStatus('warning', '⚠️ Data not available');
            }
        } catch (error) {
            this.updateStatus('error', '❌ API connection failed');
            throw error;
        }
    }

    updateStatus(type, message) {
        const statusCard = document.getElementById('status-card');
        const statusMessage = document.getElementById('status-message');
        const statusIcon = document.getElementById('status-icon');
        
        statusMessage.textContent = message;
        
        // Update card color based on status type
        statusCard.className = 'status-card';
        if (type === 'success') {
            statusCard.style.background = 'linear-gradient(45deg, #0033A0, #366092)';
        } else if (type === 'warning') {
            statusCard.style.background = 'linear-gradient(45deg, #ffc107, #fd7e14)';
        } else if (type === 'error') {
            statusCard.style.background = 'linear-gradient(45deg, #dc3545, #e83e8c)';
        }
        
        // Update icon
        statusIcon.innerHTML = type === 'success' ? 
            '<i class="fas fa-check-circle fa-2x"></i>' :
            type === 'warning' ? 
            '<i class="fas fa-exclamation-triangle fa-2x"></i>' :
            '<i class="fas fa-times-circle fa-2x"></i>';
    }

    async loadSummaryStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/summary`);
            const data = await response.json();
            
            document.getElementById('total-releases').textContent = data.total_releases.toLocaleString();
            document.getElementById('total-modules').textContent = data.total_modules.toLocaleString();
            document.getElementById('total-quarters').textContent = data.total_quarters.toLocaleString();
            document.getElementById('new-releases').textContent = data.new_releases.toLocaleString();
            
        } catch (error) {
            console.error('Failed to load summary stats:', error);
        }
    }

    async loadFilters() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/filters`);
            const data = await response.json();
            
            // Populate category filter
            const categoryFilter = document.getElementById('category-filter');
            categoryFilter.innerHTML = '<option value="all">All Categories</option>';
            data.categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                categoryFilter.appendChild(option);
            });
            
            // Populate quarter filter
            const quarterFilter = document.getElementById('quarter-filter');
            quarterFilter.innerHTML = '<option value="all">All Quarters</option>';
            data.quarters.forEach(quarter => {
                const option = document.createElement('option');
                option.value = quarter;
                option.textContent = quarter;
                quarterFilter.appendChild(option);
            });
            
            // Populate module filter
            const moduleFilter = document.getElementById('module-filter');
            moduleFilter.innerHTML = '<option value="all">All Modules</option>';
            data.modules.forEach(module => {
                const option = document.createElement('option');
                option.value = module;
                option.textContent = module;
                moduleFilter.appendChild(option);
            });
            
        } catch (error) {
            console.error('Failed to load filters:', error);
        }
    }

    async loadCharts() {
        await this.loadCategoryChart();
        await this.loadTimelineChart();
        await this.loadModulesChart();
    }

    async loadCategoryChart() {
        try {
            const params = new URLSearchParams(this.currentFilters);
            const response = await fetch(`${this.apiBaseUrl}/charts/category?${params}`);
            const data = await response.json();
            
            const ctx = document.getElementById('categoryChart').getContext('2d');
            
            if (this.charts.category) {
                this.charts.category.destroy();
            }
            
            this.charts.category = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [
                            '#dc3545', // Bug Fix
                            '#ffc107', // Enhancement
                            '#28a745', // New Feature
                            '#6c757d'  // Other
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
            
        } catch (error) {
            console.error('Failed to load category chart:', error);
        }
    }

    async loadTimelineChart() {
        try {
            const params = new URLSearchParams(this.currentFilters);
            const response = await fetch(`${this.apiBaseUrl}/charts/timeline?${params}`);
            const data = await response.json();
            
            const ctx = document.getElementById('timelineChart').getContext('2d');
            
            if (this.charts.timeline) {
                this.charts.timeline.destroy();
            }
            
            this.charts.timeline = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.quarters,
                    datasets: [{
                        label: 'Releases',
                        data: data.counts,
                        backgroundColor: '#0033A0',
                        borderColor: '#366092',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
            
        } catch (error) {
            console.error('Failed to load timeline chart:', error);
        }
    }

    async loadModulesChart() {
        try {
            const params = new URLSearchParams(this.currentFilters);
            params.append('limit', '10');
            const response = await fetch(`${this.apiBaseUrl}/charts/modules?${params}`);
            const data = await response.json();
            
            const ctx = document.getElementById('modulesChart').getContext('2d');
            
            if (this.charts.modules) {
                this.charts.modules.destroy();
            }
            
            this.charts.modules = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.modules,
                    datasets: [{
                        label: 'Releases',
                        data: data.counts,
                        backgroundColor: '#366092',
                        borderColor: '#0033A0',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
            
        } catch (error) {
            console.error('Failed to load modules chart:', error);
        }
    }

    async loadTable() {
        try {
            const params = new URLSearchParams(this.currentFilters);
            params.append('limit', this.pageSize);
            params.append('offset', this.currentPage * this.pageSize);
            
            const response = await fetch(`${this.apiBaseUrl}/releases?${params}`);
            const data = await response.json();
            
            this.renderTable(data.releases, data.total);
            
        } catch (error) {
            console.error('Failed to load table:', error);
            this.showTableError();
        }
    }

    renderTable(releases, total) {
        const tableContainer = document.getElementById('table-container');
        
        if (releases.length === 0) {
            tableContainer.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-3x mb-3"></i>
                    <p>No releases found</p>
                </div>
            `;
            return;
        }
        
        let tableHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Category</th>
                            <th>Date</th>
                            <th>Module</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        releases.forEach(release => {
            const categoryClass = this.getCategoryClass(release.category);
            const truncatedTitle = release.title.length > 50 ? 
                release.title.substring(0, 50) + '...' : release.title;
            const truncatedModule = release.module_name.length > 30 ? 
                release.module_name.substring(0, 30) + '...' : release.module_name;
            
            tableHTML += `
                <tr>
                    <td title="${release.title}">${truncatedTitle}</td>
                    <td><span class="badge ${categoryClass}">${release.category}</span></td>
                    <td>${release.date}</td>
                    <td title="${release.module_name}">${truncatedModule}</td>
                </tr>
            `;
        });
        
        tableHTML += `
                    </tbody>
                </table>
            </div>
        `;
        
        // Add pagination if needed
        if (total > this.pageSize) {
            const totalPages = Math.ceil(total / this.pageSize);
            tableHTML += `
                <div class="pagination-container">
                    <button class="btn btn-sm btn-outline-primary" ${this.currentPage === 0 ? 'disabled' : ''} 
                            onclick="dashboard.previousPage()">
                        <i class="fas fa-chevron-left"></i> Previous
                    </button>
                    <span class="pagination-info">
                        Page ${this.currentPage + 1} of ${totalPages} (${total} total)
                    </span>
                    <button class="btn btn-sm btn-outline-primary" ${this.currentPage >= totalPages - 1 ? 'disabled' : ''} 
                            onclick="dashboard.nextPage()">
                        Next <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            `;
        }
        
        tableContainer.innerHTML = tableHTML;
    }

    getCategoryClass(category) {
        switch (category.toLowerCase()) {
            case 'bug fix':
                return 'badge-bug';
            case 'enhancement':
                return 'badge-enhancement';
            case 'new feature':
                return 'badge-new-feature';
            default:
                return 'badge-other';
        }
    }

    showTableError() {
        const tableContainer = document.getElementById('table-container');
        tableContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Failed to load release data. Please try again.
            </div>
        `;
    }

    showError(message) {
        // You could implement a toast notification system here
        console.error(message);
    }

    setupEventListeners() {
        // Filter change events
        document.getElementById('category-filter').addEventListener('change', (e) => {
            this.currentFilters.category = e.target.value;
            this.refreshData();
        });
        
        document.getElementById('quarter-filter').addEventListener('change', (e) => {
            this.currentFilters.quarter = e.target.value;
            this.refreshData();
        });
        
        document.getElementById('module-filter').addEventListener('change', (e) => {
            this.currentFilters.module = e.target.value;
            this.refreshData();
        });
        
        // Reset filters button
        document.getElementById('reset-filters').addEventListener('click', () => {
            this.resetFilters();
        });
        
        // Search input
        let searchTimeout;
        document.getElementById('search-input').addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.searchQuery = e.target.value;
                this.performSearch();
            }, 500);
        });
    }

    async refreshData() {
        this.currentPage = 0; // Reset to first page
        await this.loadCharts();
        await this.loadTable();
    }

    resetFilters() {
        this.currentFilters = {
            category: 'all',
            quarter: 'all',
            module: 'all'
        };
        
        document.getElementById('category-filter').value = 'all';
        document.getElementById('quarter-filter').value = 'all';
        document.getElementById('module-filter').value = 'all';
        document.getElementById('search-input').value = '';
        
        this.searchQuery = '';
        this.currentPage = 0;
        this.refreshData();
    }

    async performSearch() {
        if (!this.searchQuery.trim()) {
            await this.loadTable();
            return;
        }
        
        try {
            const params = new URLSearchParams({
                q: this.searchQuery,
                limit: this.pageSize
            });
            
            const response = await fetch(`${this.apiBaseUrl}/search?${params}`);
            const data = await response.json();
            
            this.renderTable(data.releases, data.total);
            
        } catch (error) {
            console.error('Search failed:', error);
            this.showTableError();
        }
    }

    async previousPage() {
        if (this.currentPage > 0) {
            this.currentPage--;
            await this.loadTable();
        }
    }

    async nextPage() {
        this.currentPage++;
        await this.loadTable();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ConfluenceDashboard();
}); 