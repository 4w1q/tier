# bot.py
import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Flask için gerekli importlar
from flask import Flask, render_template, jsonify, request
from threading import Thread

# Bot için intents ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Bot ve prefixini oluşturma - PREFIX ! OLARAK AYARLANDI
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

# Bot hazır olduğunda
@bot.event
async def on_ready():
    print(f'{bot.user.name} olarak giriş yapıldı!')
    print('------')

# !siteye-ekle komutu
@bot.command(name='siteye-ekle')
async def siteye_ekle(ctx):
    # Kullanıcı ile iletişim için mesaj gönder
    embed = discord.Embed(
        title="Kit Seçimi",
        description="Lütfen eklemek istediğiniz kit türünü seçin:",
        color=discord.Color.blue()
    )
    
    # Kit seçim menüsü
    kit_select = discord.ui.Select(
        placeholder="Kit seçin",
        options=[discord.SelectOption(label=kit, value=kit) for kit in KIT_OPTIONS]
    )
    
    # Seçim view'ı
    view = discord.ui.View()
    view.add_item(kit_select)
    
    # Kullanıcının seçimlerini saklamak için değişkenler
    user_choices = {"kit": None, "tier": None, "name": None}
    
    # Kit seçim callback fonksiyonu
    async def kit_callback(interaction):
        if interaction.user.id != ctx.author.id:
            return await interaction.response.send_message("Bu menüyü sadece komutu kullanan kişi kullanabilir!", ephemeral=True)
        
        user_choices["kit"] = kit_select.values[0]
        
        # Tier seçim menüsü
        tier_embed = discord.Embed(
            title="Tier Seçimi",
            description=f"Seçilen Kit: {user_choices['kit']}\nŞimdi lütfen Tier seviyesini seçin:",
            color=discord.Color.blue()
        )
        
        tier_select = discord.ui.Select(
            placeholder="Tier seçin",
            options=[discord.SelectOption(label=tier, value=tier) for tier in TIER_OPTIONS]
        )
        
        tier_view = discord.ui.View()
        tier_view.add_item(tier_select)
        
        # Tier seçim callback fonksiyonu
        async def tier_callback(tier_interaction):
            if tier_interaction.user.id != ctx.author.id:
                return await tier_interaction.response.send_message("Bu menüyü sadece komutu kullanan kişi kullanabilir!", ephemeral=True)
            
            user_choices["tier"] = tier_select.values[0]
            
            # İsim girişi için mesaj
            name_embed = discord.Embed(
                title="İsim Girişi",
                description=f"Seçilen Kit: {user_choices['kit']}, Tier: {user_choices['tier']}\nLütfen bir isim yazın:",
                color=discord.Color.blue()
            )
            await tier_interaction.response.edit_message(embed=name_embed, view=None)
            
            # İsim bekleme
            try:
                name_msg = await bot.wait_for(
                    "message",
                    check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id,
                    timeout=60.0
                )
                
                user_choices["name"] = name_msg.content.strip()
                
                # Veriyi kaydet
                user_data = {
                    "userId": str(ctx.author.id),
                    "username": ctx.author.name,
                    "kit": user_choices["kit"],
                    "tier": user_choices["tier"],
                    "name": user_choices["name"],
                    "date": datetime.now().isoformat()
                }
                
                # Kullanıcı bu kiti daha önce eklediyse güncelle, yoksa yeni ekle
                existing_user_index = None
                for i, user in enumerate(kit_data["users"]):
                    if user["userId"] == str(ctx.author.id) and user["kit"] == user_choices["kit"]:
                        existing_user_index = i
                        break
                
                if existing_user_index is not None:
                    kit_data["users"][existing_user_index] = user_data
                else:
                    kit_data["users"].append(user_data)
                
                save_data()
                
                # Başarılı mesajı
                success_embed = discord.Embed(
                    title="Başarıyla Eklendi!",
                    description=f"Kit: {user_choices['kit']}\nTier: {user_choices['tier']}\nİsim: {user_choices['name']}",
                    color=discord.Color.green()
                )
                success_embed.set_footer(text="Siteye başarıyla eklendi!")
                await ctx.send(embed=success_embed)
                
                # İsim mesajını silmeye çalış
                try:
                    await name_msg.delete()
                except:
                    pass
                    
            except asyncio.TimeoutError:
                await ctx.send("Zaman aşımı! İşlem iptal edildi.")
                
        tier_select.callback = tier_callback
        await interaction.response.edit_message(embed=tier_embed, view=tier_view)
    
    kit_select.callback = kit_callback
    sent_message = await ctx.send(embed=embed, view=view)

# Basit test komutu
@bot.command(name='test')
async def test(ctx):
    await ctx.send("Bot çalışıyor! Prefix: !")

# Flask web uygulaması
app = Flask(__name__, template_folder='templates', static_folder='static')

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

# Web server'ı ayrı bir thread'de başlatma
def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# Ana fonksiyon
def main():
    # Web server'ı başlat
    server_thread = Thread(target=run_web_server)
    server_thread.start()
    
    # Discord botunu başlat - TOKEN .env dosyasından okunuyor
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()
