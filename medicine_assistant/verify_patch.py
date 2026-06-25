import json, pathlib, re

nb = json.loads(pathlib.Path("launch.ipynb").read_text(encoding="utf-8"))
for cell in nb["cells"]:
    if cell.get("id") == "d939ddd2":
        src = "".join(cell["source"])

        # Gradio 6.x: NO type param, NO bubble_full_width, YES dict history
        checks = [
            ("type=" not in src or 'type="messages"' not in src,
             "type='messages' absent (correct for Gradio 6.x)"),
            ("bubble_full_width" not in src,
             "bubble_full_width removed"),
            ('"role": "user"' in src,
             "role:user dict present"),
            ('"role": "assistant"' in src,
             "role:assistant dict present"),
            ("[(display_q, response)]" not in src,
             "old tuple format gone"),
            ("gr.Chatbot(" in src,
             "gr.Chatbot present"),
            ("demo.launch()" in src,
             "demo.launch() present"),
        ]

        all_ok = True
        for ok, label in checks:
            status = "OK  " if ok else "FAIL"
            print(f"  [{status}] {label}")
            if not ok:
                all_ok = False

        print()
        print("RESULT:", "ALL OK - ready to run in Jupyter!" if all_ok else "ISSUES REMAIN")
        break
