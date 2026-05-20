/* ==========================================================================
   ORBA OS DESKTOP CONSOLE LOGIC (JS)
   Handles Canvas WebGL/2D OrbaSphere, WebSocket events, and Approvals.
   ========================================================================== */

let socket = null;
let currentSphereState = "IDLE";
let sphereVolume = 0.40;
let currentActionId = null;

// --- DOM Selectors ---
const connectionStatus = document.getElementById("connectionStatus");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const terminalOutput = document.getElementById("terminalOutput");
const providerSelect = document.getElementById("providerSelect");
const modelInput = document.getElementById("modelInput");
const stateTag = document.getElementById("stateTag");
const sphereGlow = document.getElementById("sphereGlow");

// Approval Modal Selectors
const approvalModal = document.getElementById("approvalModal");
const modalToolName = document.getElementById("modalToolName");
const modalToolParams = document.getElementById("modalToolParams");
const approveBtn = document.getElementById("approveBtn");
const rejectBtn = document.getElementById("rejectBtn");

// --- WebSocket Connection ---
function connectWebSocket() {
    connectionStatus.className = "status-indicator disconnected";
    connectionStatus.querySelector(".status-text").textContent = "Connexion...";
    
    socket = new WebSocket("ws://127.0.0.1:8000/ws");

    socket.onopen = () => {
        connectionStatus.className = "status-indicator connected";
        connectionStatus.querySelector(".status-text").textContent = "En ligne";
        chatInput.disabled = false;
        sendBtn.disabled = false;
        logTerminal("SYSTEM", "Connexion établie avec le backend.", "success");
    };

    socket.onmessage = (event) => {
        const msg = jsonSafeParse(event.data);
        if (!msg) return;

        if (msg.type === "state_change") {
            updateSphereState(msg.state, msg.details);
        } else if (msg.type === "volume_update") {
            sphereVolume = msg.volume;
        } else if (msg.type === "terminal_log") {
            logTerminal(msg.badge, msg.text, msg.style);
        } else if (msg.type === "approval_required") {
            showApprovalModal(msg.action_id, msg.tool, msg.parameters);
        }
    };

    socket.onclose = () => {
        connectionStatus.className = "status-indicator disconnected";
        connectionStatus.querySelector(".status-text").textContent = "Hors ligne";
        chatInput.disabled = true;
        sendBtn.disabled = true;
        logTerminal("SYSTEM", "Connexion perdue. Tentative de reconnexion dans 4 secondes...", "system");
        
        // Auto-reconnect
        setTimeout(connectWebSocket, 4000);
    };

    socket.onerror = (err) => {
        console.error("WebSocket error:", err);
    };
}

function jsonSafeParse(str) {
    try {
        return JSON.parse(str);
    } catch (e) {
        return null;
    }
}

// --- Chat Actions ---
function sendChatMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: "chat_message",
            text: text,
            provider: providerSelect.value,
            model: modelInput.value
        }));
        chatInput.value = "";
    }
}

// Send on click or Enter key
sendBtn.addEventListener("click", sendChatMessage);
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChatMessage();
});

