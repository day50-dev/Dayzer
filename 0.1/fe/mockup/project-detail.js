// Project detail page for conversation-based projects
class ProjectDetailManager {
    constructor() {
        this.currentProject = null;
        this.conversations = [];
        this.contributors = [];
        this.init();
    }

    init() {
        // Check if we're on a project detail page
        const urlParams = new URLSearchParams(window.location.search);
        const projectName = urlParams.get('project');
        
        if (projectName) {
            this.loadProject(projectName);
        }
        
        this.bindEvents();
    }

    loadProject(projectName) {
        // Mock project data - in real app this would come from API
        const projectData = {
            'react-dashboard': {
                name: 'React Dashboard',
                description: 'Collaborative conversations about building modern admin dashboards with React and TypeScript',
                topics: ['react', 'typescript', 'dashboard', 'ui-components'],
                stars: 234,
                forks: 45,
                watchers: 89,
                lastUpdated: new Date(Date.now() - 2 * 60 * 60 * 1000),
                contributors: [
                    {
                        id: 1,
                        username: 'alexdev',
                        avatar: 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=100',
                        contributions: 15
                    },
                    {
                        id: 2,
                        username: 'sarah_codes',
                        avatar: 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?auto=compress&cs=tinysrgb&w=100',
                        contributions: 8
                    },
                    {
                        id: 3,
                        username: 'mike_dev',
                        avatar: 'https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?auto=compress&cs=tinysrgb&w=100',
                        contributions: 12
                    }
                ],
                conversations: [
                    {
                        id: 1,
                        title: 'Component Architecture Discussion',
                        participants: ['alexdev', 'sarah_codes'],
                        lastMessage: 'Great point about using compound components for the data table...',
                        messageCount: 24,
                        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
                        category: 'architecture'
                    },
                    {
                        id: 2,
                        title: 'State Management Patterns',
                        participants: ['alexdev', 'mike_dev'],
                        lastMessage: 'I think we should consider using Zustand instead of Redux for this...',
                        messageCount: 18,
                        timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
                        category: 'state-management'
                    },
                    {
                        id: 3,
                        title: 'TypeScript Best Practices',
                        participants: ['sarah_codes', 'mike_dev', 'alexdev'],
                        lastMessage: 'The generic constraints approach works well for the API layer...',
                        messageCount: 31,
                        timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000),
                        category: 'typescript'
                    },
                    {
                        id: 4,
                        title: 'Performance Optimization Strategies',
                        participants: ['alexdev', 'sarah_codes'],
                        lastMessage: 'Virtual scrolling definitely improved the table performance...',
                        messageCount: 15,
                        timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000),
                        category: 'performance'
                    },
                    {
                        id: 5,
                        title: 'Testing Component Interactions',
                        participants: ['mike_dev'],
                        lastMessage: 'The React Testing Library approach is much cleaner...',
                        messageCount: 9,
                        timestamp: new Date(Date.now() - 18 * 60 * 60 * 1000),
                        category: 'testing'
                    }
                ]
            },
            'weather-app': {
                name: 'Weather App',
                description: 'Conversations about building a responsive weather application with modern web technologies',
                topics: ['javascript', 'api', 'responsive-design', 'pwa'],
                stars: 156,
                forks: 23,
                watchers: 67,
                lastUpdated: new Date(Date.now() - 18 * 60 * 60 * 1000),
                contributors: [
                    {
                        id: 1,
                        username: 'alexdev',
                        avatar: 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=100',
                        contributions: 12
                    },
                    {
                        id: 4,
                        username: 'jenny_ui',
                        avatar: 'https://images.pexels.com/photos/733872/pexels-photo-733872.jpeg?auto=compress&cs=tinysrgb&w=100',
                        contributions: 6
                    }
                ],
                conversations: [
                    {
                        id: 1,
                        title: 'Mobile-First Design Approach',
                        participants: ['alexdev', 'jenny_ui'],
                        lastMessage: 'The progressive enhancement strategy works perfectly here...',
                        messageCount: 16,
                        timestamp: new Date(Date.now() - 18 * 60 * 60 * 1000),
                        category: 'design'
                    },
                    {
                        id: 2,
                        title: 'Weather API Integration',
                        participants: ['alexdev'],
                        lastMessage: 'Error handling for API timeouts is crucial for UX...',
                        messageCount: 11,
                        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
                        category: 'api'
                    }
                ]
            }
        };

        this.currentProject = projectData[projectName];
        if (this.currentProject) {
            this.renderProjectPage();
        }
    }

    renderProjectPage() {
        const main = document.querySelector('.main .container');
        main.innerHTML = `
            <div class="project-detail">
                <div class="project-header">
                    <div class="project-nav">
                        <a href="#profile" class="back-link">
                            <i class="fas fa-arrow-left"></i>
                            Back to Profile
                        </a>
                    </div>
                    
                    <div class="project-title-section">
                        <div class="project-title">
                            <h1>${this.currentProject.name}</h1>
                            <div class="project-visibility">
                                <i class="fas fa-lock-open"></i>
                                Public
                            </div>
                        </div>
                        
                        <div class="project-actions">
                            <button class="action-btn">
                                <i class="fas fa-eye"></i>
                                Watch
                                <span class="count">${this.currentProject.watchers}</span>
                            </button>
                            <button class="action-btn">
                                <i class="fas fa-star"></i>
                                Star
                                <span class="count">${this.currentProject.stars}</span>
                            </button>
                            <button class="action-btn">
                                <i class="fas fa-code-branch"></i>
                                Fork
                                <span class="count">${this.currentProject.forks}</span>
                            </button>
                        </div>
                    </div>
                    
                    <p class="project-description">${this.currentProject.description}</p>
                    
                    <div class="project-topics">
                        ${this.currentProject.topics.map(topic => 
                            `<span class="topic-tag">${topic}</span>`
                        ).join('')}
                    </div>
                </div>

                <div class="project-content">
                    <div class="project-main">
                        <div class="conversations-section">
                            <div class="conversations-header">
                                <h2>
                                    <i class="fas fa-comments"></i>
                                    Conversations
                                    <span class="count">${this.currentProject.conversations.length}</span>
                                </h2>
                                <button class="new-conversation-btn">
                                    <i class="fas fa-plus"></i>
                                    New Conversation
                                </button>
                            </div>
                            
                            <div class="conversations-list" id="conversationsList">
                                ${this.renderConversations()}
                            </div>
                        </div>
                    </div>
                    
                    <div class="project-sidebar">
                        <div class="contributors-section">
                            <h3>Contributors</h3>
                            <div class="contributors-list">
                                ${this.renderContributors()}
                            </div>
                        </div>
                        
                        <div class="project-stats">
                            <div class="stat-item">
                                <span class="stat-label">Total Conversations</span>
                                <span class="stat-value">${this.currentProject.conversations.length}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Total Messages</span>
                                <span class="stat-value">${this.getTotalMessages()}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Last Updated</span>
                                <span class="stat-value">${this.formatTimestamp(this.currentProject.lastUpdated)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.bindProjectEvents();
    }

    renderConversations() {
        return this.currentProject.conversations.map(conversation => `
            <div class="conversation-item" data-id="${conversation.id}">
                <div class="conversation-icon">
                    <i class="fas fa-comment-dots"></i>
                </div>
                <div class="conversation-content">
                    <div class="conversation-header">
                        <h3 class="conversation-title">${conversation.title}</h3>
                        <span class="conversation-category ${conversation.category}">${conversation.category}</span>
                    </div>
                    <div class="conversation-meta">
                        <div class="participants">
                            ${conversation.participants.map(participant => `
                                <span class="participant">@${participant}</span>
                            `).join('')}
                        </div>
                        <span class="message-count">${conversation.messageCount} messages</span>
                    </div>
                    <p class="last-message">${conversation.lastMessage}</p>
                    <div class="conversation-footer">
                        <span class="timestamp">${this.formatTimestamp(conversation.timestamp)}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderContributors() {
        return this.currentProject.contributors.map(contributor => `
            <div class="contributor-item">
                <img src="${contributor.avatar}" alt="${contributor.username}" class="contributor-avatar">
                <div class="contributor-info">
                    <span class="contributor-name">@${contributor.username}</span>
                    <span class="contribution-count">${contributor.contributions} contributions</span>
                </div>
            </div>
        `).join('');
    }

    getTotalMessages() {
        return this.currentProject.conversations.reduce((total, conv) => total + conv.messageCount, 0);
    }

    formatTimestamp(timestamp) {
        const now = new Date();
        const diffInHours = Math.floor((now - timestamp) / (1000 * 60 * 60));
        
        if (diffInHours < 1) {
            return 'just now';
        } else if (diffInHours < 24) {
            return `${diffInHours} hours ago`;
        } else {
            const diffInDays = Math.floor(diffInHours / 24);
            return `${diffInDays} days ago`;
        }
    }

    bindEvents() {
        // Handle navigation from projects page
        document.addEventListener('click', (e) => {
            if (e.target.closest('.project-card h3')) {
                e.preventDefault();
                const projectName = e.target.textContent.toLowerCase().replace(/\s+/g, '-');
                this.navigateToProject(projectName);
            }
        });
    }

    bindProjectEvents() {
        // Back navigation
        const backLink = document.querySelector('.back-link');
        if (backLink) {
            backLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateBack();
            });
        }

        // Conversation clicks
        const conversationItems = document.querySelectorAll('.conversation-item');
        conversationItems.forEach(item => {
            item.addEventListener('click', () => {
                const conversationId = item.dataset.id;
                this.openConversation(conversationId);
            });
        });

        // New conversation button
        const newConversationBtn = document.querySelector('.new-conversation-btn');
        if (newConversationBtn) {
            newConversationBtn.addEventListener('click', () => {
                this.createNewConversation();
            });
        }

        // Action buttons
        const actionBtns = document.querySelectorAll('.action-btn');
        actionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = btn.querySelector('i').classList.contains('fa-star') ? 'star' : 
                              btn.querySelector('i').classList.contains('fa-eye') ? 'watch' : 'fork';
                this.handleAction(action, btn);
            });
        });
    }

    navigateToProject(projectName) {
        // Update URL
        const newUrl = `${window.location.pathname}?project=${projectName}`;
        history.pushState({ project: projectName }, '', newUrl);
        
        // Load project
        this.loadProject(projectName);
    }

    navigateBack() {
        // Remove project parameter and go back to profile
        history.pushState(null, '', window.location.pathname);
        
        // Restore original page
        location.reload();
    }

    openConversation(conversationId) {
        const conversation = this.currentProject.conversations.find(c => c.id == conversationId);
        if (conversation) {
            alert(`Opening conversation: ${conversation.title}\n\nParticipants: ${conversation.participants.join(', ')}\nMessages: ${conversation.messageCount}\n\nLast message: ${conversation.lastMessage}`);
        }
    }

    createNewConversation() {
        const title = prompt('Enter conversation title:');
        if (title) {
            const newConversation = {
                id: this.currentProject.conversations.length + 1,
                title: title,
                participants: ['alexdev'],
                lastMessage: 'Conversation started...',
                messageCount: 1,
                timestamp: new Date(),
                category: 'general'
            };
            
            this.currentProject.conversations.unshift(newConversation);
            
            // Re-render conversations
            const conversationsList = document.getElementById('conversationsList');
            conversationsList.innerHTML = this.renderConversations();
            this.bindProjectEvents();
        }
    }

    handleAction(action, button) {
        const countSpan = button.querySelector('.count');
        let currentCount = parseInt(countSpan.textContent);
        
        // Toggle action
        if (button.classList.contains('active')) {
            button.classList.remove('active');
            countSpan.textContent = currentCount - 1;
        } else {
            button.classList.add('active');
            countSpan.textContent = currentCount + 1;
        }
        
        console.log(`${action} action toggled`);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.projectDetailManager = new ProjectDetailManager();
});

// Handle browser navigation
window.addEventListener('popstate', (e) => {
    if (e.state && e.state.project) {
        window.projectDetailManager.loadProject(e.state.project);
    } else {
        location.reload();
    }
});

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProjectDetailManager;
}