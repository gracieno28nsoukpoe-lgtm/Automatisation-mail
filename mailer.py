import smtplib
from email.message import EmailMessage
import os

# --- CONFIGURATION BREVO ---
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "ton-email@exemple.com"  # Ton login Brevo
SMTP_PASSWORD = "ta-cle-api-generee"  # Ta clé SMTP Brevo
# ---------------------------

def send_email(recipients, subject, body, files=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f"Mon Système <{SMTP_USER}>"
    msg['To'] = recipients
    msg.set_content(body)

    # Gestion des pièces jointes
    if files:
        for path in files.split(','):
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    msg.add_attachment(
                        f.read(), 
                        maintype='application', 
                        subtype='octet-stream', 
                        filename=os.path.basename(path)
                    )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # Sécurise la connexion
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erreur Brevo : {e}")
        return False