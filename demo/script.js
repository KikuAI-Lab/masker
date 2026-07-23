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

// Interactive Demo Logic (client-side regex preview, not the full Masker API)
const demoInput = document.getElementById('demo-input');
const demoOutput = document.getElementById('demo-output');
const demoStats = document.getElementById('demo-stats');
const processingLine = document.querySelector('.processing-line');

// This preview intentionally covers only these three regex patterns.
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
        demoOutput.replaceChildren();
        demoStats.replaceChildren();
        processingLine.classList.add('hidden');
        return;
    }

    const startTime = performance.now();
    const ranges = findMaskRanges(text);

    const endTime = performance.now();
    const duration = (endTime - startTime).toFixed(2);

    renderMaskedText(text, ranges);
    demoOutput.style.opacity = '1';
    processingLine.classList.add('hidden');

    const durationStat = document.createElement('span');
    durationStat.textContent = `⚡ Regex pass in ${duration}ms`;

    const matchStat = document.createElement('span');
    matchStat.textContent = `🛡️ ${ranges.length} regex matches masked`;

    demoStats.replaceChildren(durationStat, matchStat);

    // Animate result
    gsap.from(demoOutput, {
        opacity: 0,
        y: 10,
        duration: 0.3
    });
}

function findMaskRanges(text) {
    const matches = [];

    Object.values(PATTERNS).forEach((pattern) => {
        for (const match of text.matchAll(pattern)) {
            matches.push({
                start: match.index,
                end: match.index + match[0].length
            });
        }
    });

    matches.sort((left, right) => left.start - right.start || right.end - left.end);

    return matches.reduce((ranges, match) => {
        const previous = ranges[ranges.length - 1];

        if (!previous || match.start >= previous.end) {
            ranges.push(match);
        } else if (match.end > previous.end) {
            previous.end = match.end;
        }

        return ranges;
    }, []);
}

function renderMaskedText(text, ranges) {
    const fragment = document.createDocumentFragment();
    let position = 0;

    ranges.forEach((range) => {
        fragment.append(document.createTextNode(text.slice(position, range.start)));

        const highlight = document.createElement('span');
        highlight.className = 'highlight-masked';
        highlight.textContent = '***';
        fragment.append(highlight);

        position = range.end;
    });

    fragment.append(document.createTextNode(text.slice(position)));
    demoOutput.replaceChildren(fragment);
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
