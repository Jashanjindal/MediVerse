"""
Patches launch.ipynb cell 4 to fix two Gradio errors:
  1. bubble_full_width is not a valid kwarg in newer Gradio
  2. Chat history must use {"role":..., "content":...} dicts, not (q, a) tuples
"""
import json, re, pathlib

nb_path = pathlib.Path(__file__).parent / "launch.ipynb"
nb = json.loads(nb_path.read_text(encoding="utf-8"))

NEW_CELL4_SOURCE = [
    "import gradio as gr\n",
    "\n",
    "def ask_assistant(question, area, history):\n",
    "    area = area or \"\"\n",
    "    if not question or not question.strip():\n",
    "        return history, \"\"\n",
    "    response = ask_with_location(question, area=area)\n",
    "    display_q = f\"📍 {area} | {question}\" if area.strip() else question\n",
    "    history = history + [\n",
    "        {\"role\": \"user\",      \"content\": display_q},\n",
    "        {\"role\": \"assistant\", \"content\": response},\n",
    "    ]\n",
    "    return history, \"\"\n",
    "\n",
    "def clear_chat():\n",
    "    return [], \"\"\n",
    "\n",
    "css = \"\"\"\n",
    "body { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e) !important; }\n",
    "footer { display: none !important }\n",
    "\"\"\"\n",
    "\n",
    "with gr.Blocks(css=css, title=\"💊 MediBot Jaipur\") as demo:\n",
    "    gr.HTML(\"\"\"\n",
    "    <div style=\"text-align:center; padding:30px 0 10px 0;\">\n",
    "        <div style=\"font-size:3em;\">💊</div>\n",
    "        <div style=\"font-size:2.2em; font-weight:900;\n",
    "                    background:linear-gradient(90deg,#00c6ff,#0072ff);\n",
    "                    -webkit-background-clip:text;\n",
    "                    -webkit-text-fill-color:transparent;\">\n",
    "            MediBot Jaipur\n",
    "        </div>\n",
    "        <div style=\"color:#a0aec0; margin-top:5px;\">\n",
    "            Medicines + Nearest Medical Stores in Jaipur 🏙️\n",
    "        </div>\n",
    "        <div style=\"margin-top:10px; padding:8px 20px;\n",
    "                    background:rgba(255,100,100,0.15);\n",
    "                    border:1px solid #ff6464; border-radius:20px;\n",
    "                    display:inline-block; color:#ff6464; font-size:0.9em;\">\n",
    "            ⚠️ Educational purposes only — Always consult a real doctor!\n",
    "        </div>\n",
    "    </div>\n",
    "    \"\"\")\n",
    "    gr.HTML(\"\"\"\n",
    "    <div style=\"display:flex; justify-content:center; gap:15px; margin:20px 0;\">\n",
    "        <div style=\"background:rgba(0,198,255,0.1); border:1px solid #00c6ff;\n",
    "                    border-radius:12px; padding:12px 20px; text-align:center;\">\n",
    "            <div style=\"font-size:1.5em; font-weight:bold; color:#00c6ff;\">383</div>\n",
    "            <div style=\"color:#a0aec0; font-size:0.85em;\">Jaipur Stores</div>\n",
    "        </div>\n",
    "        <div style=\"background:rgba(0,198,255,0.1); border:1px solid #00c6ff;\n",
    "                    border-radius:12px; padding:12px 20px; text-align:center;\">\n",
    "            <div style=\"font-size:1.5em; font-weight:bold; color:#00c6ff;\">253K+</div>\n",
    "            <div style=\"color:#a0aec0; font-size:0.85em;\">Indian Medicines</div>\n",
    "        </div>\n",
    "        <div style=\"background:rgba(0,198,255,0.1); border:1px solid #00c6ff;\n",
    "                    border-radius:12px; padding:12px 20px; text-align:center;\">\n",
    "            <div style=\"font-size:1.5em; font-weight:bold; color:#00c6ff;\">16K+</div>\n",
    "            <div style=\"color:#a0aec0; font-size:0.85em;\">Medical Q&amp;As</div>\n",
    "        </div>\n",
    "        <div style=\"background:rgba(118,75,162,0.2); border:1px solid #764ba2;\n",
    "                    border-radius:12px; padding:12px 20px; text-align:center;\">\n",
    "            <div style=\"font-size:1.5em; font-weight:bold; color:#b794f4;\">100%</div>\n",
    "            <div style=\"color:#a0aec0; font-size:0.85em;\">Offline &amp; Free</div>\n",
    "        </div>\n",
    "    </div>\n",
    "    \"\"\")\n",
    "\n",
    "    with gr.Row():\n",
    "        with gr.Column(scale=3):\n",
    "            # type='messages' is required in Gradio >=4.x for dict-based history\n",
    "            chatbot = gr.Chatbot(\n",
    "                height=350,\n",
    "                label=\"💬 Chat with MediBot Jaipur\",\n",
    "                type=\"messages\"\n",
    "            )\n",
    "            area_box = gr.Textbox(\n",
    "                placeholder=\"📍 Your area in Jaipur (e.g. Malviya Nagar, Vaishali Nagar, C-Scheme...)\",\n",
    "                label=\"📍 Your Location\"\n",
    "            )\n",
    "            with gr.Row():\n",
    "                question_box = gr.Textbox(\n",
    "                    placeholder=\"💊 Ask about any medicine...\",\n",
    "                    label=\"\", scale=5, container=False\n",
    "                )\n",
    "                submit_btn = gr.Button(\"Ask 🚀\", variant=\"primary\", scale=1)\n",
    "            clear_btn = gr.Button(\"🗑️ Clear Chat\", size=\"sm\")\n",
    "\n",
    "        with gr.Column(scale=1):\n",
    "            gr.Markdown(\"### ⚡ Quick Questions\")\n",
    "            q1 = gr.Button(\"💊 Paracetamol uses?\", size=\"sm\")\n",
    "            q2 = gr.Button(\"💰 Price of Augmentin 625?\", size=\"sm\")\n",
    "            q3 = gr.Button(\"🤒 Medicines for fever?\", size=\"sm\")\n",
    "            q4 = gr.Button(\"⚠️ Azithromycin side effects?\", size=\"sm\")\n",
    "            q5 = gr.Button(\"🔬 Medicines with Amoxicillin?\", size=\"sm\")\n",
    "            q6 = gr.Button(\"😴 Medicines for sleep?\", size=\"sm\")\n",
    "            gr.Markdown(\"---\")\n",
    "            gr.Markdown(\"\"\"\n",
    "### 📍 Popular Areas\n",
    "Malviya Nagar • Vaishali Nagar\n",
    "C-Scheme • Mansarovar\n",
    "Tonk Road • Sanganer\n",
    "Jagatpura • Ajmer Road\n",
    "            \"\"\")\n",
    "            gr.Markdown(\"\"\"\n",
    "### 🔧 Tech Stack\n",
    "🤖 **LLM:** Mistral / Llama3\n",
    "🔍 **Search:** MiniLM\n",
    "🗄️ **DB:** ChromaDB\n",
    "📍 **Location:** GeoPy\n",
    "🦜 **Framework:** LangChain\n",
    "            \"\"\")\n",
    "\n",
    "    # ── Event wiring ──────────────────────────────────────────────────────────\n",
    "    submit_btn.click(\n",
    "        ask_assistant,\n",
    "        inputs=[question_box, area_box, chatbot],\n",
    "        outputs=[chatbot, question_box]\n",
    "    )\n",
    "    question_box.submit(\n",
    "        ask_assistant,\n",
    "        inputs=[question_box, area_box, chatbot],\n",
    "        outputs=[chatbot, question_box]\n",
    "    )\n",
    "    clear_btn.click(clear_chat, outputs=[chatbot, question_box])\n",
    "\n",
    "    q1.click(lambda a, h: ask_assistant(\"What is Paracetamol used for?\", a, h),\n",
    "             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n",
    "    q2.click(lambda a, h: ask_assistant(\"Price of Augmentin 625?\", a, h),\n",
    "             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n",
    "    q3.click(lambda a, h: ask_assistant(\"What medicines are used for fever?\", a, h),\n",
    "             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n",
    "    q4.click(lambda a, h: ask_assistant(\"Side effects of Azithromycin?\", a, h),\n",
    "             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n",
    "    q5.click(lambda a, h: ask_assistant(\"What medicines contain Amoxicillin?\", a, h),\n",
    "             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n",
    "    q6.click(lambda a, h: ask_assistant(\"What medicines help with sleep?\", a, h),\n",
    "             inputs=[area_box, chatbot], outputs=[chatbot, question_box])\n",
    "\n",
    "demo.launch()\n",
]

# Find cell with id "d939ddd2" (cell 4 - the Gradio UI cell)
target_id = "d939ddd2"
patched = False
for cell in nb["cells"]:
    if cell.get("id") == target_id:
        cell["source"] = NEW_CELL4_SOURCE
        cell["outputs"] = []          # clear stale error outputs
        cell["execution_count"] = None
        patched = True
        print(f"✅ Patched cell '{target_id}'")
        break

if not patched:
    print("❌ Could not find target cell. Searching by content...")
    for i, cell in enumerate(nb["cells"]):
        src = "".join(cell.get("source", []))
        if "bubble_full_width" in src or "history + [(display_q" in src or "gr.Chatbot" in src:
            cell["source"] = NEW_CELL4_SOURCE
            cell["outputs"] = []
            cell["execution_count"] = None
            print(f"✅ Patched cell index {i}")
            patched = True
            break

if not patched:
    print("❌ Could not find the Gradio cell to patch!")
else:
    nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Saved patched notebook → {nb_path}")
    print("\nChanges made:")
    print("  • gr.Chatbot(..., type='messages') added")
    print("  • history now uses {'role':..., 'content':...} dicts")
    print("  • bubble_full_width removed (not supported in newer Gradio)")
    print("  • Stale error outputs cleared")
