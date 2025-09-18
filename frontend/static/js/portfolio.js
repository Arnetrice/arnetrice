// Portfolio functionality

document.addEventListener('DOMContentLoaded', function() {
    // Load featured portfolio items on homepage
    const featuredPortfolio = document.getElementById('featured-portfolio');
    if (featuredPortfolio) {
        loadFeaturedPortfolio();
    }
    
    // Load all portfolio items on portfolio page
    const portfolioGrid = document.getElementById('portfolio-grid');
    if (portfolioGrid) {
        loadAllPortfolio();
    }
    
    // Initialize portfolio filters if they exist
    const portfolioFilters = document.getElementById('portfolio-filters');
    if (portfolioFilters) {
        initPortfolioFilters();
    }
});

async function loadFeaturedPortfolio() {
    const container = document.getElementById('featured-portfolio');
    
    try {
        // Show loading state
        container.innerHTML = '<div class="col-12 text-center"><div class="loading"></div><p class="mt-3">Loading featured projects...</p></div>';
        
        // Fetch featured portfolio items
        const response = await ArnetriceUtils.apiRequest('/api/portfolio/?featured_only=true&limit=3');
        
        if (response && response.length > 0) {
            displayPortfolioItems(response, container);
        } else {
            container.innerHTML = '<div class="col-12 text-center"><p class="text-muted">No featured projects available at the moment.</p></div>';
        }
        
    } catch (error) {
        console.error('Error loading featured portfolio:', error);
        container.innerHTML = '<div class="col-12 text-center"><p class="text-danger">Error loading featured projects. Please try again later.</p></div>';
    }
}

async function loadAllPortfolio() {
    const container = document.getElementById('portfolio-grid');
    
    try {
        // Show loading state
        container.innerHTML = '<div class="col-12 text-center"><div class="loading"></div><p class="mt-3">Loading portfolio...</p></div>';
        
        // Fetch all portfolio items
        const response = await ArnetriceUtils.apiRequest('/api/portfolio/');
        
        if (response && response.length > 0) {
            displayPortfolioItems(response, container);
        } else {
            container.innerHTML = '<div class="col-12 text-center"><p class="text-muted">No portfolio items available at the moment.</p></div>';
        }
        
    } catch (error) {
        console.error('Error loading portfolio:', error);
        container.innerHTML = '<div class="col-12 text-center"><p class="text-danger">Error loading portfolio. Please try again later.</p></div>';
    }
}

function displayPortfolioItems(items, container) {
    container.innerHTML = '';
    
    items.forEach(item => {
        const portfolioCard = createPortfolioCard(item);
        container.appendChild(portfolioCard);
    });
}

function createPortfolioCard(item) {
    const col = document.createElement('div');
    col.className = 'col-lg-4 col-md-6 mb-4';
    
    const card = document.createElement('div');
    card.className = 'card portfolio-item h-100 border-0 shadow-sm';
    
    // Create card content
    card.innerHTML = `
        <div class="position-relative">
            <img src="${item.image_url || '/static/images/placeholder-project.jpg'}" 
                 class="card-img-top" 
                 alt="${item.title}"
                 onerror="this.src='/static/images/placeholder-project.jpg'">
            <div class="portfolio-overlay">
                <div class="text-center text-white">
                    <h5 class="mb-2">${item.title}</h5>
                    <p class="mb-3">${item.description.substring(0, 100)}${item.description.length > 100 ? '...' : ''}</p>
                    <div class="d-flex gap-2 justify-content-center">
                        ${item.project_url ? `<a href="${item.project_url}" target="_blank" class="btn btn-outline-light btn-sm">View Project</a>` : ''}
                        ${item.github_url ? `<a href="${item.github_url}" target="_blank" class="btn btn-outline-light btn-sm">GitHub</a>` : ''}
                    </div>
                </div>
            </div>
        </div>
        <div class="card-body">
            <h5 class="card-title fw-bold">${item.title}</h5>
            <p class="card-text text-muted">${item.description}</p>
            ${item.client ? `<p class="card-text"><small class="text-muted"><strong>Client:</strong> ${item.client}</small></p>` : ''}
            ${item.technologies ? `
                <div class="mb-2">
                    <small class="text-muted"><strong>Technologies:</strong></small>
                    <div class="mt-1">
                        ${item.technologies.split(',').map(tech => 
                            `<span class="badge bg-primary me-1">${tech.trim()}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
        <div class="card-footer bg-transparent border-0">
            <small class="text-muted">${formatDate(item.created_at)}</small>
        </div>
    `;
    
    col.appendChild(card);
    return col;
}

function initPortfolioFilters() {
    const filterButtons = document.querySelectorAll('[data-filter]');
    const portfolioItems = document.querySelectorAll('.portfolio-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            
            // Update active filter button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter portfolio items
            portfolioItems.forEach(item => {
                const category = item.getAttribute('data-category');
                
                if (filter === 'all' || category === filter) {
                    item.style.display = 'block';
                    item.classList.add('fade-in');
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Portfolio modal functionality
function openPortfolioModal(item) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'portfolioModal';
    modal.setAttribute('tabindex', '-1');
    
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${item.title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <img src="${item.image_url || '/static/images/placeholder-project.jpg'}" 
                         class="img-fluid mb-3" 
                         alt="${item.title}">
                    <p class="mb-3">${item.description}</p>
                    ${item.client ? `<p><strong>Client:</strong> ${item.client}</p>` : ''}
                    ${item.technologies ? `<p><strong>Technologies:</strong> ${item.technologies}</p>` : ''}
                    <div class="d-flex gap-2">
                        ${item.project_url ? `<a href="${item.project_url}" target="_blank" class="btn btn-primary">View Project</a>` : ''}
                        ${item.github_url ? `<a href="${item.github_url}" target="_blank" class="btn btn-outline-primary">GitHub</a>` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Clean up modal after it's hidden
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// Search functionality for portfolio
function initPortfolioSearch() {
    const searchInput = document.getElementById('portfolio-search');
    if (!searchInput) return;
    
    const searchHandler = ArnetriceUtils.debounce(async function() {
        const query = searchInput.value.trim();
        const container = document.getElementById('portfolio-grid');
        
        if (query.length === 0) {
            loadAllPortfolio();
            return;
        }
        
        try {
            // Show loading state
            container.innerHTML = '<div class="col-12 text-center"><div class="loading"></div><p class="mt-3">Searching...</p></div>';
            
            // Search portfolio items (this would need to be implemented in the backend)
            const response = await ArnetriceUtils.apiRequest(`/api/portfolio/search?q=${encodeURIComponent(query)}`);
            
            if (response && response.length > 0) {
                displayPortfolioItems(response, container);
            } else {
                container.innerHTML = '<div class="col-12 text-center"><p class="text-muted">No projects found matching your search.</p></div>';
            }
            
        } catch (error) {
            console.error('Error searching portfolio:', error);
            container.innerHTML = '<div class="col-12 text-center"><p class="text-danger">Error searching portfolio. Please try again.</p></div>';
        }
    }, 300);
    
    searchInput.addEventListener('input', searchHandler);
}

// Initialize search if search input exists
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('portfolio-search');
    if (searchInput) {
        initPortfolioSearch();
    }
});

