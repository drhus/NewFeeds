import feedparser
import socket

socket.setdefaulttimeout(10)

urls = [
    # Israel batch 1 - israelinfo, hm-news, honestreporting, mivzakim
    ("IsraelInfo News", "https://news.israelinfo.co.il/rss/news.xml"),
    ("IsraelInfo Events", "https://news.israelinfo.co.il/rss/news_events.xml"),
    ("IsraelInfo Law", "https://news.israelinfo.co.il/rss/news_law.xml"),
    ("IsraelInfo Politics", "https://news.israelinfo.co.il/rss/news_politics.xml"),
    ("HM News", "https://hm-news.co.il/feed/"),
    ("HonestReporting", "https://honestreporting.com/feed/"),
    ("Mivzakim Cat1", "https://rss.mivzakim.net/rss/category/1"),
    ("Mivzakim Feed1", "https://rss.mivzakim.net/rss/feed/1"),
    ("Mivzakim 171", "https://rss.mivzakim.net/rss/feed/171"),
    ("Mivzakim 230", "https://rss.mivzakim.net/rss/feed/230"),
    ("Mivzakim 342", "https://rss.mivzakim.net/rss/feed/342"),
    ("Mivzakim 343", "https://rss.mivzakim.net/rss/feed/343"),
    ("Mivzakim 435", "https://rss.mivzakim.net/rss/feed/435"),
    ("Mivzakim 439", "https://rss.mivzakim.net/rss/feed/439"),
    ("Mivzakim 61", "https://rss.mivzakim.net/rss/feed/61"),
    ("Mivzakim 76", "https://rss.mivzakim.net/rss/feed/76"),
    ("Mivzakim 89", "https://rss.mivzakim.net/rss/feed/89"),
    ("Tov News", "https://tovnews.co.il/feed"),
    ("HaAyal", "https://haayal.co.il/xml/rss"),
    ("Maakav", "https://maakav.org.il/feed/"),
    ("Ahlla", "https://ahlla.co.il/feed/"),
    ("Post News IL", "https://postnews.co.il/feed"),
]

for name, url in urls:
    try:
        d = feedparser.parse(url)
        n = len(d.entries)
        print(f"{'OK' if n > 0 else 'EMPTY'}  {name}: {n} entries")
    except Exception as e:
        print(f"FAIL  {name}: {type(e).__name__}: {e}")
