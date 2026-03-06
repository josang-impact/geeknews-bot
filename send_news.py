import feedparser
import requests
import os
import re
from html import unescape
from bs4 import BeautifulSoup

RSS_URL = "https://news.hada.io/rss/news"
WEBHOOK = os.environ["KAKAOWORK_WEBHOOK"]


def clean_html(text):
    text = re.sub('<[^<]+?>', '', text)
    text = unescape(text)
    return text.strip()


def get_comments(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        match = re.search(r'댓글\s*(\d+)', text)
        if match:
            return int(match.group(1))
    except:
        pass

    return 0


feed = feedparser.parse(RSS_URL)

if len(feed.entries) == 0:
    print("RSS empty")
    exit()

# 이전 마지막 뉴스 읽기
try:
    with open("last_id.txt") as f:
        last_id = f.read().strip()
except:
    last_id = ""

new_last_id = feed.entries[0].id

# 첫 실행 시 기준만 저장
if last_id == "":
    with open("last_id.txt", "w") as f:
        f.write(new_last_id)
    print("First run - skip sending")
    exit()

messages = []

for entry in feed.entries:
    if entry.id == last_id:
        break

    title = clean_html(entry.title)
    link = entry.link

    summary = clean_html(entry.summary)
    summary_lines = summary.split("\n")[:3]
    summary_text = "\n".join(summary_lines)

    comments = get_comments(link)

    text = f"""📰 {title} (💬 {comments})

{summary_text}

{link}

──────────
"""

    messages.append(text)

# 오래된 것부터 전송
for msg in reversed(messages):
    try:
        requests.post(
            WEBHOOK,
            json={"text": msg},
            timeout=10
        )
    except:
        print("Webhook send failed")

# 마지막 뉴스 저장
with open("last_id.txt", "w") as f:
    f.write(new_last_id)
