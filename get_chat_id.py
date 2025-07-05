import time
import requests

TOKEN = "7700899237:AAGHm6tjtU5MbQOlegjj8FeIazkCaU1pP4s"
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

def main():
    print("Botunuza Telegram'dan bir mesaj gönderin (grup veya özel). Chat ID'ler burada listelenecek.")
    while True:
        r = requests.get(url)
        for result in r.json().get("result", []):
            msg = result.get("message", {})
            chat = msg.get("chat", {})
            chat_id = chat.get('id')
            title = chat.get('title') or chat.get('username') or chat.get('first_name') or ''
            print(f"Chat ID: {chat_id}, Title: {title}")
        time.sleep(3)

if __name__ == "__main__":
    main() 