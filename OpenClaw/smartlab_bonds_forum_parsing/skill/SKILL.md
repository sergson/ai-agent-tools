---
name: smartlab-bonds-forum-parsing
description: Monitors the smart-lab.ru bonds forum for new messages in the last 2 hours (Moscow time), filters duplicates by comment ID, and outputs time, issuer, and text snippet. Use when you need to track recent forum activity for specific issuers or general sentiment. Provides both manual and scheduled (cron) execution.
---

# Smart-Lab Bonds Forum Parsing

## Overview

This skill provides a Python script that scrapes the smart-lab.ru bonds forum page, extracts recent messages (last 2 hours by Moscow time), and outputs them in a concise format. It remembers already shown messages to avoid duplicates. Suitable for tracking new discussions about bond issuers.

## Quick Start

1. Place the script in OpenClaw workspace:
   ```bash
   cp scripts/smartlab_monitor.py ~/.openclaw/workspace/
   ```

2. Ensure dependencies: `python3`, `curl`, internet access.

3. Run manually:
   ```bash
   python3 ~/.openclaw/workspace/smartlab_monitor.py
   ```

4. To enable periodic updates, create a cron job in OpenClaw that executes the script and returns its stdout.

## Configuration

- **State file**: `~/.openclaw/workspace/smartlab_state.json` (auto-created). Stores IDs of shown comments to prevent duplicates.
- **User-Agent**: Script uses Chrome UA to fetch full HTML (some sites serve different content to bots).
- **Time window**: Last 2 hours relative to current Moscow time (UTC+3), with day-rollover handling.

## How It Works

1. Downloads `https://smart-lab.ru/bonds` with curl.
2. Parses HTML blocks matching pattern:
   `<li class="bluid_...">HH:MM<i><a href="/bonds/...">Issuer</a></i><a href="...#commentID">Text</a></li>`
3. Extracts: time, issuer, comment ID, message text.
4. Filters posts within 2-hour window (Moscow time).
5. Compares comment IDs against `smartlab_state.json`.
6. Prints new messages: `[HH:MM] Issuer: Text` (truncated to 100 chars).
7. Updates state with new IDs.

## Handling Site Changes

If smart-lab.ru changes its HTML structure, the parser may fail. In that case, the script will output "Новых сообщений за последние 2 часа нет." or an error. Update the regular expression in `parse_posts()` accordingly.

## Resources

### scripts/
- `smartlab_monitor.py` — main monitoring script

