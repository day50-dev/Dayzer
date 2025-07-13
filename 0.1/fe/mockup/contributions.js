// Contributions grid functionality
class ContributionsManager {
    constructor() {
        this.contributions = this.generateContributionData();
        this.init();
    }

    init() {
        this.renderContributionsGrid();
        this.addTooltips();
    }

    generateContributionData() {
        const contributions = [];
        const today = new Date();
        const startDate = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());
        
        // Generate 365 days of contribution data
        for (let i = 0; i < 365; i++) {
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);
            
            // Generate random contribution count with realistic patterns
            let count = 0;
            const dayOfWeek = date.getDay();
            
            // Weekend pattern (less activity)
            if (dayOfWeek === 0 || dayOfWeek === 6) {
                count = Math.random() > 0.7 ? Math.floor(Math.random() * 3) : 0;
            } else {
                // Weekday pattern (more activity)
                count = Math.random() > 0.3 ? Math.floor(Math.random() * 8) : 0;
            }
            
            // Add some random high-activity days
            if (Math.random() > 0.95) {
                count += Math.floor(Math.random() * 10) + 5;
            }
            
            contributions.push({
                date: new Date(date),
                count: count,
                level: this.getContributionLevel(count)
            });
        }
        
        return contributions;
    }

    getContributionLevel(count) {
        if (count === 0) return 0;
        if (count <= 2) return 1;
        if (count <= 5) return 2;
        if (count <= 8) return 3;
        return 4;
    }

    renderContributionsGrid() {
        const grid = document.getElementById('contributionsGrid');
        if (!grid) return;

        grid.innerHTML = '';

        this.contributions.forEach(contribution => {
            const day = document.createElement('div');
            day.className = `contribution-day level-${contribution.level}`;
            day.dataset.date = contribution.date.toISOString().split('T')[0];
            day.dataset.count = contribution.count;
            day.title = this.formatTooltip(contribution);
            
            grid.appendChild(day);
        });
    }

    formatTooltip(contribution) {
        const dateStr = contribution.date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
        
        const contributionText = contribution.count === 1 
            ? '1 contribution' 
            : `${contribution.count} contributions`;
            
        return `${contributionText} on ${dateStr}`;
    }

    addTooltips() {
        const days = document.querySelectorAll('.contribution-day');
        
        days.forEach(day => {
            day.addEventListener('mouseenter', (e) => {
                this.showTooltip(e);
            });
            
            day.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(event) {
        const tooltip = document.createElement('div');
        tooltip.className = 'contribution-tooltip';
        tooltip.textContent = event.target.title;
        tooltip.style.cssText = `
            position: absolute;
            background: var(--bg-tertiary);
            color: var(--text-primary);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        this.currentTooltip = tooltip;
    }

    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }

    getTotalContributions() {
        return this.contributions.reduce((total, day) => total + day.count, 0);
    }

    getLongestStreak() {
        let currentStreak = 0;
        let longestStreak = 0;
        
        this.contributions.forEach(day => {
            if (day.count > 0) {
                currentStreak++;
                longestStreak = Math.max(longestStreak, currentStreak);
            } else {
                currentStreak = 0;
            }
        });
        
        return longestStreak;
    }

    getCurrentStreak() {
        let streak = 0;
        
        // Start from the most recent day and count backwards
        for (let i = this.contributions.length - 1; i >= 0; i--) {
            if (this.contributions[i].count > 0) {
                streak++;
            } else {
                break;
            }
        }
        
        return streak;
    }

    updateContributionsText() {
        const textElement = document.querySelector('.contributions-count');
        if (textElement) {
            textElement.textContent = this.getTotalContributions().toLocaleString();
        }
    }
}

// Initialize contributions when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.contributionsManager = new ContributionsManager();
    window.contributionsManager.updateContributionsText();
});

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ContributionsManager;
}