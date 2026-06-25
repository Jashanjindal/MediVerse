import json
import os

NOTEBOOK_PATH = r"c:\Users\alpha\OneDrive\Desktop\mediverse\hub\launch.ipynb"

def patch():
    if not os.path.exists(NOTEBOOK_PATH):
        print(f"Error: Notebook not found at {NOTEBOOK_PATH}")
        return

    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Locate the cell with cell_type == "code" and containing "uvicorn.run" or is the last cell
    cell_idx = None
    for idx, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") == "code":
            source_text = "".join(cell.get("source", []))
            if "uvicorn.run" in source_text:
                cell_idx = idx
                break

    if cell_idx is None:
        print("Could not find the launch cell. Defaulting to last cell.")
        cell_idx = len(nb["cells"]) - 1

    print(f"Patching cell index {cell_idx}...")

    new_source = [
        "import asyncio\n",
        "import uvicorn\n",
        "\n",
        "# Store server instances globally so they can be stopped/restarted\n",
        "_server_task = None\n",
        "_server_instance = None\n",
        "\n",
        "async def stop_server():\n",
        "    global _server_task, _server_instance\n",
        "    if _server_instance:\n",
        "        print(\"Stopping uvicorn server...\")\n",
        "        _server_instance.should_exit = True\n",
        "        await _server_instance.shutdown()\n",
        "        _server_instance = None\n",
        "    if _server_task:\n",
        "        _server_task.cancel()\n",
        "        try:\n",
        "            await _server_task\n",
        "        except asyncio.CancelledError:\n",
        "            pass\n",
        "        _server_task = None\n",
        "    print(\"Server stopped. You can safely run the launch cell again.\")\n",
        "\n",
        "def run_server():\n",
        "    global _server_task, _server_instance\n",
        "    \n",
        "    # Configure uvicorn\n",
        "    config = uvicorn.Config(app, host=\"127.0.0.1\", port=8000, log_level=\"info\")\n",
        "    _server_instance = uvicorn.Server(config)\n",
        "    \n",
        "    try:\n",
        "        loop = asyncio.get_running_loop()\n",
        "    except RuntimeError:\n",
        "        loop = None\n",
        "        \n",
        "    if loop and loop.is_running():\n",
        "        print(\"🚀 Launching uvicorn server on http://127.0.0.1:8000 inside Jupyter event loop...\")\n",
        "        print(\"👉 You can browse the unified dashboard portal at http://127.0.0.1:8000\")\n",
        "        print(\"⚠️ To STOP the server, run: await stop_server() in a new cell.\")\n",
        "        # Schedule the task on the existing running loop\n",
        "        _server_task = loop.create_task(_server_instance.serve())\n",
        "    else:\n",
        "        print(\"🚀 Launching uvicorn server synchronously on http://127.0.0.1:8000...\")\n",
        "        print(\"👉 You can browse the unified dashboard portal at http://127.0.0.1:8000\")\n",
        "        uvicorn.run(app, host=\"127.0.0.1\", port=8000, log_level=\"info\")\n",
        "\n",
        "if __name__ == \"__main__\":\n",
        "    # Ensure any previous instance is stopped first\n",
        "    try:\n",
        "        if _server_task or _server_instance:\n",
        "            print(\"Previous server instance detected. Stopping it first...\")\n",
        "            loop = asyncio.get_event_loop()\n",
        "            if loop.is_running():\n",
        "                loop.create_task(stop_server())\n",
        "            else:\n",
        "                asyncio.run(stop_server())\n",
        "    except Exception:\n",
        "        pass\n",
        "        \n",
        "    run_server()\n"
    ]

    nb["cells"][cell_idx]["source"] = new_source
    nb["cells"][cell_idx]["outputs"] = []
    nb["cells"][cell_idx]["execution_count"] = None

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)

    print("Success: Notebook patched successfully!")

if __name__ == "__main__":
    patch()
