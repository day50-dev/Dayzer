// Projects data and functionality
class ProjectsManager {
    constructor() {
        this.projects = [
            {
                id: 1,
                name: 'E-Commerce Dashboard',
                description: 'A comprehensive admin dashboard for managing online stores with real-time analytics, inventory management, and order tracking.',
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
                description: 'Beautiful weather application with location-based forecasts, interactive maps, and detailed weather analytics.',
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
                description: 'Collaborative task management platform with team features, time tracking, and project analytics.',
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
                description: 'Modern portfolio website with smooth animations, responsive design, and dynamic content management.',
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
                description: 'Real-time chat application with file sharing, emoji support, and group messaging capabilities.',
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
                description: 'Interactive data visualization platform for creating beautiful charts and dashboards from CSV data.',
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

        card.innerHTML = `
            <h3>${project.name}</h3>
            <p>${project.description}</p>
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
}

// Initialize projects when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.projectsManager = new ProjectsManager();
});

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProjectsManager;
}