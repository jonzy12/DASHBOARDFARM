import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587
SMTP_USER     = ""
SMTP_PASSWORD = ""


def send_reset_email(to_email: str, reset_token: str):
    reset_link = f"http://localhost:5173/reset-password/{reset_token}"

    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 500px;
                margin: 40px auto;
                background-color: white;
                border-radius: 8px;
                padding: 40px;
                border: 1px solid #ddd;
            }}
            h2 {{
                color: #1a1a2e;
                margin-bottom: 10px;
            }}
            p {{
                color: #444;
                font-size: 15px;
                line-height: 1.6;
            }}
            .button {{
                display: inline-block;
                margin-top: 24px;
                padding: 14px 32px;
                background-color: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }}
            .footer {{
                margin-top: 32px;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>איפוס סיסמה — DashFarmBoard</h2>
            <p>קיבלנו בקשה לאיפוס הסיסמה שלך.</p>
            <p>לחץ על הכפתור כדי לאפס את הסיסמה. הקישור תקף ל-5 דקות בלבד.</p>
            <a href="{reset_link}" class="button">אפס סיסמה</a>
            <p style="margin-top: 24px;">אם לא ביקשת לאפס סיסמה, אפשר להתעלם מהמייל הזה.</p>
            <div class="footer">DashFarmBoard — מערכת ניטור חקלאית</div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "איפוס סיסמה — DashFarmBoard"
    msg["From"]    = SMTP_USER
    msg["To"]      = to_email

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_email, msg.as_string())