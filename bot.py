import os
import random
import threading
from bs4 import BeautifulSoup
import discord
from discord.ext import commands, tasks
import feedparser
from flask import Flask

# Dummy web server to satisfy Render's port check
app = Flask("")


@app.route("/")
def home():
    return "Otterbot is alive!"


def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# Discord Client Configuration
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- CONFIGURATION ---
CHANNEL_ID = 1549997290025132053
TOKEN = os.getenv("BOT_TOKEN")
DAILY_OTTER_RSS = "https://dailyotter.org/posts?format=rss"


def get_latest_otter():
    """Fetches the RSS feed from Daily Otter and extracts an image URL."""
    try:
        feed = feedparser.parse(DAILY_OTTER_RSS)
        if feed.entries:
            post = random.choice(feed.entries[:10])
            soup = BeautifulSoup(
                post.summary if "summary" in post else "", "html.parser"
            )
            img_tag = soup.find("img")
            image_url = img_tag["src"] if img_tag else None
            return post.title, post.link, image_url
    except Exception as e:
        print(f"Error fetching from Daily Otter: {e}")
    return None, None, None


@tasks.loop(hours=24)
async def send_daily_otter():
    """Loops every 24 hours to post an otter meme."""
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        title, link, img_url = get_latest_otter()
        if link:
            embed = discord.Embed(
                title=f"🦦 {title}", url=link, color=discord.Color.dark_teal()
            )
            embed.set_footer(text="Source: dailyotter.org")
            if img_url:
                embed.set_image(url=img_url)
            await channel.send(embed=embed)


@bot.event
async def on_ready():
    print(f"Otterbot is live! Logged in as: {bot.user}")
    send_daily_otter.start()


# Start web server in background thread, then start bot
threading.Thread(target=run_web_server, daemon=True).start()
bot.run(TOKEN)