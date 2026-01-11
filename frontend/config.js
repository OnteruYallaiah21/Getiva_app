// API Configuration - auto-detect based on environment
(function() {
    // Try to detect API base URL
    let apiBase;
    
    // If we're on the same domain (Render deployment), use relative URL
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        // Production: use same origin
        apiBase = window.location.origin;
    } else {
        // Development: use localhost:8000
        apiBase = 'http://localhost:8000';
    }
    
    // Export for use in other scripts
    window.API_BASE = apiBase;
})();

