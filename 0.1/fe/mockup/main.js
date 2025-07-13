// Navigation functionality
class Navigation {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.setActiveSection('profile');
    }

    bindEvents() {
        const navButtons = document.querySelectorAll('.nav-btn');
        
        navButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const sectionName = e.currentTarget.dataset.section;
                this.setActiveSection(sectionName);
                this.setActiveNavButton(e.currentTarget);
            });
        });
    }

    setActiveSection(sectionName) {
        // Hide all sections
        const sections = document.querySelectorAll('.section');
        sections.forEach(section => {
            section.classList.remove('active');
        });

        // Show target section
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Update URL without page reload
        history.pushState(null, null, `#${sectionName}`);
    }

    setActiveNavButton(activeButton) {
        // Remove active class from all nav buttons
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(button => {
            button.classList.remove('active');
        });

        // Add active class to clicked button
        activeButton.classList.add('active');
    }
}

// Smooth scrolling utility
class SmoothScroll {
    static scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
}

// Intersection Observer for animations
class AnimationObserver {
    constructor() {
        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            }
        );
        
        this.init();
    }

    init() {
        const animatedElements = document.querySelectorAll(
            '.repo-card, .project-card, .feed-item, .profile-card'
        );
        
        animatedElements.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            this.observer.observe(element);
        });
    }

    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                this.observer.unobserve(entry.target);
            }
        });
    }
}

// URL routing
class Router {
    constructor() {
        this.init();
    }

    init() {
        // Handle initial load
        this.handleRoute();
        
        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.handleRoute();
        });
    }

    handleRoute() {
        const hash = window.location.hash.substring(1);
        const validSections = ['profile', 'projects', 'feed'];
        const section = validSections.includes(hash) ? hash : 'profile';
        
        // Update active section
        const navigation = new Navigation();
        navigation.setActiveSection(section);
        
        // Update active nav button
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(button => {
            button.classList.remove('active');
            if (button.dataset.section === section) {
                button.classList.add('active');
            }
        });
    }
}

// Utility functions
class Utils {
    static formatDate(date) {
        const now = new Date();
        const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
        
        if (diffInHours < 1) {
            return 'just now';
        } else if (diffInHours < 24) {
            return `${diffInHours} hours ago`;
        } else if (diffInHours < 48) {
            return 'yesterday';
        } else {
            const diffInDays = Math.floor(diffInHours / 24);
            return `${diffInDays} days ago`;
        }
    }

    static generateRandomColor() {
        const colors = [
            '#f1e05a', // JavaScript
            '#61dafb', // React
            '#3572a5', // Python
            '#e34c26', // HTML
            '#1572b6', // CSS
            '#f7df1e', // Node.js
            '#563d7c', // Bootstrap
            '#ff6b6b', // Ruby
            '#4f5d95', // PHP
            '#89e051'  // C#
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    static truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    new Router();
    new Navigation();
    new AnimationObserver();
    
    // Add click handlers for smooth scrolling
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

    // Add loading animation
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Navigation, SmoothScroll, AnimationObserver, Router, Utils };
}