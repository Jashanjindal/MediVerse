import json, pathlib

nb_path = pathlib.Path("launch.ipynb")
nb = json.loads(nb_path.read_text(encoding="utf-8"))

# The complete fixed cell source - Gradio 6.x compatible
# Key changes:
#   - NO type="messages" param (not in Gradio 6.x Chatbot signature)
#   - NO bubble_full_width param (also gone)
#   - history uses {"role":..., "content":...} dicts (required by Gradio 6.x)

source = (
    'import gradio as gr\n'
    '\n'
    'def ask_assistant(question, area, history):\n'
    '    area = area or ""\n'
    '    if not question or not question.strip():\n'
    '        return history, ""\n'
    '    response = ask_with_location(question, area=area)\n'
    '    display_q = f"\U0001f4cd {area} | {question}" if area.strip() else question\n'
    '    history = history + [\n'
    '        {"role": "user",      "content": display_q},\n'
    '        {"role": "assistant", "content": response},\n'
    '    ]\n'
    '    return history, ""\n'
    '\n'
    'def clear_chat():\n'
    '    return [], ""\n'
    '\n'
    'css = """\n'
    'body { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e) !important; }\n'
    'footer { display: none !important }\n'
    '"""\n'
    '\n'
    'with gr.Blocks(css=css, title="\U0001f48a MediBot Jaipur") as demo:\n'
    '    gr.HTML("""\n'
    '    <div style="text-align:center; padding:30px 0 10px 0;">\n'
    '        <div style="font-size:3em;">\U0001f48a</div>\n'
    '        <div style="font-size:2.2em; font-weight:900;\n'
    '                    background:linear-gradient(90deg,#00c6ff,#0072ff);\n'
    '                    -webkit-background-clip:text;\n'
    '                    -webkit-text-fill-color:transparent;">\n'
    '            MediBot Jaipur\n'
    '        </div>\n'
    '        <div style="color:#a0aec0; margin-top:5px;">\n'
    '            Medicines + Nearest Medical Stores in Jaipur \U0001f3d9\ufe0f\n'
    '        </div>\n'
    '        <div style="margin-top:10px; padding:8px 20px;\n'
    '                    background:rgba(255,100,100,0.15);\n'
    '                    border:1px solid #ff6464; border-radius:20px;\n'
    '                    display:inline-block; color:#ff6464; font-size:0.9em;">\n'
    '            \u26a0\ufe0f Educational purposes only \u2014 Always consult a real doctor!\n'
    '        </div>\n'
    '    </div>\n'
    '    """)\n'
    '    gr.HTML("""\n'
    '    <div style="display:flex; justify-content:center; gap:15px; margin:20px 0;">\n'
    '        <div style="background:rgba(0,198,255,0.1); border:1px solid #00c6ff;\n'
    '                    border-radius:12px; padding:12px 20px; text-align:center;">\n'
    '            <div style="font-size:1.5em; font-weight:bold; color:#00c6ff;">383</div>\n'
    '            <div style="color:#a0aec0; font-size:0.85em;">Jaipur Stores</div>\n'
    '        </div>\n'
    '        <div style="background:rgba(0,198,255,0.1); border:1px solid #00c6ff;\n'
    '                    border-radius:12px; padding:12px 20px; text-align:center;">\n'
    '            <div style="font-size:1.5em; font-weight:bold; color:#00c6ff;">253K+</div>\n'
    '            <div style="color:#a0aec0; font-size:0.85em;">Indian Medicines</div>\n'
    '        </div>\n'
    '        <div style="background:rgba(0,198,255,0.1); border:1px solid #00c6ff;\n'
    '                    border-radius:12px; padding:12px 20px; text-align:center;">\n'
    '            <div style="font-size:1.5em; font-weight:bold; color:#00c6ff;">16K+</div>\n'
    '            <div style="color:#a0aec0; font-size:0.85em;">Medical Q&amp;As</div>\n'
    '        </div>\n'
    '        <div style="background:rgba(118,75,162,0.2); border:1px solid #764ba2;\n'
    '                    border-radius:12px; padding:12px 20px; text-align:center;">\n'
    '            <div style="font-size:1.5em; font-weight:bold; color:#b794f4;">100%</div>\n'
    '            <div style="color:#a0aec0; font-size:0.85em;">Offline &amp; Free</div>\n'
    '        </div>\n'
    '    </div>\n'
    '    """)\n'
    '\n'
    '    with gr.Row():\n'
    '        with gr.Column(scale=3):\n'
    '            chatbot = gr.Chatbot(\n'
    '                height=350,\n'
    '                label="\U0001f4ac Chat with MediBot Jaipur"\n'
    '            )\n'
    '            area_box = gr.Textbox(\n'
    '                placeholder="\U0001f4cd Your area in Jaipur (e.g. Malviya Nagar, Vaishali Nagar, C-Scheme...)",\n'
    '                label="\U0001f4cd Your Location"\n'
    '            )\n'
    '            with gr.Row():\n'
    '                question_box = gr.Textbox(\n'
    '                    placeholder="\U0001f48a Ask about any medicine...",\n'
    '                    label="", scale=5, container=False\n'
    '                )\n'
    '                submit_btn = gr.Button("Ask \U0001f680", variant="primary", scale=1)\n'
    '            clear_btn = gr.Button("\U0001f5d1\ufe0f Clear Chat", size="sm")\n'
    '\n'
    '        with gr.Column(scale=1):\n'
    '            gr.Markdown("### \u26a1 Quick Questions")\n'
    '            q1 = gr.Button("\U0001f48a Paracetamol uses?", size="sm")\n'
    '            q2 = gr.Button("\U0001f4b0 Price of Augmentin 625?", size="sm")\n'
    '            q3 = gr.Button("\U0001f915 Medicines for fever?", size="sm")\n'
    '            q4 = gr.Button("\u26a0\ufe0f Azithromycin side effects?", size="sm")\n'
    '            q5 = gr.Button("\U0001f52c Medicines with Amoxicillin?", size="sm")\n'
    '            q6 = gr.Button("\U0001f634 Medicines for sleep?", size="sm")\n'
    '            gr.Markdown("---")\n'
    '            gr.Markdown("""\n'
    '### \U0001f4cd Popular Areas\n'
    'Malviya Nagar \u2022 Vaishali Nagar\n'
    'C-Scheme \u2022 Mansarovar\n'
    'Tonk Road \u2022 Sanganer\n'
    'Jagatpura \u2022 Ajmer Road\n'
    '            """)\n'
    '            gr.Markdown("""\n'
    '### \U0001f527 Tech Stack\n'
    '\U0001f916 **LLM:** Mistral / Llama3\n'
    '\U0001f50d **Search:** MiniLM\n'
    '\U0001f5c4\ufe0f **DB:** ChromaDB\n'
    '\U0001f4cd **Location:** GeoPy\n'
    '\U0001f99c **Framework:** LangChain\n'
    '            """)\n'
    '\n'
    '    submit_btn.click(\n'
    '        ask_assistant,\n'
    '        inputs=[question_box, area_box, chatbot],\n'
    '        outputs=[chatbot, question_box]\n'
    '    )\n'
    '    question_box.submit(\n'
    '        ask_assistant,\n'
    '        inputs=[question_box, area_box, chatbot],\n'
    '        outputs=[chatbot, question_box]\n'
    '    )\n'
    '    clear_btn.click(clear_chat, outputs=[chatbot, question_box])\n'
    '\n'
    '    q1.click(lambda a, h: ask_assistant("What is Paracetamol used for?", a, h),\n'
    '             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n'
    '    q2.click(lambda a, h: ask_assistant("Price of Augmentin 625?", a, h),\n'
    '             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n'
    '    q3.click(lambda a, h: ask_assistant("What medicines are used for fever?", a, h),\n'
    '             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n'
    '    q4.click(lambda a, h: ask_assistant("Side effects of Azithromycin?", a, h),\n'
    '             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n'
    '    q5.click(lambda a, h: ask_assistant("What medicines contain Amoxicillin?", a, h),\n'
    '             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n'
    '    q6.click(lambda a, h: ask_assistant("What medicines help with sleep?", a, h),\n'
    '             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n'
    '\n'
    'demo.launch()\n'
)

# Convert to notebook source list
lines = source.split("\n")
source_lines = [line + "\n" for line in lines[:-1]]
if lines[-1]:
    source_lines.append(lines[-1])

target_id = "d939ddd2"
patched = False
for cell in nb["cells"]:
    if cell.get("id") == target_id:
        cell["source"] = source_lines
        cell["outputs"] = []
        cell["execution_count"] = None
        patched = True
        break

if patched:
    nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print("SUCCESS: Notebook patched and saved.")
    print("- Removed type='messages' (not in Gradio 6.x Chatbot)")
    print("- Removed bubble_full_width (not supported)")
    print("- History uses {'role':..., 'content':...} dicts (Gradio 6.x native format)")
else:
    print("FAILED: Could not find cell d939ddd2")
