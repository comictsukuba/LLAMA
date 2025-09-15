import discord
from discord.ext import commands
from discord import app_commands 
import os
from dotenv import load_dotenv
import pyotp
import datetime

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm LLAMA. Feed me!"

def run_web_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

GUILD_ID = int(os.getenv('GUILD_ID'))

SECRET_KEY = os.getenv('SECRET_KEY')

bot = commands.Bot(command_prefix="!", intents=intents) 

totp_google = pyotp.TOTP(SECRET_KEY)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print("ログインしました。")
    await bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name='エサをよこせ！！'))


@bot.tree.command(name='authenticate', description='Google アカウント認証コードを吐きます', guild=discord.Object(id=GUILD_ID))
async def authenticate_google(ctx: discord.Interaction):
    
    time_remaining = totp_google.interval - datetime.datetime.now().timestamp() % totp_google.interval
    
    embed = discord.Embed(title="認証コードが発行されました", color=discord.Color.green())
    embed.add_field(name="認証コード", value=totp_google.now(), inline=False)
    embed.add_field(name="残り有効時間", value=f"{int(time_remaining)}秒", inline=False)
    
    await ctx.response.send_message(embed=embed)

bot_token = os.getenv('DISCORD_BOT_TOKEN')
if bot_token is None:
    print("エラー: Botのトークンが設定されていません。")
else:
    # Webサーバーを別スレッドで起動
    web_thread = Thread(target=run_web_server)
    web_thread.start()
    # Discord Botを起動
    bot.run(bot_token)