document.addEventListener('DOMContentLoaded', function() {
    initializeEllipsisMenus();
    
    // Set up a mutation observer to handle dynamically added menus
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                // Check if any new ellipsis menus were added
                let newMenus = false;
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // ELEMENT_NODE
                        if (node.classList && node.classList.contains('ellipsis-menu')) {
                            newMenus = true;
                        } else if (node.querySelectorAll) {
                            const childMenus = node.querySelectorAll('.ellipsis-menu');
                            if (childMenus.length > 0) {
                                newMenus = true;
                            }
                        }
                    }
                });
                
                if (newMenus) {
                    initializeEllipsisMenus();
                }
            }
        });
    });
    
    // Start observing changes to the entire document body
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

function initializeEllipsisMenus() {
    // Initialize all ellipsis menus
    const ellipsisMenus = document.querySelectorAll('.ellipsis-menu');
    
    ellipsisMenus.forEach(menu => {
        // Skip already initialized menus
        if (menu.dataset.initialized === 'true') return;
        
        const btn = menu.querySelector('.ellipsis-btn');
        
        if (btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Close all other open menus first
                ellipsisMenus.forEach(otherMenu => {
                    if (otherMenu !== menu && otherMenu.classList.contains('active')) {
                        otherMenu.classList.remove('active');
                    }
                });
                
                // Toggle this menu
                menu.classList.toggle('active');
            });
            
            // Mark as initialized
            menu.dataset.initialized = 'true';
        }
    });
    
    // Remove any existing document click handlers for menu closing to prevent duplicates
    document.removeEventListener('click', closeAllMenus);
    document.addEventListener('click', closeAllMenus);
    
    // Setup content click event handlers to prevent bubbling
    document.querySelectorAll('.ellipsis-menu-content').forEach(content => {
        // Skip already initialized content
        if (content.dataset.initialized === 'true') return;
        
        content.addEventListener('click', function(e) {
            e.stopPropagation();
        });
        
        // Mark as initialized
        content.dataset.initialized = 'true';
    });
}

function closeAllMenus() {
    document.querySelectorAll('.ellipsis-menu.active').forEach(menu => {
        menu.classList.remove('active');
    });
}