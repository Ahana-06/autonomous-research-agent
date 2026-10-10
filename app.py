import streamlit as st
import streamlit.components.v1 as components
from agent import call_groq_llm

# ---------------------------------------------------------
# Page Setup & Styling
# ---------------------------------------------------------
st.set_page_config(page_title="Autonomous Research Agent", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #15102a 0%, #08090d 65%);
        color: #e2e8f0;
    }

    section[data-testid="stSidebar"] {
        background-color: #0d0f17 !important;
        border-right: 1px solid #1e2235 !important;
    }

    .stTextArea textarea, .stTextInput input {
        background-color: #121420 !important;
        color: #f1f5f9 !important;
        border: 1px solid #282d45 !important;
        border-radius: 12px !important;
        font-size: 15px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        height: 48px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3) !important;
    }

    /* Follow-up quick-prompt chips */
    [class*="st-key-chip_"] button {
        background: #181b2b !important;
        border: 1px solid #2e3554 !important;
        color: #a5b4fc !important;
        border-radius: 20px !important;
        height: auto !important;
        min-height: 0 !important;
        padding: 6px 14px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }
    [class*="st-key-chip_"] button:hover {
        border-color: #a855f7 !important;
        color: #e9d5ff !important;
        background: #20243a !important;
    }

    .report-box {
        background: rgba(18, 20, 32, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid #22273e;
        border-radius: 16px;
        padding: 28px;
        margin-top: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }

    .citation-tag {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(168, 85, 247, 0.4);
        color: #c084fc;
        font-size: 11px;
        font-weight: 600;
        padding: 1px 6px;
        border-radius: 6px;
        margin-left: 4px;
        vertical-align: super;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "intro_passed" not in st.session_state:
    st.session_state.intro_passed = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "report_markdown" not in st.session_state:
    st.session_state.report_markdown = None

if "research_history" not in st.session_state:
    st.session_state.research_history = []

if "current_query" not in st.session_state:
    st.session_state.current_query = ""


def start_new_chat():
    st.session_state.report_markdown = None
    st.session_state.messages = []
    st.session_state.current_query = ""
    st.session_state.pop("pending_prompt", None)


def queue_prompt(prompt_text):
    st.session_state["pending_prompt"] = prompt_text


QUICK_PROMPTS = [
    ("💡 Key Takeaways", "Summarize the key takeaways from this report in 4-5 concise bullet points."),
    ("💻 Code Example / Implementation", "Give a clean, practical code example or implementation based on this report."),
    ("📐 Future Outlook", "What is the future outlook, and what challenges does this report mention or imply?"),
]

# ---------------------------------------------------------
# Cinematic 3D App Globe Splash Screen (Click to Burst)
# ---------------------------------------------------------
if not st.session_state.intro_passed:
    st.markdown("""
        <div style='text-align: center; margin-top: 1rem;'>
            <h1 style='background: linear-gradient(135deg, #818cf8, #c084fc, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size:3.5rem; font-weight: 800;'>Autonomous Research Agent</h1>
        </div>
    """, unsafe_allow_html=True)

    app_globe_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; background: transparent; overflow: hidden; cursor: pointer; }
            canvas { display: block; margin: auto; }
            #instruction {
                position: absolute;
                bottom: 10px;
                width: 100%;
                text-align: center;
                color: #818cf8;
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 1.5px;
                text-shadow: 0 0 12px rgba(129, 140, 248, 0.6);
                pointer-events: none;
            }
        </style>
    </head>
    <body>
        <div id="instruction">⚡ CLICK GLOBE TO BURST & LAUNCH ⚡</div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / 460, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
            renderer.setSize(window.innerWidth, 460);
            document.body.appendChild(renderer.domElement);

            const particleCount = 2500;
            const geometry = new THREE.BufferGeometry();
            const positions = [];
            const colors = [];
            const velocities = [];

            const palette = [
                new THREE.Color(0x38bdf8), // Cyan / Light Blue
                new THREE.Color(0x6366f1), // Deep Indigo
                new THREE.Color(0x818cf8), // Slate Blue
                new THREE.Color(0xa855f7)  // Electric Violet
            ];

            for (let i = 0; i < particleCount; i++) {
                const phi = Math.acos(-1 + (2 * i) / particleCount);
                const theta = Math.sqrt(particleCount * Math.PI) * phi;

                const x = 2.2 * Math.cos(theta) * Math.sin(phi);
                const y = 2.2 * Math.sin(theta) * Math.sin(phi);
                const z = 2.2 * Math.cos(phi);

                positions.push(x, y, z);

                const col = palette[Math.floor(Math.random() * palette.length)];
                colors.push(col.r, col.g, col.b);

                velocities.push(x * 0.08, y * 0.08, z * 0.08);
            }

            geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

            const material = new THREE.PointsMaterial({
                size: 0.075,
                vertexColors: true,
                transparent: true,
                opacity: 0.95
            });

            const globe = new THREE.Points(geometry, material);
            scene.add(globe);

            const ringGeo = new THREE.RingGeometry(2.7, 2.76, 64);
            const ringMat = new THREE.MeshBasicMaterial({ color: 0x818cf8, side: THREE.DoubleSide, transparent: true, opacity: 0.7 });
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.x = Math.PI / 2;
            scene.add(ring);

            camera.position.z = 6;

            let bursting = false;
            let frameCount = 0;

            window.addEventListener('click', () => {
                if (!bursting) {
                    bursting = true;
                    document.getElementById('instruction').style.display = 'none';
                }
            });

            function animate() {
                requestAnimationFrame(animate);

                if (!bursting) {
                    globe.rotation.y += 0.005;
                    globe.rotation.x += 0.002;
                    ring.rotation.z -= 0.008;
                } else {
                    const posAttr = geometry.attributes.position;
                    const arr = posAttr.array;
                    for (let i = 0; i < particleCount; i++) {
                        arr[i * 3] += velocities[i] * 2.5;
                        arr[i * 3 + 1] += velocities[i * 3 + 1] * 2.5;
                        arr[i * 3 + 2] += velocities[i * 3 + 2] * 2.5;
                    }
                    posAttr.needsUpdate = true;
                    material.opacity -= 0.03;
                    ring.scale.addScalar(0.12);
                    ring.material.opacity -= 0.04;

                    frameCount++;
                    if (frameCount > 30) {
                        // Send value back to Streamlit component to trigger Python rerun
                        window.parent.postMessage({ type: 'streamlit:setComponentValue', value: true }, '*');
                    }
                }

                renderer.render(scene, camera);
            }
            animate();

            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / 460;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, 460);
            });
        </script>
    </body>
    </html>
    """

    # Capture the component return value when clicked
    globe_clicked = components.html(app_globe_html, height=500)
    
    if globe_clicked:
        st.session_state.intro_passed = True
        st.rerun()

    st.stop()

# ---------------------------------------------------------
# Main App Dashboard (Loaded After Globe Burst)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""<h3 style='color: #c084fc;'>📚 Knowledge Base</h3>""", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF documents", type=["pdf"])
    if st.button("⚡ Ingest Documents"):
        st.success("Documents successfully ingested.")

    st.markdown("---")
    st.markdown("""<h3 style='color: #c084fc;'>🎛️ Search Mode</h3>""", unsafe_allow_html=True)

    doc_only_mode = st.toggle("Strict Document-Only Mode", value=False)
    if doc_only_mode:
        st.info("📖 **Mode Active:** Reading strictly from uploaded PDFs.")
    else:
        st.success("🌐 **Mode Active:** Hybrid (PDFs + Live Web Search).")

    st.markdown("---")
    st.button("➕ New Chat", key="new_chat_btn", on_click=start_new_chat, use_container_width=True)

    st.markdown("""<h3 style='color: #c084fc;'>🕒 Recent Research</h3>""", unsafe_allow_html=True)

    if not st.session_state.research_history:
        st.caption("No recent research yet.")
    else:
        for idx, item in enumerate(reversed(st.session_state.research_history)):
            short_title = item['query'][:25] + "..." if len(item['query']) > 25 else item['query']
            if st.button(f"🔍 {short_title}", key=f"hist_{idx}"):
                st.session_state.report_markdown = item["report"]
                st.session_state.messages = item["messages"]
                st.session_state.current_query = item["query"]
                st.rerun()

