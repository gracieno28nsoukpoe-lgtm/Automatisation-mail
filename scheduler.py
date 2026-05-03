import time
import sqlite3
import os
from datetime import datetime
from mailer import send_email, notify_sender

DB_FILE = "emails_data.db"

def process_scheduled_emails():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    now = datetime.now().isoformat()
    cursor.execute('''
        SELECT id, sender_email, sender_password, recipient_emails, subject, body, files, scheduled_time
        FROM emails
        WHERE status = 'pending' AND scheduled_time <= ?
    ''', (now,))

    emails = cursor.fetchall()

    for email in emails:
        email_id, sender, password, recipients, subject, body, files, scheduled_time = email

        print(f"Envoi en cours de l'e-mail #{email_id}...")
        success = send_email(sender, password, recipients, subject, body, files)

        if success:
            notify_sender(sender, password, subject, recipients)

            cursor.execute('''
                UPDATE emails
                SET status = 'sent'
                WHERE id = ?
            ''', (email_id,))
            conn.commit()
            print(f"E-mail #{email_id} envoyé avec succès !")
        else:
            print(f"Échec de l'envoi de l'e-mail #{email_id}.")

    conn.close()

if __name__ == "__main__":
    print("Démarrage du planificateur de tâches...")
    while True:
        process_scheduled_emails()
        time.sleep(30) # Vérifie toutes les 30 secondes