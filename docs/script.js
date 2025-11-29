// Custom Cursor Logic
const cursor = document.querySelector('.glow-cursor');

document.addEventListener('mousemove', (e) => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';
});

// GSAP Animations
gsap.registerPlugin(ScrollTrigger);

// Hero Text Animation
gsap.from('.hero-content > *', {
    y: 50,
    opacity: 0,
    duration: 1,
    stagger: 0.2,
    ease: 'power3.out'
});

// Visual Metaphor Animation
gsap.from('.visual-metaphor', {
    x: 100,
    opacity: 0,
    duration: 1.5,
    delay: 0.5,
    ease: 'power3.out'
});

// Feature Cards Animation
gsap.from('.feature-card', {
    scrollTrigger: {
        trigger: '.features',
        start: 'top 80%'
    },
    y: 50,
    opacity: 0,
    duration: 0.8,
    stagger: 0.2
});

// Interactive Demo Logic (Client-side emulation for speed/demo purposes)
const demoInput = document.getElementById('demo-input');
const demoOutput = document.getElementById('demo-output');
const demoStats = document.getElementById('demo-stats');
const processingLine = document.querySelector('.processing-line');

// Simple regex for demo purposes (Backend is much more powerful)
const PATTERNS = {
    email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    phone: /(\+\d{1,3}[-.\s]?)?(\(\d{1,4}\)[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}/g,
    card: /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g
};

let typingTimer;

demoInput.addEventListener('input', () => {
    clearTimeout(typingTimer);
    processingLine.classList.remove('hidden');
    demoOutput.style.opacity = '0.5';

    typingTimer = setTimeout(() => {
        processText(demoInput.value);
    }, 500);
});

function processText(text) {
    if (!text) {
        demoOutput.innerHTML = '';
        demoStats.innerHTML = '';
        processingLine.classList.add('hidden');
        return;
    }

    const startTime = performance.now();
    let maskedText = text;
    let count = 0;

    // Apply masking
    maskedText = maskedText.replace(PATTERNS.email, () => { count++; return '<span class="highlight-masked">***</span>'; });
    maskedText = maskedText.replace(PATTERNS.phone, () => { count++; return '<span class="highlight-masked">***</span>'; });
    maskedText = maskedText.replace(PATTERNS.card, () => { count++; return '<span class="highlight-masked">***</span>'; });

    const endTime = performance.now();
    const duration = (endTime - startTime).toFixed(2);

    demoOutput.innerHTML = maskedText;
    demoOutput.style.opacity = '1';
    processingLine.classList.add('hidden');

    demoStats.innerHTML = `
        <span>⚡ Processed in ${duration}ms</span>
        <span>🛡️ ${count} PII entities masked</span>
    `;

    // Animate result
    gsap.from(demoOutput, {
        opacity: 0,
        y: 10,
        duration: 0.3
    });
}

// Glitch Effect for Title
const glitchText = document.querySelector('.glitch-text');
setInterval(() => {
    glitchText.style.textShadow = `
        ${Math.random() * 10 - 5}px ${Math.random() * 10 - 5}px 0 #00f2ff,
        ${Math.random() * 10 - 5}px ${Math.random() * 10 - 5}px 0 #ff0055
    `;
    setTimeout(() => {
        glitchText.style.textShadow = 'none';
    }, 100);
}, 3000);
