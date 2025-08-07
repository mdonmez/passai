/**
 * Pass Generator Application JavaScript
 * Handles UI interactions, API calls, and visual feedback
 */

class PassAI {
    constructor() {
        this.timeoutId = null;
        this.initializeElements();
        this.setupEventListeners();
        this.setFavicon();
    }

    /**
     * Initialize DOM element references
     */
    initializeElements() {
        this.userInput = document.getElementById('userInput');
        this.passDisplay = document.getElementById('passDisplay');
        this.passText = document.getElementById('passText');
        this.loading = document.getElementById('loading');
        this.error = document.getElementById('error');
        this.copiedToast = document.getElementById('copiedToast');
        this.favicon = document.getElementById('favicon');
    }

    /**
     * Set up event listeners for the application
     */
    setupEventListeners() {
        // Handle user input with debouncing
        this.userInput.addEventListener('input', (event) => {
            this.handleUserInput(event);
        });

        // Listen for color scheme changes
        window.matchMedia('(prefers-color-scheme: dark)')
            .addEventListener('change', () => this.setFavicon());
    }

    /**
     * Set favicon based on user's color scheme preference
     */
    setFavicon() {
        const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (isDarkMode) {
            // Dark theme: use light logo for contrast
            this.favicon.href = "/static/light_logo.svg";
        } else {
            // Light theme: use dark logo for contrast  
            this.favicon.href = "/static/dark_logo.svg";
        }
    }

    /**
     * Handle user input with debouncing and auto-resize
     * @param {Event} event - Input event
     */
    handleUserInput(event) {
        const textarea = event.target;
        
        // Clear existing timeout
        clearTimeout(this.timeoutId);
        
        // Set new timeout for pass generation
        this.timeoutId = setTimeout(() => {
            this.generatePass(textarea.value);
        }, 1000);
        
        // Auto-resize textarea
        this.autoResizeTextarea(textarea);
    }

    /**
     * Auto-resize textarea based on content
     * @param {HTMLTextAreaElement} textarea - The textarea element
     */
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        const maxHeight = window.innerWidth <= 640 ? 160 : 200;
        const newHeight = Math.min(textarea.scrollHeight, maxHeight);
        textarea.style.height = newHeight + 'px';
        
        if (textarea.scrollHeight > maxHeight) {
            textarea.style.overflowY = 'auto';
        } else {
            textarea.style.overflowY = 'hidden';
        }
    }

    /**
     * Show error message to user
     * @param {string} message - Error message to display
     */
    showError(message) {
        this.error.textContent = message;
        this.error.classList.add('show');
    }

    /**
     * Hide error message
     */
    hideError() {
        this.error.classList.remove('show');
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        this.loading.classList.add('show');
        this.hideError();
        this.copiedToast.classList.remove('show');
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        this.loading.classList.remove('show');
    }

    /**
     * Show copied indicator with auto-hide
     */
    showCopiedIndicator() {
        this.copiedToast.classList.add('show');
        setTimeout(() => {
            this.copiedToast.classList.remove('show');
        }, 1500);
    }

    /**
     * Copy text to clipboard using legacy method for broader compatibility
     * @param {string} text - Text to copy
     */
    copyToClipboard(text) {
        const activeElement = document.activeElement;
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        
        // Restore focus if it was on the user input
        if (activeElement === this.userInput) {
            this.userInput.focus();
        }
    }

    /**
     * Generate password/passphrase via API call
     * @param {string} input - User input description
     */
    async generatePass(input) {
        if (!input.trim()) {
            this.transitionToPlaceholder();
            this.hideLoading();
            this.hideError();
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: input })
            });

            const data = await response.json();
            this.hideLoading();

            if (data.error) {
                this.showError(data.error);
                this.transitionToPlaceholder();
            } else {
                this.hideError();
                this.transitionToPass(data.pass);
                this.copyToClipboard(data.pass);
                this.showCopiedIndicator();
            }
        } catch (err) {
            this.hideLoading();
            this.showError('Failed to generate pass. Please try again.');
            console.error('API Error:', err);
        }
    }

    /**
     * Transition display back to placeholder state
     */
    transitionToPlaceholder() {
        const wasEmpty = this.passDisplay.classList.contains('empty');
        
        if (!wasEmpty) {
            // Pass to placeholder transition
            this.passDisplay.classList.add('transitioning');
            this.passText.classList.add('transitioning');
            this.passText.classList.add('hide');
            this.passText.classList.remove('show');
            
            setTimeout(() => {
                this.passText.textContent = 'your pass will appear here';
                this.passDisplay.classList.add('empty');
                this.passDisplay.classList.remove('transitioning');
                this.passText.classList.remove('transitioning');
                this.passText.classList.remove('hide');
                this.passText.classList.remove('show');
            }, 250);
        } else {
            // Already placeholder, just update text if needed
            this.passText.textContent = 'your pass will appear here';
            this.passText.classList.remove('hide', 'show');
        }
    }

    /**
     * Transition display to show generated pass
     * @param {string} pass - Generated password/passphrase
     */
    transitionToPass(pass) {
        const wasEmpty = this.passDisplay.classList.contains('empty');
        
        if (wasEmpty) {
            // Placeholder to pass transition
            this.passDisplay.classList.add('transitioning');
            this.passText.classList.add('transitioning');
            this.passText.classList.add('hide');
            
            setTimeout(() => {
                this.passText.textContent = pass;
                this.passDisplay.classList.remove('empty');
                this.passText.classList.remove('hide');
                this.passText.classList.add('show');
                
                setTimeout(() => {
                    this.passDisplay.classList.remove('transitioning');
                    this.passText.classList.remove('transitioning');
                }, 300);
            }, 150);
        } else {
            // Pass to pass transition
            this.passDisplay.classList.add('transitioning');
            this.passText.classList.add('transitioning');
            this.passText.classList.add('hide');
            this.passText.classList.remove('show');
            
            setTimeout(() => {
                this.passText.textContent = pass;
                this.passText.classList.remove('hide');
                this.passText.classList.add('show');
                
                setTimeout(() => {
                    this.passDisplay.classList.remove('transitioning');
                    this.passText.classList.remove('transitioning');
                }, 300);
            }, 250);
        }
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new PassAI();
});
