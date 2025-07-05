import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

def send_email_notification(subject: str, body: str):
    # 1) Ortam değişkenlerini alın
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASS")
    recipient = os.getenv("TO_EMAIL")
    
    if not user or not password or not recipient:
        raise EnvironmentError("Lütfen GMAIL_USER, GMAIL_PASS ve TO_EMAIL ortam değişkenlerini tanımlayın.")

    # 2) Mesajı oluşturun
    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        # 3) Bağlantıyı açın, TLS'e geçin ve login olun
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.set_debuglevel(0)   # 1 yaparsanız protokol konuşmasını görebilirsiniz
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, password)

            # 4) Mesajı gönderin
            smtp.send_message(msg)
        print("📧 Mail başarıyla gönderildi.")
        return True
    except smtplib.SMTPAuthenticationError as auth_err:
        # Gmail 2FA veya app-pass sorunu varsa buraya düşer
        code, resp = auth_err.smtp_code, auth_err.smtp_error.decode()
        print(f"⚠️ Kimlik doğrulama başarısız ({code}): {resp}")
        print("→ Hesabınızda 2FA açıksa bir App Password oluşturup GMAIL_PASS olarak kullanın.")
        return False
    except smtplib.SMTPRecipientsRefused as rj_err:
        print(f"⚠️ Alıcı reddedildi: {rj_err.recipients}")
        return False
    except Exception as e:
        print(f"❌ E-posta gönderilirken beklenmeyen bir hata oluştu: {e}")
        return False

if __name__ == "__main__":
    send_email_notification(
        subject="Test Mail",
        body="Merhaba, bu bir test mesajıdır."
    )
