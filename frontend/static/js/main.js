// Main JavaScript for chat frontend

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('chat-form');
    const loading = document.getElementById('loading');
    const responses = document.getElementById('responses');
    const responseCards = document.getElementById('response-cards');
    const submitBtn = document.getElementById('submit-btn');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get selected models
        const selectedModels = Array.from(document.querySelectorAll('input[name="model"]:checked'))
            .map(cb => cb.value);
        
        const prompt = document.getElementById('prompt').value.trim();
        
        // Validation
        if (selectedModels.length === 0) {
            alert('Please select at least one model');
            return;
        }
        
        if (selectedModels.length > 3) {
            alert('Please select no more than 3 models');
            return;
        }
        
        if (!prompt) {
            alert('Please enter a prompt');
            return;
        }
        
        // Show loading, hide previous responses
        loading.classList.remove('hidden');
        responses.classList.add('hidden');
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    model_ids: selectedModels
                })
            });
            
            const data = await response.json();
            
            // Clear previous responses
            responseCards.innerHTML = '';
            
            // Show prompt
            const promptDisplay = document.createElement('div');
            promptDisplay.className = 'prompt-display';
            promptDisplay.innerHTML = `<strong>Your prompt:</strong> ${escapeHtml(prompt)}`;
            responseCards.appendChild(promptDisplay);
            
            if (data.error) {
                // Show error
                const errorCard = document.createElement('div');
                errorCard.className = 'response-card error';
                errorCard.innerHTML = `<h3>Error</h3><div class="content">${escapeHtml(data.error)}</div>`;
                responseCards.appendChild(errorCard);
            } else if (data.responses) {
                // Show each model's response
                data.responses.forEach(resp => {
                    const card = document.createElement('div');
                    card.className = resp.success ? 'response-card' : 'response-card error';
                    
                    const content = resp.success 
                        ? resp.response 
                        : (resp.error || 'Unknown error');
                    
                    card.innerHTML = `
                        <h3>${escapeHtml(resp.model_name || resp.model_id)}</h3>
                        <div class="content">${escapeHtml(content)}</div>
                    `;
                    responseCards.appendChild(card);
                });
            }
            
            responses.classList.remove('hidden');
            
        } catch (error) {
            responseCards.innerHTML = `
                <div class="response-card error">
                    <h3>Connection Error</h3>
                    <div class="content">Could not connect to the server. Please try again.</div>
                </div>
            `;
            responses.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });
    
    // Helper function to escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
