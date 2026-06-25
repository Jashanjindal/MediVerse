import json, pathlib

# Target notebook
nb_path = pathlib.Path("launch.ipynb")
nb = json.loads(nb_path.read_text(encoding="utf-8"))

# The complete beautiful UI code
source_code = """import gradio as gr

# ── Handlers ────────────────────────────────────────────────────────────────
def ask_assistant(question, area, history):
    area = area or ""
    if not question or not question.strip():
        yield history, ""
        return
    display_q = f"📍 {area} | {question}" if area.strip() else question
    history = history + [
        {"role": "user",      "content": display_q},
        {"role": "assistant", "content": ""},
    ]
    yield history, ""
    
    stream = ask_with_location(question, area=area)
    accumulated = ""
    for token in stream:
        accumulated += token
        history[-1]["content"] = accumulated
        yield history, ""

def clear_chat():
    return [], ""

# ── Custom CSS ──────────────────────────────────────────────────────────────
css = \"\"\"
/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap');

/* Style the body and outer page wrapper */
body {
    font-family: 'Inter', sans-serif !important;
    background-color: #07090f !important;
    color: #c9d1de !important;
}

/* Ambient glow background */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 900px 600px at 10% 0%,   rgba(37,99,235,0.08)  0%, transparent 70%),
        radial-gradient(ellipse 700px 500px at 90% 100%, rgba(6,182,212,0.06)  0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* Hide Gradio default footer */
footer { display: none !important; }

/* ── Entrance animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes statusPulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: .5; transform: scale(.85); }
}

/* Topbar */
.mb-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(7,9,15,0.85);
    backdrop-filter: blur(16px);
    border-radius: 12px;
    margin-bottom: 16px;
    animation: fadeUp .5s ease forwards;
}
.mb-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.mb-brand-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #2563eb, #06b6d4);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1em;
    box-shadow: 0 0 20px rgba(37,99,235,0.35);
    flex-shrink: 0;
}
.mb-brand-name {
    font-family: 'Sora', sans-serif;
    font-size: 1.25em;
    font-weight: 700;
    color: #f0f4ff;
    letter-spacing: -0.3px;
}
.mb-brand-sub {
    font-size: 0.75em;
    color: #5b7094;
    font-weight: 400;
    letter-spacing: 0.2px;
}
.mb-status {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    font-size: 0.8em;
    color: #6b7c96;
    font-weight: 500;
}
.mb-status-dot {
    width: 7px; height: 7px;
    background: #22c55e;
    border-radius: 50%;
    animation: statusPulse 2s ease-in-out infinite;
    flex-shrink: 0;
}
.mb-disclaimer {
    font-size: 0.75em;
    color: #4e5f7c;
    font-weight: 400;
    text-align: center;
}

/* Statsbar */
.mb-statsbar {
    display: flex;
    align-items: center;
    justify-content: space-around;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    background: rgba(255,255,255,0.015);
    border-radius: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;
}
.mb-stat-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    transition: background .2s ease;
    cursor: default;
    border-radius: 8px;
}
.mb-stat-item:hover { background: rgba(255,255,255,0.025); }
.mb-stat-num {
    font-family: 'Sora', sans-serif;
    font-size: 1.3em;
    font-weight: 700;
    color: #e8f0ff;
}
.mb-stat-lbl {
    font-size: 0.72em;
    color: #5b7094;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* Sidebar Components */
.mb-section-label {
    font-size: 0.75em;
    font-weight: 700;
    color: #4a5a78;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
    margin-top: 24px;
}
.mb-section-label:first-child { margin-top: 0; }
.mb-section-divider {
    height: 1px;
    background: rgba(255,255,255,0.05);
    margin: 16px 0;
}

/* Quick Question Buttons styling */
.mb-qbtn button {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    color: #8c9cb8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85em !important;
    font-weight: 500 !important;
    width: 100% !important;
    margin-bottom: 6px !important;
    text-align: left !important;
    padding: 10px 14px !important;
    transition: all .2s ease !important;
}
.mb-qbtn button:hover {
    background: rgba(37,99,235,0.08) !important;
    border-color: rgba(37,99,235,0.28) !important;
    color: #93c5fd !important;
    padding-left: 18px !important;
}

/* Area Tags */
.mb-area-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.mb-area-tag {
    padding: 4px 10px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 6px;
    font-size: 0.78em;
    color: #5b7094;
    font-weight: 500;
    transition: all .2s ease;
    cursor: default;
}
.mb-area-tag:hover {
    background: rgba(6,182,212,0.07);
    border-color: rgba(6,182,212,0.2);
    color: #67e8f9;
}

/* Tech stack items */
.mb-tech-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.85em;
}
.mb-tech-item:last-child { border-bottom: none; }
.mb-tech-key { color: #4a5a78; font-weight: 600; }
.mb-tech-val { color: #8c9cb8; font-weight: 500; }

/* ── Chatbot container and styling ── */
#mb-chatbot {
    border: 1px solid rgba(255,255,255,0.06) !important;
    background: rgba(255,255,255,0.015) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Custom styles for user and assistant messages in Gradio 6 */
#mb-chatbot .message.user > div,
#mb-chatbot [data-testid="user-message"] {
    background: #1e3a5f !important;
    border: 1px solid rgba(37,99,235,0.3) !important;
    color: #dbeafe !important;
    border-radius: 12px 12px 3px 12px !important;
    font-size: 0.92em !important;
}

#mb-chatbot .message.assistant > div,
#mb-chatbot .message.bot > div,
#mb-chatbot [data-testid="assistant-message"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    color: #bfcfe0 !important;
    border-radius: 12px 12px 12px 3px !important;
    font-size: 0.92em !important;
}

/* Styling input fields, textboxes and buttons */
.mb-input-wrap {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

#mb-send {
    background: #2563eb !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 0.9em !important;
    box-shadow: 0 2px 12px rgba(37,99,235,0.35) !important;
    transition: all 0.2s ease !important;
}
#mb-send:hover {
    background: #1d4ed8 !important;
    box-shadow: 0 4px 20px rgba(37,99,235,0.5) !important;
    transform: translateY(-1px) !important;
}

#mb-clear {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    color: #5b7094 !important;
    font-size: 0.8em !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    margin-top: 8px !important;
}
#mb-clear:hover {
    border-color: rgba(239,68,68,0.3) !important;
    color: #f87171 !important;
    background: rgba(239,68,68,0.04) !important;
}
\"\"\"

# ── HTML blocks ──────────────────────────────────────────────────────────────
FONTS_HTML = \"\"\"
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap" rel="stylesheet">
\"\"\"

TOPBAR_HTML = \"\"\"
<div class="mb-topbar">
    <div class="mb-brand">
        <div class="mb-brand-icon">⊕</div>
        <div>
            <div class="mb-brand-name">MediBot Jaipur</div>
            <div class="mb-brand-sub">AI Medicine &amp; Pharmacy Assistant</div>
        </div>
    </div>
    <div class="mb-disclaimer">Educational use only — Not a substitute for medical advice</div>
    <div class="mb-status">
        <div class="mb-status-dot"></div>
        <span>Offline · RAG Active</span>
    </div>
</div>
\"\"\"

STATSBAR_HTML = \"\"\"
<div class="mb-statsbar">
    <div class="mb-stat-item">
        <div>
            <div class="mb-stat-num" style="color: #38bdf8;">383</div>
            <div class="mb-stat-lbl">Jaipur Stores</div>
        </div>
    </div>
    <div class="mb-stat-item">
        <div>
            <div class="mb-stat-num">253K+</div>
            <div class="mb-stat-lbl">Indian Medicines</div>
        </div>
    </div>
    <div class="mb-stat-item">
        <div>
            <div class="mb-stat-num">16K+</div>
            <div class="mb-stat-lbl">Medical Q&amp;As</div>
        </div>
    </div>
    <div class="mb-stat-item">
        <div>
            <div class="mb-stat-num">40</div>
            <div class="mb-stat-lbl">Areas Covered</div>
        </div>
    </div>
    <div class="mb-stat-item">
        <div>
            <div class="mb-stat-num" style="color: #4ade80;">100%</div>
            <div class="mb-stat-lbl">Offline &amp; Free</div>
        </div>
    </div>
    <div class="mb-stat-item">
        <div>
            <div class="mb-stat-num">Mistral</div>
            <div class="mb-stat-lbl">Active Model</div>
        </div>
    </div>
</div>
\"\"\"

SIDEBAR_HTML = \"\"\"
<div class="mb-sidebar-wrap">
    <div class="mb-section-label">Quick Questions</div>
\"\"\"

SIDEBAR_BOTTOM_HTML = \"\"\"
    <div class="mb-section-divider"></div>
    <div class="mb-section-label">Jaipur Areas</div>
    <div class="mb-area-wrap">
        <span class="mb-area-tag">Malviya Nagar</span>
        <span class="mb-area-tag">Vaishali Nagar</span>
        <span class="mb-area-tag">C-Scheme</span>
        <span class="mb-area-tag">Mansarovar</span>
        <span class="mb-area-tag">Tonk Road</span>
        <span class="mb-area-tag">Sanganer</span>
        <span class="mb-area-tag">Jagatpura</span>
        <span class="mb-area-tag">Ajmer Road</span>
        <span class="mb-area-tag">Raja Park</span>
        <span class="mb-area-tag">Bani Park</span>
    </div>
    <div class="mb-section-divider"></div>
    <div class="mb-section-label">Stack</div>
    <div class="mb-tech-item"><span class="mb-tech-key">LLM</span><span class="mb-tech-val">Mistral / Llama3</span></div>
    <div class="mb-tech-item"><span class="mb-tech-key">Embeddings</span><span class="mb-tech-val">MiniLM L6</span></div>
    <div class="mb-tech-item"><span class="mb-tech-key">Vector Store</span><span class="mb-tech-val">ChromaDB</span></div>
    <div class="mb-tech-item"><span class="mb-tech-key">Location</span><span class="mb-tech-val">GeoPy</span></div>
    <div class="mb-tech-item"><span class="mb-tech-key">Framework</span><span class="mb-tech-val">LangChain</span></div>
</div>
\"\"\"

PLACEHOLDER_HTML = (
    "<div style='text-align:center;padding:80px 20px;'>"
    "<svg width='40' height='40' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.3)' "
    "stroke-width='1.5' style='margin:0 auto 16px;display:block;'>"
    "<path stroke-linecap='round' stroke-linejoin='round' "
    "d='M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z'/>"
    "</svg>"
    "<p style='color:#a0aec0;font-size:1em;font-weight:600;margin-bottom:6px;'>No messages yet</p>"
    "<p style='color:#718096;font-size:.85em;line-height:1.6;'>"
    "Ask about medicine prices, compositions,<br>uses, or nearby pharmacies in Jaipur."
    "</p></div>"
)

# ── Build UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(title="MediBot Jaipur") as demo:

    gr.HTML(FONTS_HTML)
    gr.HTML(TOPBAR_HTML)
    gr.HTML(STATSBAR_HTML)

    with gr.Row(equal_height=True):

        # ── Chat column ────────────────────────────────────────────────
        with gr.Column(scale=3, elem_classes="mb-chat-section"):

            chatbot = gr.Chatbot(
                height=460,
                label="",
                elem_id="mb-chatbot",
                show_label=False,
                placeholder=PLACEHOLDER_HTML,
            )

            with gr.Group(elem_classes="mb-input-wrap"):
                area_box = gr.Textbox(
                    placeholder="Your locality in Jaipur  —  e.g. Malviya Nagar, C-Scheme, Vaishali Nagar",
                    label="Location",
                    lines=1,
                )
                with gr.Row():
                    question_box = gr.Textbox(
                        placeholder="Ask about a medicine, price, composition, dosage, or nearby pharmacy ...",
                        label="",
                        scale=5,
                        container=False,
                        lines=1,
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1, elem_id="mb-send")
                clear_btn = gr.Button("Clear conversation", size="sm", elem_id="mb-clear")

        # ── Sidebar ────────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=280):

            gr.HTML(SIDEBAR_HTML)

            q1 = gr.Button("Paracetamol — uses & dosage",      size="sm", elem_classes="mb-qbtn")
            q2 = gr.Button("Price of Augmentin 625 tablet",    size="sm", elem_classes="mb-qbtn")
            q3 = gr.Button("Common medicines for fever",        size="sm", elem_classes="mb-qbtn")
            q4 = gr.Button("Azithromycin side effects",         size="sm", elem_classes="mb-qbtn")
            q5 = gr.Button("Medicines containing Amoxicillin",  size="sm", elem_classes="mb-qbtn")
            q6 = gr.Button("Safe sleep-aid medicines",          size="sm", elem_classes="mb-qbtn")

            gr.HTML(SIDEBAR_BOTTOM_HTML)

    # ── Wiring ────────────────────────────────────────────────────────────────
    submit_btn.click(
        ask_assistant,
        inputs=[question_box, area_box, chatbot],
        outputs=[chatbot, question_box],
    )
    question_box.submit(
        ask_assistant,
        inputs=[question_box, area_box, chatbot],
        outputs=[chatbot, question_box],
    )
    clear_btn.click(clear_chat, outputs=[chatbot, question_box])

    def click_q1(area, history):
        yield from ask_assistant("What is Paracetamol used for and what is the dosage?", area, history)
    def click_q2(area, history):
        yield from ask_assistant("Price of Augmentin 625?", area, history)
    def click_q3(area, history):
        yield from ask_assistant("What medicines are used for fever?", area, history)
    def click_q4(area, history):
        yield from ask_assistant("Side effects of Azithromycin?", area, history)
    def click_q5(area, history):
        yield from ask_assistant("What medicines contain Amoxicillin?", area, history)
    def click_q6(area, history):
        yield from ask_assistant("What medicines help with sleep?", area, history)

    q1.click(click_q1, inputs=[area_box, chatbot], outputs=[chatbot, question_box])
    q2.click(click_q2, inputs=[area_box, chatbot], outputs=[chatbot, question_box])
    q3.click(click_q3, inputs=[area_box, chatbot], outputs=[chatbot, question_box])
    q4.click(click_q4, inputs=[area_box, chatbot], outputs=[chatbot, question_box])
    q5.click(click_q5, inputs=[area_box, chatbot], outputs=[chatbot, question_box])
    q6.click(click_q6, inputs=[area_box, chatbot], outputs=[chatbot, question_box])

demo.launch(css=css)"""

# Convert to list of notebook lines
lines = source_code.split("\n")
nb_lines = [line + "\n" for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])

# Find and patch the cell
target_id = "d939ddd2"
patched = False
for cell in nb["cells"]:
    if cell.get("id") == target_id:
        cell["source"] = nb_lines
        cell["outputs"] = []
        cell["execution_count"] = None
        patched = True
        break

if patched:
    nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print("SUCCESS: launch.ipynb successfully updated with stunning Gradio 6 UI!")
else:
    print("ERROR: Could not find cell with ID 'd939ddd2'")
