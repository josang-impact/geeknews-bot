import feedparser
import requests
import os

RSS_URL = "https://news.hada.io/rss/news"
WEBHOOK = os.environ["KAKAOWORK_WEBHOOK"]

feed = feedparser.parse(RSS_URL)

if len(feed.entries) == 0:
    print("RSS empty")
    exit()

try:
    with open("last_id.txt") as f:
        last_id = f.read().strip()
except:
    last_id = ""

new_last_id = feed.entries[0].id

messages = []

for entry in feed.entries:
    if entry.id == last_id:
        break

    title = entry.title
    link = entry.link
    summary = entry.summary.split("\n")[:3]

    text = f"""
📢 GeekNews 업데이트

*{title}*

{''.join(summary)}

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
