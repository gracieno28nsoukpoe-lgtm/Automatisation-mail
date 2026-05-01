import streamlit as st
import sqlite3
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from sheduler import process_scheduled_emails # Import de votre fonction d'envoi
import atexit

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Auto-Mailer Pro", layout="centered")

# --- INITIALISATION DU PLANIFICATEUR (SCHEDULER) ---
# Cette fonction tourne en arrière-plan tant que l'app est lancée
def start_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    # Vérifie les emails à envoyer toutes les 30 secondes
    scheduler.add_job(
        id='email_job',
        func=process_scheduled_emails,
        trigger='interval',
        seconds=30,
        replace_existing=True
    )
    if not scheduler.running:
        scheduler.start()
    return scheduler

# On lance le scheduler une seule fois grâce au session_state
if 'scheduler_started' not in st.session_state:
    start_scheduler()
    st.session_state['scheduler_started'] = True

# --- INTERFACE UTILISATEUR ---
st.title("📧 Automatisation d'Envoi d'E-mails")
st.markdown("Configurez vos envois programmés ci-dessous.")

# Barre latérale pour la sécurité (Optionnel mais recommandé)
with st.sidebar:
    st.header("Paramètres de connexion")
    sender_email = st.text_input("Votre Email Gmail")
    # Utilisation du Mot de passe d'application (16 caractères)
    sender_password = st.text_input("Mot de passe d'application", type="password")
    st.info("💡 Utilisez un 'Mot de passe d'application' Google, pas votre mot de passe habituel.")

# Formulaire d'envoi
with st.form("mail_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        recipient = st.text_input("Destinataire (Email)")
    with col2:
        subject = st.text_input("Objet du message")
    
    body = st.text_area("Corps du message")
    
    # Choix de la date et l'heure
    d = st.date_input("Date d'envoi")
    t = st.time_input("Heure d'envoi")
    scheduled_time = f"{d} {t}"

    submit = st.form_submit_button("Programmer l'envoi")

# --- LOGIQUE DE SAUVEGARDE ---
if submit:
    if not sender_email or not sender_password:
        st.error("Veuillez remplir vos identifiants dans la barre latérale.")
    else:
        try:
            conn = sqlite3.connect('emails.db')
            cursor = conn.cursor()
            # Création de la table si elle n'existe pas (évite l'erreur 'no such table')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_email TEXT,
                    sender_password TEXT,
                    recipient_emails TEXT,
                    subject TEXT,
                    body TEXT,
                    files TEXT,
                    scheduled_time TEXT,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            cursor.execute('''
                INSERT INTO emails (sender_email, sender_password, recipient_emails, subject, body, scheduled_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (sender_email, sender_password, recipient, subject, body, scheduled_time))
            
            conn.commit()
            conn.close()
            st.success(f"✅ E-mail programmé pour le {scheduled_time} !")
        except Exception as e:
            st.error(f"Erreur base de données : {e}")

# --- AFFICHAGE DES TÂCHES EN ATTENTE ---
st.divider()
st.subheader("📋 Liste des envois programmés")
try:
    conn = sqlite3.connect('emails.db')
    df = pd.read_sql_query("SELECT recipient_emails, subject, scheduled_time, status FROM emails", conn)
    st.table(df)
    conn.close()
except:
    st.write("Aucun envoi programmé pour le moment.")