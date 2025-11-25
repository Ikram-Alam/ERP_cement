/**
 * CemERP Dashboard - JavaScript for Interactive Features
 * Component-based approach using modern ES6+ syntax
 */

// ========================================
// Sidebar Controller Class
// ========================================
class SidebarController {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.mobileToggle = document.getElementById('mobileToggle');
        this.mainContent = document.querySelector('.main-content');
        
        this.init();
    }
    
    init() {
        // Desktop sidebar toggle
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }
        
        // Mobile sidebar toggle
        if (this.mobileToggle) {
            this.mobileToggle.addEventListener('click', () => this.toggleMobileSidebar());
        }
        
        // Close mobile sidebar when clicking outside
        document.addEventListener('click', (e) => this.handleOutsideClick(e));
        
        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());
    }
    
    toggleSidebar() {
        this.sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', this.sidebar.classList.contains('collapsed'));
    }
    
    toggleMobileSidebar() {
        this.sidebar.classList.toggle('mobile-open');
    }
    
    handleOutsideClick(e) {
        if (window.innerWidth <= 768) {
            if (!this.sidebar.contains(e.target) && 
                !this.mobileToggle.contains(e.target) &&
                this.sidebar.classList.contains('mobile-open')) {
                this.sidebar.classList.remove('mobile-open');
            }
        }
    }
    
    handleResize() {
        if (window.innerWidth > 768) {
            this.sidebar.classList.remove('mobile-open');
        }
    }
    
    // Restore sidebar state from localStorage
    restoreState() {
        const collapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (collapsed && window.innerWidth > 768) {
            this.sidebar.classList.add('collapsed');
        }
    }
}

// ========================================
// Stats Card Animation Class
// ========================================
class StatsAnimator {
    constructor() {
        this.statCards = document.querySelectorAll('.stat-card');
        this.init();
    }
    
    init() {
        this.observeCards();
    }
    
    observeCards() {
        const options = {
            threshold: 0.2,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, options);
        
        this.statCards.forEach(card => {
            observer.observe(card);
        });
    }
    
    animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = end > start ? 1 : -1;
        const stepTime = Math.abs(Math.floor(duration / range));
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            element.textContent = current;
            if (current === end) {
                clearInterval(timer);
            }
        }, stepTime);
    }
}

// ========================================
// Search Functionality Class
// ========================================
class SearchHandler {
    constructor() {
        this.searchInput = document.querySelector('.search-box input');
        this.init();
    }
    
    init() {
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => this.handleSearch(e));
            this.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.executeSearch(e.target.value);
                }
            });
        }
    }
    
    handleSearch(e) {
        const query = e.target.value.trim();
        if (query.length > 2) {
            // Implement search logic here
            console.log('Searching for:', query);
        }
    }
    
    executeSearch(query) {
        if (query.trim()) {
            console.log('Execute search:', query);
            // Redirect to search results or filter current page
        }
    }
}

// ========================================
// Notification Handler Class
// ========================================
class NotificationHandler {
    constructor() {
        this.notificationBtn = document.querySelector('.notification-btn');
        this.init();
    }
    
    init() {
        if (this.notificationBtn) {
            this.notificationBtn.addEventListener('click', () => this.showNotifications());
        }
    }
    
    showNotifications() {
        // For now, just log - will implement dropdown in next phase
        console.log('Show notifications');
        // TODO: Create and show notification dropdown
    }
}

// ========================================
// Chart Filter Handler Class
// ========================================
class ChartFilterHandler {
    constructor() {
        this.filterButtons = document.querySelectorAll('.filter-btn');
        this.init();
    }
    
    init() {
        this.filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleFilterClick(e));
        });
    }
    
    handleFilterClick(e) {
        // Remove active class from all buttons
        this.filterButtons.forEach(btn => btn.classList.remove('active'));
        
        // Add active class to clicked button
        e.target.classList.add('active');
        
        // Filter chart data based on selected period
        const period = e.target.textContent.toLowerCase();
        console.log('Filter chart by:', period);
        // TODO: Update chart data based on selected period
    }
}

// ========================================
// Dashboard Data Refresher Class
// ========================================
class DashboardRefresher {
    constructor(interval = 60000) { // Default: refresh every 60 seconds
        this.interval = interval;
        this.timer = null;
    }
    
    start() {
        this.timer = setInterval(() => {
            this.refreshData();
        }, this.interval);
    }
    
    stop() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }
    
    async refreshData() {
        console.log('Refreshing dashboard data...');
        // TODO: Implement AJAX call to fetch updated data
        // Example:
        // const response = await fetch('/api/dashboard/stats/');
        // const data = await response.json();
        // this.updateUI(data);
    }
    
    updateUI(data) {
        // Update stat cards, alerts, etc. with new data
        console.log('Updating UI with:', data);
    }
}

// ========================================
// Utility Functions
// ========================================
const Utils = {
    // Format numbers with commas
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    
    // Format currency
    formatCurrency(amount, symbol = '₹') {
        return `${symbol}${this.formatNumber(amount)}`;
    },
    
    // Get relative time
    getRelativeTime(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diff = Math.floor((now - time) / 1000); // difference in seconds
        
        if (diff < 60) return 'just now';
        if (diff < 3600) return `${Math.floor(diff / 60)} mins ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
        return `${Math.floor(diff / 86400)} days ago`;
    },
    
    // Show toast notification
    showToast(message, type = 'info') {
        // TODO: Implement toast notification
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
};

// ========================================
// Initialize Dashboard
// ========================================
class DashboardApp {
    constructor() {
        this.sidebarController = null;
        this.statsAnimator = null;
        this.searchHandler = null;
        this.notificationHandler = null;
        this.chartFilterHandler = null;
        this.refresher = null;
    }
    
    init() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
        } else {
            this.initializeComponents();
        }
    }
    
    initializeComponents() {
        // Initialize all components
        this.sidebarController = new SidebarController();
        this.statsAnimator = new StatsAnimator();
        this.searchHandler = new SearchHandler();
        this.notificationHandler = new NotificationHandler();
        this.chartFilterHandler = new ChartFilterHandler();
        
        // Restore sidebar state
        this.sidebarController.restoreState();
        
        // Start auto-refresh (optional - uncomment if needed)
        // this.refresher = new DashboardRefresher(60000);
        // this.refresher.start();
        
        // Add smooth scroll behavior
        this.enableSmoothScroll();
        
        // Log initialization
        console.log('✅ CemERP Dashboard initialized successfully');
    }
    
    enableSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// ========================================
// Start the Application
// ========================================
const app = new DashboardApp();
app.init();

// Export for use in other modules (if using module system)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DashboardApp,
        SidebarController,
        StatsAnimator,
        SearchHandler,
        NotificationHandler,
        ChartFilterHandler,
        DashboardRefresher,
        Utils
    };
}
