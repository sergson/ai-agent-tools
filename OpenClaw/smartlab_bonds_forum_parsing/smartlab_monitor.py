#!/usr/bin/env python3
import sys, json, re, subprocess, os
from datetime import datetime, timedelta

def get_html():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    url = 'https://smart-lab.ru/bonds'
    res = subprocess.run(['curl', '-s', '-A', user_agent, url], capture_output=True, text=True)
    return res.stdout

def parse_posts(html):
    pattern = r'<li class="bluid_[0-9]*">([0-9]{2}:[0-9]{2})<i><a href="/bonds/[^"]*">([^<]*)</a></i><a href="[^"]*#comment([0-9]+)"[^>]*>([^<]*)</a></li>'
    posts = []
    for m in re.finditer(pattern, html):
        time_str = m.group(1)
        issuer = m.group(2)
        comment_id = m.group(3)
        text = m.group(4)
        posts.append({'time': time_str, 'issuer': issuer, 'id': comment_id, 'text': text})
    return posts

def time_to_minutes(t):
    h, m = map(int, t.split(':'))
    return h*60 + m

def within_last_2_hours(post_time, cur_time):
    cur_min = time_to_minutes(cur_time)
    post_min = time_to_minutes(post_time)
    if cur_min < post_min:
        cur_min += 1440
    return (cur_min - post_min) <= 120

def load_state(path):
    if not os.path.exists(path):
        return set()
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return set(data.get('shown_messages', []))
    except:
        return set()

def save_state(path, shown):
    with open(path, 'w') as f:
        json.dump({'shown_messages': list(shown)}, f, ensure_ascii=False, indent=2)

def main():
    state_file = os.path.expanduser('~/.openclaw/workspace/smartlab_state.json')
    html = get_html()
    posts = parse_posts(html)
    # Получаем текущее время в MSK
    cur_time = subprocess.run(['bash', '-c', "TZ=Europe/Moscow date +%H:%M"], capture_output=True, text=True).stdout.strip()
    recent_posts = [p for p in posts if within_last_2_hours(p['time'], cur_time)]
    shown = load_state(state_file)
    new_posts = [p for p in recent_posts if p['id'] not in shown]
    if not new_posts:
        print("Новых сообщений за последние 2 часа нет.")
    else:
        for p in new_posts:
            txt = p['text']
            if len(txt) > 100:
                txt = txt[:100] + '...'
            print(f"[{p['time']}] {p['issuer']}: {txt}")
    shown.update(p['id'] for p in new_posts)
    save_state(state_file, shown)

if __name__ == '__main__':
    main()