// --- Terminal Logs Helper ---
function logTerminal(badge, text, styleClass) {
    const p = document.createElement("p");
    p.className = `term-line ${styleClass}`;
    p.innerHTML = `<span class="t-badge">[${badge}]</span> ${text}`;
    terminalOutput.appendChild(p);
    
    // Auto-scroll
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

// --- Guardrail Approval Modal Controls ---
function showApprovalModal(actionId, toolName, parameters) {
    currentActionId = actionId;
    modalToolName.textContent = toolName;
    modalToolParams.textContent = JSON.stringify(parameters, null, 2);
    
    approvalModal.classList.add("active");
    updateSphereState("ANALYZING", "Approbation critique requise");
}

function closeApprovalModal(approved) {
    approvalModal.classList.remove("active");
    
    if (socket && socket.readyState === WebSocket.OPEN && currentActionId) {
        socket.send(JSON.stringify({
            type: "approval_response",
            action_id: currentActionId,
            approved: approved
        }));
    }
    currentActionId = null;
}

approveBtn.addEventListener("click", () => closeApprovalModal(true));
rejectBtn.addEventListener("click", () => closeApprovalModal(false));

// --- State and UI Glow Manager ---
const STATE_DOTS = {
    IDLE: '<span class="indicator-dot state-idle"></span> Orba est en veille',
    LISTENING: '<span class="indicator-dot" style="background-color: hsl(280, 100%, 50%); box-shadow: 0 0 10px hsl(280, 100%, 50%)"></span> Orba vous écoute...',
    THINKING: '<span class="indicator-dot" style="background-color: hsl(0, 0%, 98%); box-shadow: 0 0 10px hsl(0, 0%, 98%)"></span> Orba réfléchit...',
    SPEAKING: '<span class="indicator-dot" style="background-color: hsl(45, 100%, 55%); box-shadow: 0 0 10px hsl(45, 100%, 55%)"></span> Orba parle...',
    ANALYZING: '<span class="indicator-dot" style="background-color: hsl(180, 100%, 50%); box-shadow: 0 0 10px hsl(180, 100%, 50%)"></span> Orba lance un outil...'
};

const STATE_GLOWS = {
    IDLE: "radial-gradient(circle, rgba(240, 45, 240, 0.22) 0%, rgba(0,0,0,0) 70%)",
    LISTENING: "radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, rgba(0,0,0,0) 70%)",
    THINKING: "radial-gradient(circle, rgba(255, 255, 255, 0.18) 0%, rgba(0,0,0,0) 70%)",
    SPEAKING: "radial-gradient(circle, rgba(255, 215, 0, 0.2) 0%, rgba(0,0,0,0) 70%)",
    ANALYZING: "radial-gradient(circle, rgba(6, 182, 212, 0.25) 0%, rgba(0,0,0,0) 70%)"
};

function updateSphereState(state, details) {
    currentSphereState = state;
    if (stateTag) stateTag.innerHTML = STATE_DOTS[state] || STATE_DOTS.IDLE;
    if (sphereGlow) sphereGlow.style.background = STATE_GLOWS[state] || STATE_GLOWS.IDLE;
}

// --- WebGL/Canvas 2D OrbaSphere Rendering (Same as Landing Page V3) ---
function initOrbaSphere() {
    const canvas = document.getElementById("orbaSphereCanvas");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let animationFrameId;

    function resizeCanvas() {
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * window.devicePixelRatio;
        canvas.height = rect.height * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }
    
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    const STATE_CONFIG = {
        IDLE: {
            color: "hsl(300, 100%, 25%)",
            colorGlow: "hsl(300, 100%, 12%)",
            colorLight: "hsl(300, 100%, 65%)",
            speed: 0.018,
            noiseFreq: 3.5,
            noiseAmp: 6,
            particleCount: 10,
        },
        LISTENING: {
            color: "hsl(280, 100%, 35%)",
            colorGlow: "hsl(280, 100%, 15%)",
            colorLight: "hsl(280, 100%, 75%)",
            speed: 0.05,
            noiseFreq: 8,
            noiseAmp: 14,
            particleCount: 28,
        },
        THINKING: {
            color: "hsl(320, 10%, 60%)",
            colorGlow: "hsl(320, 5%, 25%)",
            colorLight: "hsl(0, 0%, 100%)",
            speed: 0.028,
            noiseFreq: 5.5,
            noiseAmp: 8,
            particleCount: 15,
        },
        SPEAKING: {
            color: "hsl(335, 100%, 35%)",
            colorGlow: "hsl(335, 100%, 18%)",
            colorLight: "hsl(40, 100%, 70%)",
            speed: 0.038,
            noiseFreq: 4.5,
            noiseAmp: 18,
            particleCount: 22,
        },
        ANALYZING: {
            color: "hsl(180, 100%, 30%)",
            colorGlow: "hsl(180, 100%, 12%)",
            colorLight: "hsl(180, 100%, 68%)",
            speed: 0.065,
            noiseFreq: 11,
            noiseAmp: 5,
            particleCount: 35,
        }
    };

    let time = 0;
    let morphColor = STATE_CONFIG.IDLE.color;
    let morphColorGlow = STATE_CONFIG.IDLE.colorGlow;
    let morphColorLight = STATE_CONFIG.IDLE.colorLight;
    let morphSpeed = STATE_CONFIG.IDLE.speed;
    let morphFreq = STATE_CONFIG.IDLE.noiseFreq;
    let morphAmp = STATE_CONFIG.IDLE.noiseAmp;

    const particles = [];
    for (let i = 0; i < 45; i++) {
        particles.push({
            x: (Math.random() - 0.5) * 110,
            y: (Math.random() - 0.5) * 110,
            r: Math.random() * 2.5 + 1,
            speedX: (Math.random() - 0.5) * 1.5,
            speedY: (Math.random() - 0.5) * 1.5,
            alpha: Math.random() * 0.5 + 0.3
        });
    }

    function render() {
        const width = canvas.width / window.devicePixelRatio;
        const height = canvas.height / window.devicePixelRatio;
        const centerX = width / 2;
        const centerY = height / 2;
        const baseRadius = 55;

        ctx.clearRect(0, 0, width, height);

        const target = STATE_CONFIG[currentSphereState] || STATE_CONFIG.IDLE;

        morphSpeed += (target.speed - morphSpeed) * 0.08;
        morphFreq += (target.noiseFreq - morphFreq) * 0.08;
        
        let targetAmp = target.noiseAmp;
        if (currentSphereState === "SPEAKING") {
            targetAmp = target.noiseAmp * (0.2 + sphereVolume * 1.8);
        } else if (currentSphereState === "LISTENING") {
            targetAmp = target.noiseAmp * (0.8 + Math.sin(time * 15) * 0.25);
        }
        morphAmp += (targetAmp - morphAmp) * 0.08;

        function interpolateHSL(c1, c2, factor) {
            const getVals = (hslStr) => hslStr.match(/\d+/g).map(Number);
            const v1 = getVals(c1);
            const v2 = getVals(c2);
            const h = Math.round(v1[0] + (v2[0] - v1[0]) * factor);
            const s = Math.round(v1[1] + (v2[1] - v1[1]) * factor);
            const l = Math.round(v1[2] + (v2[2] - v1[2]) * factor);
            return `hsl(${h}, ${s}%, ${l}%)`;
        }

        morphColor = interpolateHSL(morphColor, target.color, 0.1);
        morphColorGlow = interpolateHSL(morphColorGlow, target.colorGlow, 0.1);
        morphColorLight = interpolateHSL(morphColorLight, target.colorLight, 0.1);

        time += morphSpeed;

        // Halo
        const outerGlow = ctx.createRadialGradient(centerX, centerY, baseRadius * 0.2, centerX, centerY, baseRadius * 1.8);
        outerGlow.addColorStop(0, morphColorGlow);
        outerGlow.addColorStop(0.4, morphColorGlow);
        outerGlow.addColorStop(1, "rgba(0, 0, 0, 0)");
        
        ctx.fillStyle = outerGlow;
        ctx.beginPath();
        ctx.arc(centerX, centerY, baseRadius * 1.8, 0, Math.PI * 2);
        ctx.fill();

        // Sphere shape
        ctx.beginPath();
        const numPoints = 100;
        for (let i = 0; i < numPoints; i++) {
            const angle = (i / numPoints) * Math.PI * 2;
            const wave1 = Math.sin(angle * morphFreq + time * 3.5) * morphAmp;
            const wave2 = Math.cos(angle * (morphFreq / 2) - time * 1.5) * (morphAmp * 0.4);
            const radius = baseRadius + wave1 + wave2;
            
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            
            if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.closePath();

        const innerGlow = ctx.createRadialGradient(centerX - baseRadius*0.2, centerY - baseRadius*0.2, baseRadius*0.05, centerX, centerY, baseRadius*1.1);
        innerGlow.addColorStop(0, morphColorLight);
        innerGlow.addColorStop(0.3, morphColor);
        innerGlow.addColorStop(0.85, morphColorGlow);
        innerGlow.addColorStop(1, "rgba(5, 2, 10, 0.95)");

        ctx.fillStyle = innerGlow;
        ctx.shadowBlur = 20;
        ctx.shadowColor = morphColor;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Internal Particles
        ctx.save();
        ctx.beginPath();
        for (let i = 0; i < numPoints; i++) {
            const angle = (i / numPoints) * Math.PI * 2;
            const wave = Math.sin(angle * morphFreq + time * 3.5) * morphAmp + Math.cos(angle * (morphFreq / 2) - time * 1.5) * (morphAmp * 0.4);
            const radius = baseRadius + wave - 3;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.clip();

        particles.slice(0, target.particleCount).forEach(p => {
            p.x += p.speedX * (morphSpeed * 15);
            p.y += p.speedY * (morphSpeed * 15);

            const dist = Math.sqrt(p.x * p.x + p.y * p.y);
            if (dist > baseRadius - 10) {
                p.speedX *= -1;
                p.speedY *= -1;
            }

            ctx.fillStyle = morphColorLight;
            ctx.globalAlpha = p.alpha * (0.6 + Math.sin(time * 3 + p.x) * 0.4);
            ctx.beginPath();
            ctx.arc(centerX + p.x, centerY + p.y, p.r, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.restore();
        ctx.globalAlpha = 1.0;

        animationFrameId = requestAnimationFrame(render);
    }

    document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
            cancelAnimationFrame(animationFrameId);
        } else {
            cancelAnimationFrame(animationFrameId);
            render();
        }
    });

    render();
}

// --- Init App ---
document.addEventListener("DOMContentLoaded", () => {
    initOrbaSphere();
    connectWebSocket();
});