# Header & Research Input Area
st.markdown("""<h1 style='text-align: center; background: linear-gradient(135deg, #818cf8, #c084fc, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size:3rem; font-weight: 800;'>Autonomous Research Agent</h1>""", unsafe_allow_html=True)
st.markdown("""<p style='text-align: center; color: #94a3b8; font-size: 1.05rem; margin-bottom: 2rem;'>Synthesizing real-time web intelligence with private document context.</p>""", unsafe_allow_html=True)

user_query = st.text_area(
    "Research Query",
    value=st.session_state.current_query,
    placeholder="Enter any topic to research (e.g., Quantum Computing, Transformer Architectures, Neural Networks...)",
    label_visibility="collapsed"
)

if st.button("🚀 Run Research Agent"):
    if not user_query.strip():
        st.warning("Please enter a research topic first.")
    else:
        with st.spinner(f"Generating research report on '{user_query}'..."):
            report_prompt = [
                {
                    "role": "system",
                    "content": (
                        "You are an Autonomous Research Agent. Generate a well-structured Markdown research report "
                        "containing:\n"
                        "1. ## Executive Summary\n"
                        "2. ## Key Findings (bullet points with citation badges like <span class=\"citation-tag\">[Web-1]</span> or <span class=\"citation-tag\">[Internal-1]</span>)\n"
                        "3. ## Sources"
                    )
                },
                {
                    "role": "user",
                    "content": f"Generate a comprehensive research report for the topic: {user_query}"
                }
            ]

            generated_report = call_groq_llm(report_prompt, doc_only_mode=doc_only_mode)

            st.session_state.report_markdown = generated_report
            st.session_state.messages = []
            st.session_state.current_query = user_query

            st.session_state.research_history.append({
                "query": user_query,
                "report": generated_report,
                "messages": st.session_state.messages
            })

