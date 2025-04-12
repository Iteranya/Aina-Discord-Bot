
/**
 * Initialize the AI generation functionality
 * @param {HTMLTextAreaElement} htmlCode - The HTML editor element
 * @param {Function} updatePreviewCallback - Callback to update the preview
 */
function initAiGeneration(htmlCode, updatePreviewCallback) {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const button = form.querySelector('button');
        const originalButtonText = button.innerHTML;
        
        // Show loading state
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        
        const formData = new FormData(form);
        const websiteDescription = formData.get('content');
        
        // Combine content
        const combinedContent = `${htmlCode.value}\n\n${websiteDescription}`;
        formData.set('content', combinedContent);
        
        try {
            const response = await fetch('/generate-website', {
                method: 'POST',
                body: formData
            });
    
            const data = await response.json();
            if (data.id) {
                // Connect to the streaming endpoint
                const eventSource = new EventSource(`/stream/${data.id}`);
                let generatedHtml = '';
                
                eventSource.onmessage = function(event) {
                    const eventData = JSON.parse(event.data);
                    
                    if (eventData.html) {
                        generatedHtml += eventData.html;
                        htmlCode.value = generatedHtml;
                        updatePreviewCallback(htmlCode, document.getElementById('preview'));
                    }
                    
                    if (eventData.done) {
                        eventSource.close();
                        button.disabled = false;
                        button.innerHTML = originalButtonText;
                        
                        // Show completion effect
                        const completionEffect = document.createElement('div');
                        completionEffect.innerHTML = '✧･ﾟ: *✧･ﾟ:* Generation Complete! *:･ﾟ✧*:･ﾟ✧';
                        completionEffect.style.position = 'fixed';
                        completionEffect.style.bottom = '20px';
                        completionEffect.style.left = '50%';
                        completionEffect.style.transform = 'translateX(-50%)';
                        completionEffect.style.backgroundColor = 'rgba(76, 175, 80, 0.9)';
                        completionEffect.style.color = 'white';
                        completionEffect.style.padding = '10px 20px';
                        completionEffect.style.borderRadius = '20px';
                        completionEffect.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.2)';
                        completionEffect.style.animation = 'fadeInOut 3s ease-out';
                        completionEffect.style.zIndex = '1000';
                        
                        document.body.appendChild(completionEffect);
                        
                        setTimeout(() => {
                            completionEffect.style.animation = 'fadeOut 0.5s ease-out';
                            setTimeout(() => completionEffect.remove(), 500);
                        }, 2500);
                    }
                };
            }
        } catch (error) {
            console.error('Error:', error);
            button.disabled = false;
            button.innerHTML = originalButtonText;
            
            showNotification('Yabai! Something went wrong (╥﹏╥)', 'error');
        }
    });
}