# app.py

import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
import threading

# .env dosyasını yükle
load_dotenv()

# Flask uygulaması
app = Flask(__name__)

# Bot için intents ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Bot ve prefixini oluşturma
bot = commands.Bot(command_prefix='!', intents=intents)

# Veri dosyası yolu
DATA_FILE = 'kit_data.json'

# Veri yapısını oluştur veya yükle
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        kit_data = json.load(f)
else:
    kit_data = {"users": []}

# Veriyi kaydetme fonksiyonu
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(kit_data, f, indent=2)

# Kit ve Tier seçenekleri
KIT_OPTIONS = ["Nethpot", "Beast", "Diapot", "Smp", "Axe", "Gapple", "Elytra", "Crystal"]
TIER_OPTIONS = ["Tier1", "Tier2", "Tier3", "Tier4", "Tier5"]

# Flask rotaları
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/kits')
def get_kits():
    return jsonify(kit_data)

@app.route('/api/kits/<kit_type>')
def get_kit_rankings(kit_type):
    if kit_type not in KIT_OPTIONS:
        return jsonify({"error": "Geçersiz kit türü"}), 400
    
    # Belirli bir kit türüne göre kullanıcıları filtrele
    filtered_users = [user for user in kit_data["users"] if user["kit"] == kit_type]
    
    # Tier seviyesine göre sırala (Tier5 en üstte)
    sorted_users = sorted(filtered_users, key=lambda x: TIER_OPTIONS.index(x["tier"]), reverse=True)
    
    return jsonify({"users": sorted_users})

# Bot komutları - bunlar eski bot.py'den alınmıştır
@bot.event
async def on_ready():
    print(f'{bot.user.name} olarak giriş yapıldı!')
    print('------')

@bot.command(name='siteye-ekle')
async def siteye_ekle(ctx):
    # Bot komut kodları (mevcut bot.py'den kopyala)
    # ... (tüm siteye_ekle fonksiyonu)
    pass

@bot.command(name='test')
async def test(ctx):
    await ctx.send("Bot çalışıyor! Prefix: !")

# Botu ayrı bir thread'de çalıştır
def run_bot():
    bot.run(os.getenv('DISCORD_TOKEN'))

# Ana fonksiyon
if __name__ == '__main__':
    # Botu ayrı bir thread'de başlat
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Web uygulamasını çalıştır
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
