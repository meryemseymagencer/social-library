import smtplib
from email.mime.text import MIMEText

SMTP_EMAIL = "seymabetul90@gmail.com"
SMTP_PASSWORD = "kokb uwut guxz vehr"

def send_reset_code(email: str, code: str):
    msg = MIMEText(
        f"Şifre sıfırlama kodunuz: {code}\n\nBu kod 5 dakika boyunca geçerlidir."
    )
    msg["Subject"] = "Social Library – Şifre Sıfırlama Kodu"
    msg["From"] = SMTP_EMAIL
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, email, msg.as_string())
