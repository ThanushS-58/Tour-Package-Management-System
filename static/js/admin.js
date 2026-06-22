// Admin dashboard functionality

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality for mobile view
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const adminSidebar = document.querySelector('.admin-sidebar');
    const adminContent = document.querySelector('.admin-content');
    
    // Initialize sidebar state based on screen width
    function initSidebar() {
        if (window.innerWidth <= 768) {
            adminSidebar.classList.add('collapsed');
            adminContent.classList.add('expanded');
        } else {
            adminSidebar.classList.remove('collapsed');
            adminContent.classList.remove('expanded');
        }
    }
    
    // Toggle sidebar on button click
    if (sidebarToggle && adminSidebar && adminContent) {
        // Set initial state
        initSidebar();
        
        // Add event listener for toggle button
        sidebarToggle.addEventListener('click', function() {
            adminSidebar.classList.toggle('collapsed');
            adminContent.classList.toggle('expanded');
        });
        
        // Update on window resize
        window.addEventListener('resize', initSidebar);
    }
    
    // Package image preview before upload
    const imageInput = document.querySelector('input[name="image"]');
    const imagePreview = document.querySelector('.image-preview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            
            if (file) {
                const reader = new FileReader();
                
                reader.addEventListener('load', function() {
                    imagePreview.style.backgroundImage = `url(${this.result})`;
                    imagePreview.style.display = 'block';
                });
                
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Status update dropdown functionality
    const statusDropdowns = document.querySelectorAll('.status-dropdown');
    
    statusDropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });
    
    // Package form validation with rich text support
    const packageForm = document.querySelector('.package-form');
    
    if (packageForm) {
        packageForm.addEventListener('submit', function(e) {
            const nameInput = document.querySelector('input[name="name"]');
            const priceInput = document.querySelector('input[name="price"]');
            const durationInput = document.querySelector('input[name="duration"]');
            const locationInput = document.querySelector('input[name="location"]');
            const itineraryInput = document.querySelector('textarea[name="itinerary"]');
            
            let isValid = true;
            
            // Validate required fields
            if (!nameInput.value.trim()) {
                showError(nameInput, 'Package name is required');
                isValid = false;
            } else {
                removeError(nameInput);
            }
            
            // Validate price (must be a positive number)
            if (!priceInput.value.trim() || isNaN(priceInput.value) || parseFloat(priceInput.value) <= 0) {
                showError(priceInput, 'Please enter a valid price');
                isValid = false;
            } else {
                removeError(priceInput);
            }
            
            // Validate duration (must be a positive integer)
            if (!durationInput.value.trim() || isNaN(durationInput.value) || parseInt(durationInput.value) <= 0) {
                showError(durationInput, 'Please enter a valid duration in days');
                isValid = false;
            } else {
                removeError(durationInput);
            }
            
            // Validate location
            if (!locationInput.value.trim()) {
                showError(locationInput, 'Location is required');
                isValid = false;
            } else {
                removeError(locationInput);
            }
            
            // Validate itinerary
            if (!itineraryInput.value.trim()) {
                showError(itineraryInput, 'Itinerary is required');
                isValid = false;
            } else {
                removeError(itineraryInput);
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
    
    // Helper functions for form validation
    function showError(element, message) {
        let errorMsg = element.nextElementSibling;
        if (!errorMsg || !errorMsg.classList.contains('error-message')) {
            errorMsg = document.createElement('div');
            errorMsg.classList.add('error-message');
            errorMsg.style.color = 'red';
            errorMsg.style.fontSize = '0.85rem';
            errorMsg.style.marginTop = '0.25rem';
            element.parentNode.insertBefore(errorMsg, element.nextSibling);
        }
        
        errorMsg.textContent = message;
    }
    
    function removeError(element) {
        const errorMsg = element.nextElementSibling;
        if (errorMsg && errorMsg.classList.contains('error-message')) {
            errorMsg.remove();
        }
    }
    
    // Data tables functionality for admin lists
    const tables = document.querySelectorAll('.admin-table');
    
    tables.forEach(table => {
        const searchInput = table.parentElement.querySelector('.table-search');
        
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        }
    });
});