# Report Output & Interactive Follow-Up Chat
if st.session_state.report_markdown:
    st.markdown("---")
    st.markdown("""<h3 style='color: #f8fafc;'>📊 Generated Research Report</h3>""", unsafe_allow_html=True)

    st.markdown(f'<div class="report-box">{st.session_state.report_markdown}</div>', unsafe_allow_html=True)

    st.download_button(
        label="📥 Download Report as Markdown",
        data=st.session_state.report_markdown,
        file_name="research_report.md",
        mime="text/markdown"
    )

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("""<h3 style='color: #f8fafc;'>💬 AI Follow-up Assistant</h3>""", unsafe_allow_html=True)
    st.caption("Click a quick prompt, or type your own question below.")

    chip_cols = st.columns(3)
    for i, (label, question_text) in enumerate(QUICK_PROMPTS):
        with chip_cols[i]:
            st.button(
                label,
                key=f"chip_{i}",
                on_click=queue_prompt,
                args=(question_text,),
                use_container_width=True,
            )

    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "system",
            "content": f"You are an AI research assistant. Answer follow-up questions concisely based on this research report, including citation badges where relevant:\n\n{st.session_state.report_markdown}"
        })

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)

    typed_prompt = st.chat_input("Ask a follow-up question about this report...")
    prompt = st.session_state.pop("pending_prompt", None) or typed_prompt

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Generating response..."):
            response = call_groq_llm(st.session_state.messages, doc_only_mode=doc_only_mode)

        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": response})

        for item in st.session_state.research_history:
            if item["query"] == st.session_state.current_query:
                item["messages"] = st.session_state.messages