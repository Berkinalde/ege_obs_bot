import os
import time
import schedule
from obs_scraper import login_and_get_grades
from storage import load_grades, save_grades, diff_grades
from notifier import send_email_notification

SON_NOTLAR_PATH = os.path.join(os.path.dirname(__file__), 'son_notlar.json')

def send_test_message():
    send_email_notification("OBS Bot Test Mesajı", "✅ Ege OBS Botu test mesajı: E-posta bildirimi çalışıyor!")
    print("Test e-posta mesajı gönderildi.")

def check_and_notify():
    try:
        current_grades = login_and_get_grades()
    except Exception as e:
        print(f"OBS'den notlar alınamadı: {e}")
        return

    old_grades = load_grades(SON_NOTLAR_PATH)
    if old_grades is None:
        # İlk çalışmada sadece kaydet, mesaj gönderme
        save_grades(SON_NOTLAR_PATH, current_grades)
        print("İlk veri kaydedildi.")
        return

    changes = diff_grades(old_grades, current_grades)
    if changes:
        for ders, notu in changes:
            subject = f"Yeni Not: {ders}"
            body = f"📢 Yeni not: {ders} - {notu}"
            send_email_notification(subject, body)
        save_grades(SON_NOTLAR_PATH, current_grades)
        print(f"{len(changes)} yeni not bildirimi e-posta ile gönderildi.")
    else:
        print("Değişiklik yok.")


def main():
    send_test_message()  # Sadece ilk başlatmada test mesajı gönder
    schedule.every(10).minutes.do(check_and_notify)
    print("Ege OBS botu başlatıldı. Notlar 10 dakikada bir kontrol edilecek.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
