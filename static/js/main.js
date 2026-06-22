// Main JavaScript file for the Tour Package Management System

// Handle filter changes
document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        const filters = filterForm.querySelectorAll('select');
        filters.forEach(filter => {
            filter.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navToggle = document.querySelector('.navbar-toggle');
    
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            const navItems = document.querySelector('.navbar-nav');
            navItems.classList.toggle('active');
        });
    }
    
    // Package card hover effects
    const packageCards = document.querySelectorAll('.card');
    
    packageCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
        });
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.alert');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    
                    // Create error message if it doesn't exist
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.classList.add('error-message');
                        errorMsg.style.color = 'red';
                        errorMsg.style.fontSize = '0.85rem';
                        errorMsg.style.marginTop = '0.25rem';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                    
                    errorMsg.textContent = 'This field is required';
                } else {
                    field.classList.remove('is-invalid');
                    
                    // Remove error message if it exists
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
    
    // Initialize date pickers
    const datePickers = document.querySelectorAll('input[type="date"]');
    
    datePickers.forEach(picker => {
        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        picker.setAttribute('min', today);
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('packageSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const packages = document.querySelectorAll('.packages-grid .card');
            
            packages.forEach(package => {
                const title = package.querySelector('.card-title').textContent.toLowerCase();
                const description = package.querySelector('.card-text').textContent.toLowerCase();
                document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('packageSearchForm');
    if (!searchForm) return;

    function filterPackages() {
        const keyword = document.getElementById('keyword').value.toLowerCase();
        const location = document.getElementById('location').value.toLowerCase();
        const duration = document.getElementById('duration').value;
        const price = document.getElementById('price').value;
        const sort = document.getElementById('sort').value;

        const packages = document.querySelectorAll('.card');
        
        packages.forEach(package => {
            const title = package.querySelector('.card-title').textContent.toLowerCase();
            const packageLocation = package.querySelector('.card-location').textContent.toLowerCase();
            const durationText = package.querySelector('.card-duration').textContent;
            const priceText = package.querySelector('.card-price').textContent;
            const durationDays = parseInt(durationText.match(/\d+/)[0]);
            const priceValue = parseInt(priceText.replace(/[^0-9]/g, ''));

            let isVisible = true;

            // Keyword filter
            if (keyword && !title.includes(keyword) && !packageLocation.includes(keyword)) {
                isVisible = false;
            }

            // Location filter
            if (location && !packageLocation.includes(location)) {
                isVisible = false;
            }

            // Duration filter
            if (duration) {
                const [min, max] = duration.split('-').map(Number);
                if (max) {
                    if (durationDays < min || durationDays > max) isVisible = false;
                } else {
                    if (durationDays < min) isVisible = false;
                }
            }

            // Price filter
            if (price) {
                const [minPrice, maxPrice] = price.split('-').map(str => parseInt(str) || Infinity);
                if (priceValue < minPrice || priceValue > maxPrice) isVisible = false;
            }

            package.style.display = isVisible ? '' : 'none';
        });

        // Sorting
        const packagesContainer = document.querySelector('.packages-grid');
        const packagesArray = Array.from(packages);
        
        packagesArray.sort((a, b) => {
            switch(sort) {
                case 'price_low':
                    return getPriceValue(a) - getPriceValue(b);
                case 'price_high':
                    return getPriceValue(b) - getPriceValue(a);
                case 'duration':
                    return getDurationValue(a) - getDurationValue(b);
                default:
                    return 0;
            }
        });

        packagesArray.forEach(package => {
            if (package.style.display !== 'none') {
                packagesContainer.appendChild(package);
            }
        });
    }

    function getPriceValue(package) {
        return parseInt(package.querySelector('.card-price').textContent.replace(/[^0-9]/g, ''));
    }

    function getDurationValue(package) {
        return parseInt(package.querySelector('.card-duration').textContent.match(/\d+/)[0]);
    }

    // Add event listeners
    searchForm.querySelectorAll('select, input').forEach(element => {
        element.addEventListener('change', filterPackages);
    });
    
    document.getElementById('keyword').addEventListener('input', filterPackages);
    
    searchForm.querySelector('button[type="reset"]').addEventListener('click', () => {
        setTimeout(filterPackages, 10);
    });
});
