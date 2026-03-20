import os
import time
import logging
import requests
from datetime import datetime
from typing import List, Dict

# ============================================================================
# Configuration
# ============================================================================

TELEGRAM_BOT_TOKEN = "7761602407:AAE_W_1tZAZPtbha5demGir5hbvOgXdZKs4"
TELEGRAM_CHAT_ID = "-1003750689711"
NEWSDATA_API_KEY = "pub_0ea6f4347a8b4aa0b3f20247240ca7eb"
NEWSDATA_BASE_URL = "https://newsdata.io/api/1/news"

logging.basicConfig(level=logging.INFO, format='%(asctime )s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

NEWS_CATEGORIES = {
    "politics_economy": {"emoji": "🔥", "title": "Top Stories", "keywords": ["election", "Fed", "inflation", "US economy"]},
    "market_dynamics": {"emoji": "📈", "title": "Market Watch", "keywords": ["Wall Street", "S&P 500", "Nasdaq", "trading"]},
    "sports_esports": {"emoji": "🏆", "title": "Sports & Esports", "keywords": ["NBA", "NFL", "MLB", "Esports"]},
    "tech_ai": {"emoji": "💡", "title": "Tech & AI", "keywords": ["OpenAI", "Nvidia", "AI", "startup"]}
}

class FortuneNewsBot:
    def __init__(self, bot_token: str, chat_id: str, api_key: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_key = api_key

    def escape_markdown(self, text: str) -> str:
        if not text: return ""
        return text.replace("_", "\\_").replace("*", "").replace("[", "\\[").replace("]", "\\]")

    def fetch_news(self, category: str, limit: int = 2) -> List[Dict]:
        keywords = " OR ".join(NEWS_CATEGORIES[category]["keywords"])
        params = {"apikey": self.api_key, "q": keywords, "language": "en", "country": "us,ca"}
        try:
            response = requests.get(NEWSDATA_BASE_URL, params=params, timeout=20)
            if response.status_code == 200:
                return response.json().get("results", [])[:limit]
            return []
        except Exception as e:
            logger.error(f"Fetch Error ({category}): {e}")
            return []

    def build_report(self) -> str:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        report = f"🍪 *Fortune Protocol Daily Market Report*\n\n📅 **{current_time} (UTC)**\n\n---\n"
        has_content = False
        for category, config in NEWS_CATEGORIES.items():
            articles = self.fetch_news(category)
            if articles:
                report += f"\n{config['emoji']} **{config['title']}**\n"
                for art in articles:
                    title = self.escape_markdown(art.get("title", "No Title"))
                    link = art.get("link", "#")
                    report += f"\n• *{title}*\n  [Read More]({link})\n"
                    has_content = True
                report += "\n---\n"
        if not has_content: report += "\nNo new updates.\n"
        report += "\n✨ *Follow Fortune Protocol for more insights!*\n🐦 [Twitter](https://x.com/io_fortune )"
        return report

    def send_report(self, report: str) -> bool:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": report, "parse_mode": "Markdown", "disable_web_page_preview": True}
        try:
            response = requests.post(url, json=payload, timeout=20 )
            if response.status_code == 200:
                logger.info("✅ Report sent successfully!")
                return True
            else:
                logger.error(f"❌ Telegram API Error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to send report: {e}")
            return False

def main():
    logger.info("🚀 Bot starting in Docker Mode...")
    bot = FortuneNewsBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, NEWSDATA_API_KEY)
    while True:
        try:
            report = bot.build_report()
            bot.send_report(report)
            logger.info("⏳ Waiting 2 hours for next update...")
            time.sleep(7200)
        except Exception as e:
            logger.error(f"Main Loop Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
