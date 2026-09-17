import os
import random
from bs4 import BeautifulSoup
import discord
from discord.ext import commands, tasks
import feedparser

# Discord Client Configuration
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


CHANNEL_ID = 1549997290025132053  # Replace with your Discord Channel ID (numbers, no quotes)
TOKEN = os.getenv("BOT_TOKEN")
DAILY_OTTER_RSS = "https://dailyotter.org/posts?format=rss"


def get_latest_otter():
    """Fetches the RSS feed from Daily Otter and extracts an image URL."""
    try:
        feed = feedparser.parse(DAILY_OTTER_RSS)
        if feed.entries:
            # Pick a random entry from the 10 most recent posts
            post = random.choice(feed.entries[:10])

            # Parse HTML content inside post to pull out the image tag
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
    channel = bot.get_channel(1549997290025132053)
    if channel:
        title, link, img_url = get_latest_otter()

        if link:
            # Format the output into a clean Discord Embed
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


# Start the bot
bot.run(TOKEN)