import sqlite3
from datetime import datetime

DB_FILE = "emails_data.db"

def init_db():
    """Initialise la base de données et crée la table si elle n'existe pas."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT NOT NULL,
            sender_password TEXT NOT NULL,
            recipient_emails TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT,
            files TEXT,
            scheduled_time TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

def save_email(sender_email, sender_password, recipient_emails, subject, body, files, scheduled_time):
    """Sauvegarde un e-mail dans la base de données."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emails (sender_email, sender_password, recipient_emails, subject, body, files, scheduled_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (sender_email, sender_password, recipient_emails, subject, body, files, scheduled_time.isoformat()))
    conn.commit()
    conn.close()