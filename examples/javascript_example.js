/**
 * Masker API - JavaScript Example
 * 
 * This example shows how to use Masker API to clean PII before sending to ChatGPT.
 */

const MASKER_API_URL = 'https://masker.kikuai.dev/v1/redact';

/**
 * Redact PII from text using Masker API.
 * 
 * @param {string} text - Text containing PII
 * @param {string} mode - Redaction mode: "mask" or "placeholder"
 * @returns {Promise<string>} Text with PII redacted
 */
async function redactPII(text, mode = 'placeholder') {
    const response = await fetch(MASKER_API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text, mode })
    });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.redacted_text;
}

/**
 * Redact PII from JSON structure using Masker API.
 * 
 * @param {Object} data - JSON object containing PII
 * @param {string} mode - Redaction mode: "mask" or "placeholder"
 * @returns {Promise<Object>} JSON object with PII redacted
 */
async function redactJSON(data, mode = 'placeholder') {
    const response = await fetch(MASKER_API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ json: data, mode })
    });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    return result.redacted_json;
}

// Example 1: Clean user message before ChatGPT
async function exampleChatGPTCleanup() {
    const userMessage = "My name is John Doe and my email is john@example.com";
    
    // Clean the message
    const safeMessage = await redactPII(userMessage, 'placeholder');
    console.log('Original:', userMessage);
    console.log('Cleaned:', safeMessage);
    // Output: "My name is <PERSON> and my email is <EMAIL>"
    
    // Now safe to send to ChatGPT
    // const chatgptResponse = await openai.chat.completions.create({
    //     model: "gpt-4",
    //     messages: [{ role: "user", content: safeMessage }]
    // });
}

// Example 2: Anonymize support ticket
async function exampleSupportTicket() {
    const ticket = {
        customer: "John Doe",
        email: "john@example.com",
        phone: "555-123-4567",
        issue: "Can't login to my account"
    };
    
    // Anonymize
    const anonymized = await redactJSON(ticket, 'placeholder');
    console.log('Original ticket:', ticket);
    console.log('Anonymized:', anonymized);
}

// Example 3: Process form data
async function exampleFormData() {
    const formData = {
        name: "Jane Smith",
        email: "jane@example.com",
        message: "I need help with my order"
    };
    
    // Clean before classification
    const cleaned = await redactJSON(formData, 'placeholder');
    console.log('Original form:', formData);
    console.log('Cleaned form:', cleaned);
}

// Run examples
(async () => {
    try {
        console.log('=== Example 1: ChatGPT Cleanup ===');
        await exampleChatGPTCleanup();
        console.log();
        
        console.log('=== Example 2: Support Ticket ===');
        await exampleSupportTicket();
        console.log();
        
        console.log('=== Example 3: Form Data ===');
        await exampleFormData();
    } catch (error) {
        console.error('Error:', error.message);
    }
})();

