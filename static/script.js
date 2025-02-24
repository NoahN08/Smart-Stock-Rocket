
document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-container");
    const chatButton = document.getElementById("ai-button");
    const closeButton = document.getElementById("close-btn");
    const sendButton = document.getElementById("send-btn");
    const chatInput = document.getElementById("chat-text");
    const chatBody = document.getElementById("chat-body");

    if (!chatBox || !chatButton || !closeButton || !sendButton || !chatInput || !chatBody) {
        console.error("Chat elements not found!");
        return;
    }

    chatButton.addEventListener("click", function () {
        chatBox.classList.toggle("chat-visible");
    });

    closeButton.addEventListener("click", function () {
        chatBox.classList.remove("chat-visible");
    });

    function sendMessage() {
        const userMessage = chatInput.value.trim();
        if (userMessage) {
            appendMessage(userMessage, 'user');
            chatInput.value = '';

            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ message: userMessage })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                if (data.response) {
                    appendMessage(data.response, 'assistant');
                } else {
                    throw new Error('No response from assistant');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                appendMessage('Sorry, something went wrong. Please try again.', 'assistant');
            });
        }
    }

    sendButton.addEventListener("click", sendMessage);
    
    chatInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });

    function appendMessage(message, sender) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", sender);
        messageElement.textContent = message;
        chatBody.appendChild(messageElement);
        chatBody.scrollTop = chatBody.scrollHeight;
    }
});
