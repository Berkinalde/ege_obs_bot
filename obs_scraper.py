import os
import smtplib
import time
import requests
from email.message import EmailMessage
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from dotenv import load_dotenv
import json
import traceback

# ——— Ortam değişkenlerini yükle ———
load_dotenv()

# ——— Mail gönderme fonksiyonu ———
def send_email(subject: str, body: str, recipient: str):
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASS")
    if not user or not password:
        raise EnvironmentError("GMAIL_USER veya GMAIL_PASS tanımsız.")
    
    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        print(f"📧 E-posta başarıyla gönderildi: {subject}")
        return True
    except Exception as e:
        print(f"❌ E-posta gönderilemedi: {e}")
        print(traceback.format_exc())
        return False

# ——— OBS notlarını çekme ———
def fetch_obs_grades():
    session = requests.Session()
    username = os.getenv("OBS_USERNAME")
    password = os.getenv("OBS_PASSWORD")
    
    if not username or not password:
        raise EnvironmentError("OBS_USERNAME veya OBS_PASSWORD tanımsız.")
    
    # Giriş sayfasını al
    login_url = "https://kimlik.ege.edu.tr/Identity/Account/Login?ReturnUrl=%2F"
    login_page = session.get(login_url)
    login_page.raise_for_status()
    soup = BeautifulSoup(login_page.text, "html.parser")
    
    # Hidden inputları topla
    payload = {
        "Input.Username": username,
        "Input.Password": password,
        "Input.RememberMe": "false"
    }
    for hidden in soup.find_all('input', {'type': 'hidden'}):
        if hidden.get('name'):
            payload[hidden['name']] = hidden.get('value', '')
    
    # Giriş yap
    resp = session.post(login_url, data=payload)
    if resp.url == login_url or "Hatalı" in resp.text:
        raise Exception("OBS giriş başarısız!")
    
    # Notlar sayfasına git
    grades_url = "https://obys4.ege.edu.tr/Ogrenci/Ogr0201/Default.aspx"
    grades_page = session.get(grades_url)
    grades_page.raise_for_status()
    
    # Notları parse et
    grades_soup = BeautifulSoup(grades_page.text, 'html.parser')
    grades = {}
    
    for div in grades_soup.find_all('div', id=lambda x: x and x.startswith('divFinalNot')):
        ders_adi = div.find_previous('td').get_text(strip=True) if div.find_previous('td') else "Bilinmeyen Ders"
        notu = div.get_text(strip=True)
        if notu and notu.strip():  # Boş notları filtrele
            grades[ders_adi] = notu
    
    return grades

# ——— Son durumu saklamak için dosya tabanlı storage ———
def load_last_grades():
    try:
        with open('last_grades.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_last_grades(grades):
    with open('last_grades.json', 'w', encoding='utf-8') as f:
        json.dump(grades, f, ensure_ascii=False, indent=2)

def job_check_and_notify():
    try:
        current = fetch_obs_grades()
        last = load_last_grades()
        
        # Değişiklikleri bul
        diff = {}
        for ders, notu in current.items():
            if ders not in last or last[ders] != notu:
                diff[ders] = notu
        
        if diff:
            # E-posta gönder
            subject = f"📢 OBS Not Güncellemesi - {len(diff)} yeni not"
            body = "Yeni notlar:\n\n"
            for ders, notu in diff.items():
                body += f"📚 {ders}: {notu}\n"
            
            recipient = os.getenv("TO_EMAIL", os.getenv("GMAIL_USER"))
            email_sent = send_email(subject, body, recipient)
            
            # Son durumu kaydet
            save_last_grades(current)
            
            return {
                "status": "success", 
                "message": "Yeni notlar bulundu ve e-posta gönderildi",
                "diff": diff,
                "email_sent": email_sent
            }
        else:
            return {
                "status": "success", 
                "message": "Değişiklik yok",
                "diff": {},
                "email_sent": False
            }
            
    except Exception as e:
        error_msg = f"İşlem sırasında hata: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        return {
            "status": "error", 
            "message": error_msg,
            "diff": {},
            "email_sent": False
        }

# ——— Flask uygulaması ———
app = Flask(__name__)

@app.route("/", methods=["GET"])
def trigger():
    result = job_check_and_notify()
    return jsonify(result), 200 if result["status"] == "success" else 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()}), 200

if __name__ == "__main__":
    # Lokal test için
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
