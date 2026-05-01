import streamlit as st
import sqlite3
import pandas as pd
import os
from apscheduler.schedulers.background import BackgroundScheduler
from sheduler import process_scheduled_emails
import atexit

st.set_page_config(page_title="Auto-Mailer Pro", layout="wide")

# --- INITIALISATION DU SCHEDULER ---
if 'scheduler_started' not in st.session_state:
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(id='email_job', func=process_scheduled_emails, trigger='interval', seconds=30)
    scheduler.start()
    st.session_state['scheduler_started'] = True
    atexit.register(lambda: scheduler.shutdown())

# --- FONCTIONS DE BASE DE DONNÉES ---
def save_email(data):
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emails (sender_email, sender_password, recipient_emails, subject, body, files, scheduled_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    ''', data)
    conn.commit()
    conn.close()

# --- INTERFACE ---
st.title("🚀 Automatisation d'Envoi d'E-mails Professionnel")

with st.sidebar:
    st.header("🔐 Configuration de Sécurité")
    master_key = st.text_input("Créez votre Clé Maître (pour cette session)", type="password", help="Cette clé protège vos accès.")
    user_email = st.text_input("Votre Email Gmail")
    app_password = st.text_input("Mot de passe d'application Google", type="password")
    
    if not master_key:
        st.warning("⚠️ Définissez une clé maître pour activer le formulaire.")

# --- FORMULAIRE PRINCIPAL ---
if master_key:
    with st.container():
        st.subheader("📝 Préparer un nouvel envoi")
        
        col1, col2 = st.columns(2)
        with col1:
            dest = st.text_input("Destinataire")
            sujet = st.text_input("Objet")
        with col2:
            date_envoi = st.date_input("Date")
            heure_envoi = st.time_input("Heure")
        
        message = st.text_area("Message", height=150)
        uploaded_file = st.file_uploader("Joindre un fichier (Optionnel)", type=['pdf', 'docx', 'jpg', 'png'])

        # --- LOGIQUE DE VALIDATION ET CONFIRMATION ---
        if st.button("Programmer l'envoi"):
            # 1. Vérification des champs vides
            if not all([user_email, app_password, dest, sujet, message]):
                st.error("❌ Erreur : Tous les champs obligatoires doivent être remplis.")
            else:
                # 2. Fenêtre de confirmation (Streamlit natif)
                st.session_state.confirm_data = (
                    user_email, app_password, dest, sujet, message, 
                    uploaded_file.name if uploaded_file else None,
                    f"{date_envoi} {heure_envoi}"
                )
                st.warning("Veuillez confirmer les informations ci-dessous avant programmation.")
                st.write(f"**Vers :** {dest} | **Sujet :** {sujet} | **Heure :** {date_envoi} {heure_envoi}")
                
                if st.button("✅ OUI, CONFIRMER LA PROGRAMMATION"):
                    save_email(st.session_state.confirm_data)
                    st.success("🎯 E-mail enregistré et mis en file d'attente !")
                    if uploaded_file:
                        # Sauvegarde locale du fichier pour le scheduler
                        if not os.path.exists("attachments"): os.makedirs("attachments")
                        with open(os.path.join("attachments", uploaded_file.name), "wb") as f:
                            f.write(uploaded_file.getbuffer())

# --- AFFICHAGE ET GESTION ---
st.divider()
st.subheader("📊 File d'attente des messages")
try:
    conn = sqlite3.connect('emails.db')
    df = pd.read_sql_query("SELECT id, recipient_emails, subject, scheduled_time, status FROM emails", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()
except:
    st.info("La file d'attente est vide.")