from flask import Flask, render_template, jsonify
import json
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Flask uygulaması
app = Flask(__name__)

# Veri dosyası yolu
DATA_FILE = 'kit_data.json'

# Kit ve Tier seçenekleri
KIT_OPTIONS = ["Nethpot", "Beast", "Diapot", "Smp", "Axe", "Gapple", "Elytra", "Crystal"]
TIER_OPTIONS = ["Tier1", "Tier2", "Tier3", "Tier4", "Tier5"]

# Veri yapısını oluştur veya yükle
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"users": []}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/kits')
def get_kits():
    return jsonify(load_data())

@app.route('/api/kits/<kit_type>')
def get_kit_rankings(kit_type):
    if kit_type not in KIT_OPTIONS:
        return jsonify({"error": "Geçersiz kit türü"}), 400
    
    kit_data = load_data()
    # Belirli bir kit türüne göre kullanıcıları filtrele
    filtered_users = [user for user in kit_data["users"] if user["kit"] == kit_type]
    
    # Tier seviyesine göre sırala (Tier5 en üstte)
    sorted_users = sorted(filtered_users, key=lambda x: TIER_OPTIONS.index(x["tier"]), reverse=True)
    
    return jsonify({"users": sorted_users})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
