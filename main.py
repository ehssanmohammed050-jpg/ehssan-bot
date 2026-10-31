import os, sqlite3, threading, time, random
from datetime import datetime
import pytz, requests
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DB_PATH = "users.db"
KHARTOUM_TZ = pytz.timezone("Africa/Khartoum")

MESSAGES = [
"صباح الخير يا إحسان! 🌸 يوم جديد وفرصة جديدة 💪",
"انتي أقوى من أي تحدي يا بطلة ❤️",
"كل خطوة صغيرة بتقربك لهدفك ✨",
"استراحة؟ قومي اتمشي وارجعي بطاقة جديدة 🔋",
"انتي مميزة وشغلك حلو شديد 👏"
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def save_user(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT chat_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except:
        pass

def bot_loop():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?timeout=30&offset={offset}"
            resp = requests.get(url, timeout=35).json()
            if "result" in resp:
                for upd in resp["result"]:
                    offset = upd["update_id"] + 1
                    if "message" in upd:
                        chat_id = upd["message"]["chat"]["id"]
                        save_user(chat_id)
                        send_message(chat_id, "أهلا يا إحسان! 🌸 البوت اشتغل في Render 💪")
        except:
            time.sleep(5)

def scheduler_loop():
    while True:
        try:
            now = datetime.now(KHARTOUM_TZ)
            if 8 <= now.hour <= 22 and now.hour in [8,11,14,17,20] and now.minute == 0:
                users = get_users()
                msg = random.choice(MESSAGES)
                for uid in users:
                    send_message(uid, msg)
                time.sleep(60)
            time.sleep(30)
        except:
            time.sleep(30)

app = Flask(__name__)
@app.route("/")
def home():
    return "Ehssan Bot Running ✅"

if __name__ == "__main__":
    init_db()
    threading.Thread(target=bot_loop, daemon=True).start()
    threading.Thread(target=scheduler_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
