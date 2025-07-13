// Feed data and functionality
class FeedManager {
    constructor() {
        this.feedItems = [
            {
                id: 1,
                type: 'commit',
                title: 'Updated README.md with installation instructions',
                description: 'Added comprehensive setup guide and troubleshooting section',
                repository: 'awesome-portfolio',
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
                icon: 'fas fa-code-commit'
            },
            {
                id: 2,
                type: 'issue',
                title: 'Bug: Navigation menu not responsive on mobile',
                description: 'The navigation menu overlaps content on devices smaller than 768px',
                repository: 'react-dashboard',
                timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000), // 5 hours ago
                icon: 'fas fa-exclamation-circle'
            },
            {
                id: 3,
                type: 'pr',
                title: 'Feature: Add dark mode toggle',
                description: 'Implemented dark mode with persistent user preference storage',
                repository: 'portfolio-website',
                timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000), // 8 hours ago
                icon: 'fas fa-code-merge'
            },
            {
                id: 4,
                type: 'commit',
                title: 'Refactored authentication logic',
                description: 'Improved security and error handling in user authentication flow',
                repository: 'chat-application',
                timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000), // 12 hours ago
                icon: 'fas fa-code-commit'
            },
            {
                id: 5,
                type: 'issue',
                title: 'Feature Request: Add export functionality',
                description: 'Users should be able to export data visualizations as PNG/SVG',
                repository: 'data-visualization-tool',
                timestamp: new Date(Date.now() - 18 * 60 * 60 * 1000), // 18 hours ago
                icon: 'fas fa-lightbulb'
            },
            {
                id: 6,
                type: 'pr',
                title: 'Performance: Optimize database queries',
                description: 'Reduced query execution time by 40% through indexing and optimization',
                repository: 'e-commerce-dashboard',
                timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
                icon: 'fas fa-code-merge'
            },
            {
                id: 7,
                type: 'commit',
                title: 'Added unit tests for utility functions',
                description: 'Increased test coverage to 85% with comprehensive unit tests',
                repository: 'task-management-system',
                timestamp: new Date(Date.now() - 36 * 60 * 60 * 1000), // 1.5 days ago
                icon: 'fas fa-code-commit'
            },
            {
                id: 8,
                type: 'issue',
                title: 'Bug: Memory leak in chart rendering',
                description: 'Charts are not properly cleaned up when switching between views',
                repository: 'weather-app',
                timestamp: new Date(Date.now() - 48 * 60 * 60 * 1000), // 2 days ago
                icon: 'fas fa-bug'
            }
        ];
        
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.renderFeed();
        this.bindFilterEvents();
        this.startLiveUpdates();
    }

    renderFeed(filter = 'all') {
        const feedTimeline = document.getElementById('feedTimeline');
        if (!feedTimeline) return;

        const filteredItems = filter === 'all' 
            ? this.feedItems 
            : this.feedItems.filter(item => this.getFilterType(item.type) === filter);

        feedTimeline.innerHTML = '';

        filteredItems.forEach(item => {
            const feedItem = this.createFeedItem(item);
            feedTimeline.appendChild(feedItem);
        });

        // Trigger animation observer for new elements
        if (window.animationObserver) {
            const newItems = feedTimeline.querySelectorAll('.feed-item');
            newItems.forEach(item => {
                item.style.opacity = '0';
                item.style.transform = 'translateY(20px)';
                window.animationObserver.observer.observe(item);
            });
        }
    }

    getFilterType(itemType) {
        const typeMap = {
            'commit': 'commits',
            'issue': 'issues',
            'pr': 'prs'
        };
        return typeMap[itemType] || itemType;
    }

    createFeedItem(item) {
        const feedItem = document.createElement('div');
        feedItem.className = 'feed-item';
        feedItem.dataset.type = item.type;

        const iconClass = this.getIconClass(item.type);
        const timeAgo = this.formatTimestamp(item.timestamp);

        feedItem.innerHTML = `
            <div class="feed-icon ${item.type}">
                <i class="${iconClass}"></i>
            </div>
            <div class="feed-content">
                <h3>${item.title}</h3>
                <p>${item.description}</p>
                <div class="feed-meta">
                    <a href="#" class="feed-repo">${item.repository}</a>
                    <span> • ${timeAgo}</span>
                </div>
            </div>
        `;

        // Add click interaction
        feedItem.addEventListener('click', () => {
            this.handleFeedItemClick(item);
        });

        return feedItem;
    }

    getIconClass(type) {
        const iconMap = {
            'commit': 'fas fa-code-commit',
            'issue': 'fas fa-exclamation-circle',
            'pr': 'fas fa-code-merge'
        };
        return iconMap[type] || 'fas fa-circle';
    }

    formatTimestamp(timestamp) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - timestamp) / 1000);
        
        if (diffInSeconds < 60) {
            return 'just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days} day${days !== 1 ? 's' : ''} ago`;
        }
    }

    bindFilterEvents() {
        const filterButtons = document.querySelectorAll('.feed-filters .filter-btn');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const filter = e.target.dataset.filter;
                this.setActiveFilter(filter);
                this.renderFeed(filter);
            });
        });
    }

    setActiveFilter(filter) {
        this.currentFilter = filter;
        
        const filterButtons = document.querySelectorAll('.feed-filters .filter-btn');
        filterButtons.forEach(button => {
            button.classList.remove('active');
            if (button.dataset.filter === filter) {
                button.classList.add('active');
            }
        });
    }

    handleFeedItemClick(item) {
        // Simulate opening item details or navigating to repository
        console.log(`Opening ${item.type}: ${item.title}`);
        
        // You could implement a modal or navigate to a detail view here
        // For now, we'll just show an alert
        const message = `${item.type.toUpperCase()}: ${item.title}\n\nRepository: ${item.repository}\nTime: ${this.formatTimestamp(item.timestamp)}`;
        alert(message);
    }

    addFeedItem(itemData) {
        const newItem = {
            id: this.feedItems.length + 1,
            timestamp: new Date(),
            ...itemData
        };
        
        this.feedItems.unshift(newItem); // Add to beginning
        this.renderFeed(this.currentFilter);
    }

    startLiveUpdates() {
        // Simulate live updates every 30 seconds
        setInterval(() => {
            if (Math.random() > 0.7) { // 30% chance of new activity
                this.simulateNewActivity();
            }
        }, 30000);
    }

    simulateNewActivity() {
        const activityTypes = ['commit', 'issue', 'pr'];
        const repositories = ['awesome-portfolio', 'react-dashboard', 'chat-application', 'weather-app'];
        
        const activities = {
            commit: [
                'Fixed minor styling issues',
                'Updated dependencies',
                'Improved error handling',
                'Added new utility function',
                'Optimized performance'
            ],
            issue: [
                'Bug: Button not responding on click',
                'Feature: Add search functionality',
                'Enhancement: Improve loading times',
                'Bug: Form validation not working',
                'Feature: Add keyboard shortcuts'
            ],
            pr: [
                'Feature: Add user preferences',
                'Fix: Resolve mobile layout issues',
                'Enhancement: Improve accessibility',
                'Feature: Add data export',
                'Fix: Memory leak in component'
            ]
        };

        const type = activityTypes[Math.floor(Math.random() * activityTypes.length)];
        const repo = repositories[Math.floor(Math.random() * repositories.length)];
        const titles = activities[type];
        const title = titles[Math.floor(Math.random() * titles.length)];

        this.addFeedItem({
            type,
            title,
            description: `Recent activity in ${repo}`,
            repository: repo,
            icon: this.getIconClass(type)
        });
    }
}

// Initialize feed when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.feedManager = new FeedManager();
});

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FeedManager;
}