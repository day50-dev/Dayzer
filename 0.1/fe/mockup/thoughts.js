// Thoughts/Memories data and functionality
class ThoughtsManager {
    constructor() {
        this.thoughts = [
            {
                id: 1,
                title: 'Building a React Dashboard',
                snippet: 'Discussed implementing a modern admin dashboard with TypeScript, focusing on component architecture and state management patterns...',
                repository: 'react-dashboard',
                timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000), // 2 days ago
                conversationLength: 'Long',
                category: 'development'
            },
            {
                id: 2,
                title: 'CSS Grid vs Flexbox',
                snippet: 'Deep dive into when to use CSS Grid versus Flexbox for different layout scenarios. Covered responsive design patterns...',
                repository: 'awesome-portfolio',
                timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000), // 5 days ago
                conversationLength: 'Medium',
                category: 'design'
            },
            {
                id: 3,
                title: 'Database Optimization Strategies',
                snippet: 'Explored various database indexing techniques and query optimization methods for improving application performance...',
                repository: 'e-commerce-dashboard',
                timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 1 week ago
                conversationLength: 'Long',
                category: 'backend'
            },
            {
                id: 4,
                title: 'JavaScript Async Patterns',
                snippet: 'Covered promises, async/await, and error handling patterns. Discussed best practices for managing asynchronous operations...',
                repository: 'chat-application',
                timestamp: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000), // 10 days ago
                conversationLength: 'Medium',
                category: 'development'
            },
            {
                id: 5,
                title: 'API Design Principles',
                snippet: 'Discussed RESTful API design, HTTP status codes, and authentication strategies. Covered GraphQL vs REST considerations...',
                repository: 'task-management-system',
                timestamp: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000), // 2 weeks ago
                conversationLength: 'Long',
                category: 'backend'
            },
            {
                id: 6,
                title: 'Mobile-First Design',
                snippet: 'Explored mobile-first responsive design principles and progressive enhancement strategies for better user experience...',
                repository: 'weather-app',
                timestamp: new Date(Date.now() - 18 * 24 * 60 * 60 * 1000), // 18 days ago
                conversationLength: 'Short',
                category: 'design'
            }
        ];
        
        this.init();
    }

    init() {
        this.renderThoughts();
    }

    renderThoughts() {
        const thoughtsGrid = document.getElementById('thoughtsGrid');
        if (!thoughtsGrid) return;

        thoughtsGrid.innerHTML = '';

        this.thoughts.forEach(thought => {
            const thoughtCard = this.createThoughtCard(thought);
            thoughtsGrid.appendChild(thoughtCard);
        });

        // Trigger animation observer for new elements
        if (window.animationObserver) {
            const newCards = thoughtsGrid.querySelectorAll('.thought-card');
            newCards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                window.animationObserver.observer.observe(card);
            });
        }
    }

    createThoughtCard(thought) {
        const card = document.createElement('div');
        card.className = 'thought-card';
        card.dataset.category = thought.category;

        const timeAgo = this.formatTimestamp(thought.timestamp);
        const lengthIcon = this.getLengthIcon(thought.conversationLength);
        const categoryColor = this.getCategoryColor(thought.category);

        card.innerHTML = `
            <div class="thought-header">
                <h3 class="thought-title">${thought.title}</h3>
                <div class="thought-meta">
                    <span class="conversation-length ${thought.conversationLength.toLowerCase()}">
                        ${lengthIcon} ${thought.conversationLength}
                    </span>
                </div>
            </div>
            <p class="thought-snippet">${thought.snippet}</p>
            <div class="thought-repository">
                <a href="#projects" class="repository-link" data-repo="${thought.repository}">
                    <i class="fas fa-folder"></i>
                    ${thought.repository}
                </a>
            </div>
            <div class="thought-footer">
                <span class="thought-category" style="color: ${categoryColor};">
                    <i class="fas fa-circle"></i> ${this.formatCategory(thought.category)}
                </span>
                <span class="thought-time">${timeAgo}</span>
            </div>
        `;

        // Add click interaction
        card.addEventListener('click', () => {
            this.handleThoughtClick(thought);
        });

        // Add repository link click handler
        const repoLink = card.querySelector('.repository-link');
        repoLink.addEventListener('click', (e) => {
            e.stopPropagation();
            this.handleRepositoryClick(thought.repository);
        });

        // Add hover effects
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-2px)';
            card.style.borderColor = 'var(--accent-blue)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.borderColor = 'var(--border-color)';
        });

        return card;
    }

    getLengthIcon(length) {
        const icons = {
            'Short': '<i class="fas fa-comment"></i>',
            'Medium': '<i class="fas fa-comments"></i>',
            'Long': '<i class="fas fa-comment-dots"></i>'
        };
        return icons[length] || '<i class="fas fa-comment"></i>';
    }

    getCategoryColor(category) {
        const colors = {
            'development': 'var(--accent-blue)',
            'design': 'var(--accent-green)',
            'backend': 'var(--accent-orange)',
            'general': 'var(--text-secondary)'
        };
        return colors[category] || 'var(--text-secondary)';
    }

    formatCategory(category) {
        return category.charAt(0).toUpperCase() + category.slice(1);
    }

    formatTimestamp(timestamp) {
        const now = new Date();
        const diffInDays = Math.floor((now - timestamp) / (1000 * 60 * 60 * 24));
        
        if (diffInDays === 0) {
            return 'today';
        } else if (diffInDays === 1) {
            return 'yesterday';
        } else if (diffInDays < 7) {
            return `${diffInDays} days ago`;
        } else if (diffInDays < 30) {
            const weeks = Math.floor(diffInDays / 7);
            return `${weeks} week${weeks !== 1 ? 's' : ''} ago`;
        } else {
            const months = Math.floor(diffInDays / 30);
            return `${months} month${months !== 1 ? 's' : ''} ago`;
        }
    }

    handleThoughtClick(thought) {
        // Simulate opening thought details or resuming conversation
        console.log(`Opening thought: ${thought.title}`);
        
        const message = `💭 ${thought.title}\n\n${thought.snippet}\n\nRepository: ${thought.repository}\nCategory: ${this.formatCategory(thought.category)}\nConversation Length: ${thought.conversationLength}`;
        alert(message);
    }

    handleRepositoryClick(repositoryName) {
        // Navigate to projects section and highlight the repository
        console.log(`Navigating to repository: ${repositoryName}`);
        
        // Switch to projects section
        const projectsNavBtn = document.querySelector('.nav-btn[data-section="projects"]');
        if (projectsNavBtn) {
            projectsNavBtn.click();
        }
        
        // Highlight the repository (we'll implement this in projects.js)
        if (window.projectsManager) {
            window.projectsManager.highlightRepository(repositoryName);
        }
    }

    addThought(thoughtData) {
        const newThought = {
            id: this.thoughts.length + 1,
            timestamp: new Date(),
            ...thoughtData
        };
        
        this.thoughts.unshift(newThought); // Add to beginning
        this.renderThoughts();
    }

    removeThought(thoughtId) {
        this.thoughts = this.thoughts.filter(thought => thought.id !== thoughtId);
        this.renderThoughts();
    }

    searchThoughts(query) {
        const filteredThoughts = this.thoughts.filter(thought => 
            thought.title.toLowerCase().includes(query.toLowerCase()) ||
            thought.snippet.toLowerCase().includes(query.toLowerCase()) ||
            thought.repository.toLowerCase().includes(query.toLowerCase())
        );
        
        return filteredThoughts;
    }
}

// Initialize thoughts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.thoughtsManager = new ThoughtsManager();
});

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThoughtsManager;
}