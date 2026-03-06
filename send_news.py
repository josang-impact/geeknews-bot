import feedparser
import requests
import os
import re
from html import unescape

RSS_URL = "https://news.hada.io/rss/news"
WEBHOOK = os.environ["KAKAOWORK_WEBHOOK"]

feed = feedparser.parse(RSS_URL)

if len(feed.entries) == 0:
    print("RSS empty")
    exit()

# 마지막 뉴스 읽기
try:
    with open("last_id.txt") as f:
        last_id = f.read().strip()
except:
    last_id = ""

new_last_id = feed.entries[0].id

messages = []

def clean_html(text):
    text = re.sub('<[^<]+?>', '', text)  # HTML 태그 제거
    text = unescape(text)                # &amp; 같은 것 변환
    return text.strip()

for entry in feed.entries:
    if entry.id == last_id:
        break

    title = clean_html(entry.title)
    link = entry.link

    summary = clean_html(entry.summary)
    summary_lines = summary.split("\n")[:3]
    summary_text = "\n".join(summary_lines)

    text = f"""{title}

{summary_text}

{link}
"""

    messages.append(text)

for msg in reversed(messages):
    requests.post(
        WEBHOOK,
        json={"text": msg}
    )

with open("last_id.txt", "w") as f:
    f.write(new_last_id)
