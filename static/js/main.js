const chatContainer = document.getElementById('chat-container');
const form = document.getElementById('generatorForm');

// Input elements
const pdfInput = document.querySelector('input[name="pdfFile"]');
const imageInput = document.querySelector('input[name="imageFile"]');
const urlInput = document.querySelector('input[name="imageUrl"]');
const contextInput = document.querySelector('textarea[name="context"]');

// Function to disable/enable inputs
function toggleInputs(activeInput) {
    const inputs = {
        pdfFile: pdfInput,
        imageFile: imageInput,
        imageUrl: urlInput,
        context: contextInput
    };
    
    Object.entries(inputs).forEach(([key, input]) => {
        if (key === activeInput) {
            input.disabled = false;
            input.classList.remove('opacity-50', 'bg-gray-100');
        } else {
            input.disabled = true;
            input.classList.add('opacity-50', 'bg-gray-100');
        }
    });
}

// Reset function
function resetInputs() {
    const inputs = [pdfInput, imageInput, urlInput, contextInput];
    inputs.forEach(input => {
        input.disabled = false;
        input.classList.remove('opacity-50', 'bg-gray-100');
        input.value = '';
    });
}

// Event listeners for inputs
[pdfInput, imageInput, urlInput, contextInput].forEach(input => {
    input.addEventListener('input', function() {
        if (this.value) {
            toggleInputs(this.name);
        }
    });
});

function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
    messageDiv.innerHTML = content;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function handleSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    let hasInput = false;

    // Check if any input method has content
    if (formData.get('pdfFile') && formData.get('pdfFile').size > 0) hasInput = true;
    if (formData.get('imageFile') && formData.get('imageFile').size > 0) hasInput = true;
    if (formData.get('imageUrl') && formData.get('imageUrl').trim() !== '') hasInput = true;
    if (formData.get('context') && formData.get('context').trim() !== '') hasInput = true;

    if (!hasInput) {
        addMessage('<div class="text-red-500">Please provide input text through one of the available methods.</div>');
        return;
    }

    // Display loading message
    addMessage(`
        <div class="font-medium">Input Parameters:</div>
        <ul class="list-disc ml-4">
            <li>Bloom's Level: ${formData.get('bloom_level')}</li>
            <li>Question Type: ${formData.get('question_type')}</li>
            <li>Difficulty Level: ${formData.get('difficulty_level')}</li>
            <li>Number of Questions: ${formData.get('num_questions')}</li>
        </ul>
    `, true);

    const loadingMessage = document.createElement('div');
    loadingMessage.classList.add('animate-pulse');
    loadingMessage.innerHTML = 'Generating questions...';
    chatContainer.appendChild(loadingMessage);

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }

        const result = await response.json();

        // Remove loading animation
        loadingMessage.remove();


        if (result.error) {
            addMessage(`<div class="text-red-500">Error: ${result.error}</div>`);
            return;
        }

        // Display generated questions
        const questions = result.questions || [];
        if (questions.length === 0) {
            addMessage('<div class="text-yellow-600">No questions could be generated. Please try again with different parameters or input text.</div>');
            return;
        }

        const questionsHtml = questions.map((q, idx) => {
            // Generate HTML for each question
            let optionsHtml = '';
            if (q.options && q.options.length > 0) {
                optionsHtml = `
                    <div class="mt-2"><strong>Options:</strong>
                        <ul class="list-disc pl-8">
                            ${q.options.map(opt => `<li>${opt}</li>`).join('')}
                        </ul>
                    </div>`;
            }
        
            return `
                <div class="question bg-gray-50 p-4 rounded-lg mb-4">
                    <h3 class="font-bold">${idx + 1}. ${q.question}</h3>
                    ${optionsHtml}
                    <div class="mt-2"><strong>Answer:</strong> ${q.answer}</div>
                    <div class="mt-2"><strong>Explanation:</strong> ${q.explanation}</div>
                </div>
            `;
        }).join('');

        addMessage(questionsHtml);

    } catch (error) {
        addMessage(`<div class="text-red-500">Error: ${error.message}</div>`);
    }
}
