#!/usr/bin/env python3
import os
import re
import sys

# Add the project's root to the Python path so it can find skills/what-watch-bot/src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'skills', 'what-watch-bot')))

from src.utils.platforms import SUPPORTED_PLATFORMS

SKILL_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'skills', 'what-watch-bot', 'SKILL.md')

def generate_ui_markdown(platforms):
    subs = [p for p in platforms if p['tier'] == 'SUBSCRIPTION']
    free = [p for p in platforms if p['tier'] == 'FREE']

    lines = ["💳 SUBSCRIPTION:"]
    for p in subs:
        checkbox = "✅" if p['name'] == 'Netflix' else "◻️"
        lines.append(f"{checkbox} {p['name']}")
    
    lines.append("")
    lines.append("🆓 FREE (ad-supported or free):")
    for p in free:
        lines.append(f"◻️ {p['name']}")
    
    return "\n".join(lines)

def generate_lookup_markdown(platforms):
    subs = [p for p in platforms if p['tier'] == 'SUBSCRIPTION']
    free = [p for p in platforms if p['tier'] == 'FREE']

    lines = ["💳 SUBSCRIPTION:"]
    lines.append("| Platform | ID |")
    lines.append("| --- | --- |")
    for p in subs:
        lines.append(f"| {p['name']} | {p['id']} |")
    
    lines.append("")
    lines.append("🆓 FREE (tier `free` or `ads` on TMDB):")
    lines.append("| Platform | ID |")
    lines.append("| --- | --- |")
    for p in free:
        lines.append(f"| {p['name']} | {p['id']} |")
    
    return "\n".join(lines)

def sync_platforms():
    try:
        with open(SKILL_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {SKILL_FILE_PATH} not found.")
        return

    ui_markdown = generate_ui_markdown(SUPPORTED_PLATFORMS)
    lookup_markdown = generate_lookup_markdown(SUPPORTED_PLATFORMS)

    # Use re.DOTALL to match across newlines
    ui_pattern = re.compile(r'(<!-- PLATFORMS_UI_START -->\n).*?(\n<!-- PLATFORMS_UI_END -->)', re.DOTALL)
    if not ui_pattern.search(content):
        print("Error: <!-- PLATFORMS_UI_START --> / END markers not found in SKILL.md")
        return
    content = ui_pattern.sub(lambda m: f"{m.group(1)}{ui_markdown}{m.group(2)}", content)

    lookup_pattern = re.compile(r'(<!-- PLATFORMS_LOOKUP_START -->\n).*?(\n<!-- PLATFORMS_LOOKUP_END -->)', re.DOTALL)
    if not lookup_pattern.search(content):
        print("Error: <!-- PLATFORMS_LOOKUP_START --> / END markers not found in SKILL.md")
        return
    content = lookup_pattern.sub(lambda m: f"{m.group(1)}{lookup_markdown}{m.group(2)}", content)

    with open(SKILL_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SKILL.md successfully synchronized with src/utils/platforms.py!")

if __name__ == '__main__':
    sync_platforms()
