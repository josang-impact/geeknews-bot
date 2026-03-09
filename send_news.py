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


def get_meta(url):
    """
    GeekNews 페이지에서 추천수(points)와 댓글수 추출
    """
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        points = 0
        comments = 0

        p = re.search(r'(\d+)\s+points', text)
        c = re.search(r'댓글\s*(\d+)', text)

        if p:
            points = int(p.group(1))

        if c:
            comments = int(c.group(1))

        return points, comments

    except:
        return 0, 0


# RSS 읽기
feed = feedparser.parse(RSS_URL)

if len(feed.entries) == 0:
    print("RSS empty")
    exit()

# 이전 마지막 뉴스
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

    title = clean_html(entry.title)
    link = entry.link

    summary = clean_html(entry.summary)
    summary_lines = summary.split("\n")[:3]
    summary_text = "\n".join(summary_lines)

    points, comments = get_meta(link)

    text = f"""📰 {title} (👍 {points} | 💬 {comments})

{summary_text}

{link}

──────────
"""

    messages.append(text)

# 오래된 뉴스부터 전송
for msg in reversed(messages):
    try:
        requests.post(
            WEBHOOK,
            json={"text": msg},
            timeout=10
        )
        print("sent")
    except:
        print("send failed")

# 마지막 뉴스 저장
with open("last_id.txt", "w") as f:
    f.write(new_last_id)
