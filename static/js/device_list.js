// Device List JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Set active nav item
    setActiveNavItem();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Add event listeners to filter controls
    setupFilterListeners();
});

// Function to set the active navigation item
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath === href || (currentPath.startsWith(href) && href !== '/')) {
            link.classList.add('active');
        }
    });
}

// Function to initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup event listeners for filter controls
function setupFilterListeners() {
    // Auto-submit on filter change
    const filterSelects = document.querySelectorAll('select[name="device_type"], select[name="status"]');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            this.form.submit();
        });
    });
    
    // Clear search on reset button click
    const resetButton = document.querySelector('a.btn-outline-secondary');
    if (resetButton) {
        resetButton.addEventListener('click', function(e) {
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.value = '';
            }
        });
    }
}
