# Smart-Lab Bonds Forum Parsing

**Description:**  
Monitors the latest messages on the smart-lab.ru bonds forum. Collects messages posted in the last 2 hours (Moscow time), filters out already shown ones, and outputs time, issuer, and a short text snippet.

**Capabilities:**
- Periodic execution via cron (scheduled)
- Manual run (command)
- State persistence (IDs of shown messages)

**Usage:**
1. Ensure `python3` and `curl` are available in the system.
2. Copy `smartlab_monitor.py` to the OpenClaw working directory (e.g., `/home/serg/.openclaw/workspace/`).
3. Configure a cron job in OpenClaw that runs the script and sends its output to the chat:
   ```json
   {
     "name": "Smart-Lab Bonds Monitor",
     "schedule": { "kind": "cron", "expr": "0 7-21 * * *", "tz": "UTC" },
     "payload": {
       "kind": "agentTurn",
       "message": "Execute command: `python3 /home/serg/.openclaw/workspace/smartlab_monitor.py` and return its stdout as your response. Do not add any extra text."
     },
     "sessionTarget": "isolated",
     "delivery": { "mode": "announce", "channel": "telegram", "to": "770932371" }
   }
   ```
4. On first run, all messages from the last 2 hours will be shown; subsequent runs show only new ones.

**Configuration:**
- State file: `smartlab_state.json` (stored in the working directory). Format: `{"shown_messages": ["<comment_id>", ...]}`.
- User-Agent: Chrome is used to ensure the site returns the full HTML page.

**Notes:**
- The structure of smart-lab.ru/bonds may change. If it does, the parser will need updating.
- The current parser looks for blocks: `<li class="bluid_...">HH:MM<i><a href="/bonds/...">Issuer</a></i><a href="...#commentID">Text</a></li>`
- If the page changes, the script will return "Новых сообщений за последние 2 часа нет." or an error.

**Files:**
- `smartlab_monitor.py` — main Python script.