// Chatbot functionality for Tour Package Management System

document.addEventListener('DOMContentLoaded', function() {
    // Get chatbot elements
    const chatbotButton = document.querySelector('.chatbot-button');
    const chatbotWindow = document.querySelector('.chatbot-window');
    const chatbotClose = document.querySelector('.chatbot-close');
    const chatbotMessages = document.querySelector('.chatbot-messages');
    const chatbotInput = document.querySelector('.chatbot-input input');
    const chatbotSend = document.querySelector('.chatbot-input button');
    
    if (!chatbotButton || !chatbotWindow) return;
    
    // Toggle chatbot window visibility
    chatbotButton.addEventListener('click', function() {
        chatbotWindow.style.display = chatbotWindow.style.display === 'none' || chatbotWindow.style.display === '' ? 'flex' : 'none';
        
        // If opening the chatbot, show welcome message and focus input
        if (chatbotWindow.style.display === 'flex') {
            if (chatbotMessages.children.length === 0) {
                addBotMessage("Hello! Welcome to Tour Package Management System. How can I help you today?");
                addBotMessage("You can ask me about our packages, booking process, payment options, or cancellation policy.");
            }
            
            if (chatbotInput) {
                chatbotInput.focus();
            }
        }
    });
    
    // Close chatbot window
    if (chatbotClose) {
        chatbotClose.addEventListener('click', function() {
            chatbotWindow.style.display = 'none';
        });
    }
    
    // Send message on button click or Enter key press
    if (chatbotSend && chatbotInput) {
        chatbotSend.addEventListener('click', sendMessage);
        
        chatbotInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Function to send user message and get response
    function sendMessage() {
        const message = chatbotInput.value.trim();
        
        if (message === '') return;
        
        // Add user message to chat
        addUserMessage(message);
        
        // Clear input
        chatbotInput.value = '';
        
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('chatbot-message', 'message-bot', 'typing-indicator');
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        chatbotMessages.appendChild(typingIndicator);
        
        // Scroll to bottom
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        
        // Send message to server and get response
        fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            const typingIndicator = document.querySelector('.typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            // Add bot response with slight delay for natural feel
            setTimeout(() => {
                addBotMessage(data.response);
            }, 500);
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Remove typing indicator
            const typingIndicator = document.querySelector('.typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            // Add error message
            addBotMessage("I'm sorry, I'm having trouble connecting. Please try again later.");
        });
    }
    
    // Function to add user message to chat
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chatbot-message', 'message-user');
        messageElement.textContent = message;
        chatbotMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
    
    // Function to add bot message to chat
    function addBotMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chatbot-message', 'message-bot');
        messageElement.textContent = message;
        chatbotMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
});
