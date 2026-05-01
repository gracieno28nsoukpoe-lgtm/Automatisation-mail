import smtplib
from email.message import EmailMessage
import os

def send_email(sender, password, recipients, subject, body, files=None):
    """Envoie un e-mail avec ou sans pièces jointes via SMTP."""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    msg.set_content(body)

    if files:
        # Les fichiers sont séparés par des virgules
        file_list = files.split(',')
        for file_path in file_list:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    file_name = os.path.basename(file_path)
                    msg.add_attachment(
                        file_data, 
                        maintype='application', 
                        subtype='octet-stream', 
                        filename=file_name
                    )

    try:
        # Envoi via SMTP (Exemple pour un compte Gmail, utilisez le port 587 si nécessaire)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")
        return False

def notify_sender(sender, password, subject, original_recipient):
    """Envoie une notification à l'expéditeur une fois le mail envoyé."""
    notify_subject = f"Confirmation d'envoi : {subject}"
    notify_body = (
        f"Bonjour,\n\nVotre e-mail ayant pour objet '{subject}' "
        f"destiné à {original_recipient} a été envoyé avec succès !"
    )
    send_email(sender, password, sender, notify_subject, notify_body)