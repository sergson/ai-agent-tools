# Smart-Lab Bonds Forum Parsing Skill

This skill provides monitoring of the latest messages on the smart-lab.ru bonds forum.

## Quick Start

1. **Place the script**  
   The `smartlab_monitor.py` script must be available at the path you specify in the cron job. It is recommended to place it in the OpenClaw working directory:
   ```bash
   cp smartlab_monitor.py /home/serg/.openclaw/workspace/
   ```

2. **Configure a cron job in OpenClaw**  
   Add a job via `openclaw cron add` or in the config. Example payload:
   ```json
   {
     "kind": "agentTurn",
     "message": "Execute command: `python3 /home/serg/.openclaw/workspace/smartlab_monitor.py` and return its stdout as your response."
   }
   ```
   Schedule: every hour from 07:00 to 21:00 UTC.

3. **First run**  
   On first run, the state file `smartlab_state.json` will be created automatically. All messages from the last 2 hours will be shown as new.

## How it works

- The script downloads the page `https://smart-lab.ru/bonds` with a browser User-Agent.
- It parses the blocks of recent forum messages matching the `bluid_...` pattern.
- Filters posts published in the last 2 hours (Moscow time, UTC+3), correctly handling day rollover.
- Compares comment IDs with already shown ones (stored in `smartlab_state.json`).
- Formats output: `[HH:MM] Issuer: Text` (text truncated to 100 characters).

## State format

File `smartlab_state.json`:
```json
{
  "shown_messages": ["19176891", "19176879", ...]
}
```
Message IDs are the numbers after `#comment` in the link.

## Requirements

- Python 3.x
- curl
- Internet access

## Handling site changes

If the structure of smart-lab.ru/bonds changes, the parser may stop working. In that case, the script will return "Новых сообщений за последние 2 часа нет." or an error. You will need to update the regular expression in the `parse_posts` function.

## License

As part of OpenClaw.
