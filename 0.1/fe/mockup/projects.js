// Projects data and functionality
class ProjectsManager {
    constructor() {
        this.projects = [
            {
                id: 1,
                name: 'E-Commerce Dashboard',
                thoughts: ['Database Optimization Strategies'],
                technologies: ['React', 'Node.js', 'MongoDB', 'Socket.io'],
                category: 'react',
                githubUrl: '#',
                liveUrl: '#',
                stars: 234,
                forks: 45
            },
            {
                id: 2,
                name: 'Weather App',
                thoughts: ['Mobile-First Design'],
                technologies: ['JavaScript', 'CSS3', 'Weather API'],
                category: 'javascript',
                githubUrl: '#',
                liveUrl: '#',
                stars: 156,
                forks: 23
            },
            {
                id: 3,
                name: 'Task Management System',
                thoughts: ['API Design Principles'],
                technologies: ['Python', 'Django', 'PostgreSQL', 'Redis'],
                category: 'python',
                githubUrl: '#',
                liveUrl: '#',
                stars: 189,
                forks: 34
            },
            {
                id: 4,
                name: 'Portfolio Website',
                thoughts: ['CSS Grid vs Flexbox'],
                technologies: ['HTML5', 'CSS3', 'JavaScript', 'GSAP'],
                category: 'javascript',
                githubUrl: '#',
                liveUrl: '#',
                stars: 87,
                forks: 12
            },
            {
                id: 5,
                name: 'Chat Application',
                thoughts: ['JavaScript Async Patterns'],
                technologies: ['React', 'Socket.io', 'Express', 'MongoDB'],
                category: 'react',
                githubUrl: '#',
                liveUrl: '#',
                stars: 298,
                forks: 67
            },
            {
                id: 6,
                name: 'Data Visualization Tool',
                thoughts: ['Performance Optimization'],
                technologies: ['Python', 'Flask', 'D3.js', 'Pandas'],
                category: 'python',
                githubUrl: '#',
                liveUrl: '#',
                stars: 145,
                forks: 28
            }
        ];
        
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.renderProjects();
        this.bindFilterEvents();
    }

    renderProjects(filter = 'all') {
        const projectsGrid = document.getElementById('projectsGrid');
        if (!projectsGrid) return;

        const filteredProjects = filter === 'all' 
            ? this.projects 
            : this.projects.filter(project => project.category === filter);

        projectsGrid.innerHTML = '';

        filteredProjects.forEach(project => {
            const projectCard = this.createProjectCard(project);
            projectsGrid.appendChild(projectCard);
        });

        // Trigger animation observer for new elements
        if (window.animationObserver) {
            const newCards = projectsGrid.querySelectorAll('.project-card');
            newCards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                window.animationObserver.observer.observe(card);
            });
        }
    }

    createProjectCard(project) {
        const card = document.createElement('div');
        card.className = 'project-card';
        card.dataset.category = project.category;

        const techTags = project.technologies.map(tech => 
            `<span class="tech-tag">${tech}</span>`
        ).join('');

        const thoughtsLinks = project.thoughts.map(thought => 
            `<span class="thought-link">${thought}</span>`
        ).join('');
        card.innerHTML = `
            <h3>${project.name}</h3>
            <div class="project-thoughts">
                <span class="thoughts-label">Related thoughts:</span>
                <div class="thoughts-list">
                    ${thoughtsLinks}
                </div>
            </div>
            <div class="project-tech">
                ${techTags}
            </div>
            <div class="project-links">
                <a href="${project.githubUrl}" class="project-link" target="_blank">
                    <i class="fab fa-github"></i>
                    Code
                </a>
                <a href="${project.liveUrl}" class="project-link" target="_blank">
                    <i class="fas fa-external-link-alt"></i>
                    Live Demo
                </a>
            </div>
            <div class="project-stats">
                <span class="stat">
                    <i class="fas fa-star"></i> ${project.stars}
                </span>
                <span class="stat">
                    <i class="fas fa-code-branch"></i> ${project.forks}
                </span>
            </div>
        `;

        // Add hover effects
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });

        // Add click handler to navigate to project detail
        const projectTitle = card.querySelector('h3');
        projectTitle.style.cursor = 'pointer';
        projectTitle.addEventListener('click', (e) => {
            e.preventDefault();
            const projectName = project.name.toLowerCase().replace(/\s+/g, '-');
            this.navigateToProject(projectName);
        });
        return card;
    }

    bindFilterEvents() {
        const filterButtons = document.querySelectorAll('.projects-filters .filter-btn');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const filter = e.target.dataset.filter;
                this.setActiveFilter(filter);
                this.renderProjects(filter);
            });
        });
    }

    setActiveFilter(filter) {
        this.currentFilter = filter;
        
        const filterButtons = document.querySelectorAll('.projects-filters .filter-btn');
        filterButtons.forEach(button => {
            button.classList.remove('active');
            if (button.dataset.filter === filter) {
                button.classList.add('active');
            }
        });
    }

    addProject(projectData) {
        const newProject = {
            id: this.projects.length + 1,
            ...projectData
        };
        this.projects.push(newProject);
        this.renderProjects(this.currentFilter);
    }

    removeProject(projectId) {
        this.projects = this.projects.filter(project => project.id !== projectId);
        this.renderProjects(this.currentFilter);
    }

    updateProject(projectId, updatedData) {
        const projectIndex = this.projects.findIndex(project => project.id === projectId);
        if (projectIndex !== -1) {
            this.projects[projectIndex] = { ...this.projects[projectIndex], ...updatedData };
            this.renderProjects(this.currentFilter);
        }
    }

    highlightRepository(repositoryName) {
        // Find and highlight the repository card
        setTimeout(() => {
            const projectCards = document.querySelectorAll('.project-card');
            projectCards.forEach(card => {
                const projectName = card.querySelector('h3').textContent.toLowerCase().replace(/\s+/g, '-');
                if (projectName === repositoryName) {
                    // Scroll to the card
                    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    
                    // Add highlight effect
                    card.style.borderColor = 'var(--accent-blue)';
                    card.style.boxShadow = '0 0 20px rgba(88, 166, 255, 0.3)';
                    
                    // Remove highlight after 3 seconds
                    setTimeout(() => {
                        card.style.borderColor = 'var(--border-color)';
                        card.style.boxShadow = 'none';
                    }, 3000);
                }
            });
        }, 100);
    }

    navigateToProject(projectName) {
        // Navigate to project detail page
        const newUrl = `${window.location.pathname}?project=${projectName}`;
        window.location.href = newUrl;
    }
}

// Initialize projects when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.projectsManager = new ProjectsManager();
});

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProjectsManager;
}