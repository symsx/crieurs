#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal v2 - Traite deux sources d'annonces
- crieur-des-sorties (événements de sorties)
- crieur-libre-expression (annonces en expression libre)
"""

import sys
import os
import re
import json
import unicodedata
from email_reader import EmailReader, HTMLGenerator


# ==================== EXTRACTION FUNCTIONS ====================

def extract_phone_number(text: str) -> str:
    """Extrait un numéro de téléphone du texte"""
    phone_pattern = r'0[1-9](?:[\s\.\-]?\d{2}){4}'
    matches = re.findall(phone_pattern, text)
    if matches:
        phone = matches[0]
        phone_clean = re.sub(r'[\s\.\-]', '', phone)
        return phone_clean
    return ""


def extract_whatsapp_link(text: str) -> str:
    """Extrait un lien WhatsApp du texte"""
    whatsapp_pattern = r'https://chat\.whatsapp\.com/[^\s\n<>]+'
    match = re.search(whatsapp_pattern, text)
    if match:
        return match.group(0).strip()
    return ""


def extract_second_email(text: str) -> str:
    """Extrait une adresse email du descriptif"""
    email_pattern = r'\b([a-zA-Z0-9._%+-]+\s*@\s*[a-zA-Z0-9.\s-]+\.[a-zA-Z]{2,4})'
    matches = re.findall(email_pattern, text)
    if matches and len(matches) > 0:
        email = matches[0].replace(' ', '')
        return email
    return ""


def clean_text(text: str) -> str:
    """Nettoie le texte"""
    text = text.replace('\r', '')
    text = text.replace('\n', ' ')
    cleaned = []
    for char in text:
        category = unicodedata.category(char)
        if category[0] in ('L', 'N', 'P', 'Z'):
            cleaned.append(char)
        elif ord(char) < 128 and char.isprintable():
            cleaned.append(char)
    text = ''.join(cleaned)
    text = re.sub(r' +', ' ', text)
    return text.strip()


def extract_sommaire(email_content: str) -> str:
    """Extrait le sommaire entre "Sommaire :" et "------..." """
    match = re.search(
        r'Sommaire\s*:\s*\n(.*?)(?:\n-{10,}|\nMessage-ID:)',
        email_content,
        re.DOTALL
    )
    if match:
        sommaire = match.group(1)
        return sommaire.strip()
    return ""


def parse_events_from_sommaire(sommaire_text: str) -> list:
    """Parse les événements du sommaire"""
    events = []
    lines = sommaire_text.split('\n')
    
    current_event = None
    for line in lines:
        line = line.strip()
        
        if re.match(r'^\*\s+\d+', line):
            if current_event:
                events.append(current_event)
            
            num_match = re.match(r'^\*\s+(\d+)', line)
            numero = int(num_match.group(1)) if num_match else 0
            
            line = re.sub(r'^\*\s+\d+\s*-?\s*', '', line)
            
            current_event = {
                'numero': numero,
                'texte_complet': line,
                'types': [],
                'titre': '',
                'date_heure': '',
                'organisateur': '',
                'email': ''
            }
        
        elif current_event and line:
            current_event['texte_complet'] += ' ' + line
    
    if current_event:
        events.append(current_event)
    
    for event in events:
        parse_event_fields(event)
    
    return events


def parse_event_fields(event: dict):
    """Parse les champs d'un événement"""
    text = event['texte_complet']
    
    types = re.findall(r'\[([^\]]+)\]', text)
    event['types'] = types
    
    remaining = re.sub(r'^\s*(\[([^\]]+)\]\s*)+', '', text)
    remaining = re.sub(r'^\s*-\s*', '', remaining)
    
    email_match = re.search(r'<([^>]+)>', remaining)
    if email_match:
        event['email'] = email_match.group(1).strip()
        remaining = re.sub(r'<[^>]+>', '', remaining).strip()
    
    parts = [p.strip() for p in remaining.split(' - ')]
    
    if len(parts) >= 1:
        event['titre'] = clean_text(parts[0])
    if len(parts) >= 2:
        event['date_heure'] = clean_text(parts[1])
    if len(parts) >= 3:
        event['organisateur'] = clean_text(' - '.join(parts[2:]).strip())


def extract_messages(email_content: str) -> list:
    """Extrait chaque message individuel commençant par "Message-ID: " """
    messages = []
    
    parts = email_content.split('Message-ID: ')
    
    for part in parts[1:]:
        lines = part.split('\n', 1)
        message_id = lines[0].strip() if lines else ""
        content = lines[1] if len(lines) > 1 else ""
        
        messages.append({
            'message_id': message_id,
            'content': content,
            'quand': '',
            'lieu': '',
            'descriptif': '',
            'telephone': '',
            'whatsapp': '',
            'mailcontact': '',
            'lien': '',
            'agenda': '',
            'pièces_jointes': []
        })
    
    return messages


def extract_message_fields(message: dict):
    """Extrait les champs d'un message"""
    content = message['content']
    
    # Extrait "Quand : "
    quand_match = re.search(
        r'Quand\s*:\s*(.*?)(?=Où\s*:)',
        content,
        re.DOTALL
    )
    if quand_match:
        quand_text = quand_match.group(1).strip()
        quand_text = clean_text(quand_text)
        message['quand'] = quand_text
    
    # Extrait "Où : "
    lieu_match = re.search(
        r'Où\s*:\s*(.*?)(?=Descriptif)',
        content,
        re.DOTALL
    )
    if lieu_match:
        lieu_text = lieu_match.group(1).strip()
        lieu_text = clean_text(lieu_text)
        message['lieu'] = lieu_text
    
    # Extrait "Descriptif"
    descriptif_match = re.search(
        r'Descriptif\s*\n\s*-+\s*\n+(.*?)(?:-->\s*Visitez|-->\s*Une pièce jointe|📅\s*Cet événement|^-{10,})',
        content,
        re.DOTALL | re.MULTILINE
    )
    if descriptif_match:
        descriptif_text = descriptif_match.group(1).strip()
        # Extraits AVANT nettoyage
        phone = extract_phone_number(descriptif_text)
        message['telephone'] = phone
        whatsapp = extract_whatsapp_link(descriptif_text)
        message['whatsapp'] = whatsapp
        mailcontact = extract_second_email(descriptif_text)
        message['mailcontact'] = mailcontact
        # Nettoyage
        descriptif_text = clean_text(descriptif_text)
        message['descriptif'] = descriptif_text
    
    # Extrait les liens
    lien_match = re.search(
        r'-->\s*Visitez le site internet de l\'événement\s*:\s*(\S+)',
        content,
        re.DOTALL
    )
    if lien_match:
        lien = lien_match.group(1).strip()
        message['lien'] = lien
    
    # Extrait le lien agenda
    agenda_match = re.search(
        r'📅\s*Cet événement a été ajouté à l\'agenda des sorties des crieurs\s*:\s*(\S+)',
        content,
        re.DOTALL
    )
    if agenda_match:
        agenda_lien = agenda_match.group(1).strip()
        message['agenda'] = agenda_lien
    
    # Extrait les pièces jointes
    pièces_jointes = []
    pj_match = re.search(
        r'-->\s*Une pièce jointe est disponible\s*:\s*(.*?)(?:^-{10,}|Contactez|Ne répondez)',
        content,
        re.DOTALL | re.MULTILINE
    )
    if pj_match:
        pj_section = pj_match.group(1).strip()
        liens = re.findall(r'https://gco\.ouvaton\.org/wp-content/[^\s\n<>]*', pj_section)
        pièces_jointes = liens
    
    message['pièces_jointes'] = pièces_jointes


def consolidate_events(sommaire_events: list, messages: list) -> list:
    """Consolide les informations du sommaire et des messages"""
    consolidated = []
    
    for event in sommaire_events:
        numero = event['numero']
        
        message = messages[numero - 1] if numero <= len(messages) else None
        
        if message:
            extract_message_fields(message)
            
            consolidated_event = {
                'numero': numero,
                'types': event['types'],
                'titre': event['titre'],
                'date_heure_sommaire': event['date_heure'],
                'organisateur': event['organisateur'],
                'mailorga': event['email'],
                'quand_detail': message['quand'],
                'lieu_detail': message['lieu'],
                'descriptif': message['descriptif'],
                'telephone': message['telephone'],
                'whatsapp': message['whatsapp'],
                'mailcontact': message['mailcontact'],
                'lien': message['lien'],
                'agenda': message['agenda'],
                'pièces_jointes': message['pièces_jointes']
            }
            consolidated.append(consolidated_event)
    
    return consolidated


def extract_libre_expression_events(email_content: str) -> list:
    """
    Extrait les événements d'expression libre depuis le contenu email brut.
    
    Format attendu pour expression libre:
    - Texte entre lignes de tirets
    - Pas de structure Quand/Où/Descriptif
    - Pas de date ni lieu structurés
    - Texte libre entre deux séries de tirets
    """
    events = []
    
    # Extrait le sommaire pour obtenir les titres et emails
    sommaire = extract_sommaire(email_content)
    if not sommaire:
        return events
    
    sommaire_events = parse_events_from_sommaire(sommaire)
    
    # Extrait les messages individuels
    parts = email_content.split('Message-ID: ')
    
    for idx, part in enumerate(parts[1:], 1):
        lines = part.split('\n', 1)
        message_content = lines[1] if len(lines) > 1 else ""
        
        # Trouve le titre et email correspondants du sommaire
        titre = ""
        email_auteur = ""
        if idx <= len(sommaire_events):
            titre = sommaire_events[idx - 1]['titre']
            email_auteur = sommaire_events[idx - 1]['email']
        
        # Extrait le texte entre les tirets
        # Début: une série de tirets (au moins 10)
        # Fin: "-------------------------" (25 tirets)
        texte_match = re.search(
            r'-{10,}\s*\n+(.*?)\n+\-{25,}',
            message_content,
            re.DOTALL
        )
        
        if texte_match:
            texte_brut = texte_match.group(1).strip()
            
            # Nettoie le texte : enlève le titre au début s'il est présent
            # Le titre est souvent suivi de tirets "======..."
            texte_brut = re.sub(r'^[^=]*=+\s*\n+', '', texte_brut, flags=re.DOTALL)
            
            # Extrait les infos de contact du texte
            phone = extract_phone_number(texte_brut)
            whatsapp = extract_whatsapp_link(texte_brut)
            mailcontact = extract_second_email(texte_brut)
            
            # Crée l'événement simplifié pour expression libre
            event = {
                'numero': idx,
                'titre': titre,
                'mailorga': email_auteur,
                'texte_libre': clean_text(texte_brut),
                'telephone': phone,
                'whatsapp': whatsapp,
                'mailcontact': mailcontact,
                # Pas de date, lieu, ou descriptif structuré pour expression libre
                'date_heure_sommaire': '',
                'lieu_detail': '',
                'quand_detail': '',
                'organisateur': '',
                'descriptif': '',
                'lien': '',
                'agenda': '',
                'pièces_jointes': [],
                'types': []
            }
            events.append(event)
    
    return events

# ==================== END EXTRACTION FUNCTIONS ====================


def process_annonces_source(email: str, password: str, imap_server: str, imap_port: int,
                           mail_folder: str, email_limit: int, domain_filter: str,
                           source: dict) -> bool:
    """
    Traite une source d'annonces (sorties ou expression libre)
    Retourne True si succès, False sinon
    """
    try:
        # Étape 1: Connexion et récupération des emails
        print(f"\n📧 Connexion à {email} sur {imap_server}...")
        reader = EmailReader(email, password, imap_server, imap_port)
        
        # Récupère les emails du dossier spécifié
        print(f"📂 Lecture du dossier '{mail_folder}'...")
        if domain_filter:
            print(f"🔍 Filtre domaine: *{domain_filter}")
        
        emails = reader.get_emails(folder=mail_folder, limit=email_limit, domain_filter=domain_filter)
        reader.close()
        
        if not emails:
            print(f"❌ Aucun email trouvé dans le dossier '{mail_folder}'")
            return False
        
        # Filtre les emails pour le sujet spécifié
        print(f"🔍 Filtre sujet: '{source['filter']}'")
        emails_filtered = [e for e in emails if source['filter'] in e.get('subject', '').lower()]
        print(f"✓ {len(emails_filtered)}/{len(emails)} email(s) trouvé(s)")
        
        if not emails_filtered:
            print(f"⚠️  Aucun email avec le sujet '{source['filter']}'")
            return False
        
        emails = emails_filtered
        
        # Étape 2: Extraction consolidée des événements
        print("\n🔍 Extraction consolidée des événements...")
        all_events_consolidated = []
        
        # Utilise la logique d'extraction appropriée selon la source
        if source['filter'] == 'crieur-libre-expression':
            # Expression libre: texte libre entre tirets
            for email_msg in emails:
                email_content = email_msg['body']
                email_date = email_msg['date']
                
                events = extract_libre_expression_events(email_content)
                
                # Ajoute la date de l'email à chaque événement
                for event in events:
                    event['email_date'] = email_date
                
                all_events_consolidated.extend(events)
        else:
            # Sorties: extraction sommaire + messages structurés
            for email_msg in emails:
                email_content = email_msg['body']
                email_date = email_msg['date']
                
                # Extrait sommaire et messages
                sommaire = extract_sommaire(email_content)
                if not sommaire:
                    continue
                
                events_sommaire = parse_events_from_sommaire(sommaire)
                messages = extract_messages(email_content)
                
                # Consolide les événements
                events_consolidated = consolidate_events(events_sommaire, messages)
                
                # Ajoute la date de l'email à chaque événement
                for event in events_consolidated:
                    event['email_date'] = email_date
                
                all_events_consolidated.extend(events_consolidated)
        
        print(f"✓ {len(all_events_consolidated)} événement(s) extrait(s)")

        
        if not all_events_consolidated:
            print(f"⚠️  Aucun événement extrait")
            return False
        
        # Applique les corrections manuelles d'annonces
        base_dir = os.path.dirname(os.path.abspath(__file__))
        corrections_file = os.path.join(os.path.dirname(base_dir), "data", "corrections_annonces.json")
        
        if os.path.exists(corrections_file):
            try:
                with open(corrections_file, "r", encoding="utf-8") as f:
                    corrections_data = json.load(f)
                    corrections = corrections_data.get("corrections", {})
                    
                    for event in all_events_consolidated:
                        event_title = event['titre']
                        if event_title in corrections:
                            print(f"  ✓ Correction: {event_title}")
                            for field, value in corrections[event_title].items():
                                if field == "date":
                                    event['date_heure_sommaire'] = value
                                else:
                                    event[field] = value
            except json.JSONDecodeError:
                print("  ⚠️  Impossible de lire corrections_annonces.json")
        
        # Étape 3: Génération HTML
        print(f"\n🎨 Génération HTML pour {source['name']}...")
        
        # Convertit au format HTMLGenerator
        events_html_format = []
        for event in all_events_consolidated:
            if source['filter'] == 'crieur-libre-expression':
                # Expression libre: structure simplifiée
                event_html = {
                    'subject': event['titre'],
                    'date': '',  # Pas de date pour expression libre
                    'location': '',  # Pas de lieu pour expression libre
                    'description': event.get('texte_libre', ''),  # Texte libre à la place de descriptif
                    'links': None,
                    'telephone': event['telephone'],
                    'whatsapp': event['whatsapp'],
                    'mailcontact': event['mailcontact'],
                    'email_date': event.get('email_date', 'Non spécifiée'),
                    'organizer_email': event['mailorga'],
                    'is_libre_expression': True  # Marqueur pour le template
                }
            else:
                # Sorties: structure complète
                links = []
                if event.get('lien'):
                    links.append(event['lien'])
                if event.get('agenda'):
                    links.append(event['agenda'])
                if event.get('pièces_jointes'):
                    links.extend(event['pièces_jointes'])
                
                event_html = {
                    'subject': event['titre'],
                    'date': event['date_heure_sommaire'],
                    'location': event['lieu_detail'],
                    'description': event['descriptif'],
                    'links': links if links else None,
                    'telephone': event['telephone'],
                    'whatsapp': event['whatsapp'],
                    'mailcontact': event['mailcontact'],
                    'email_date': event.get('email_date', 'Non spécifiée'),
                    'organizer_email': event['mailorga'],
                    'is_libre_expression': False
                }
            events_html_format.append(event_html)
        
        generator = HTMLGenerator(source['title'])
        generator.add_events(events_html_format)
        # Définit le type de source pour le menu de navigation
        generator.source_type = source['name']  # 'Sorties' ou 'Expression Libre'
        
        # Chemins de sortie
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        output_annonces = os.path.join(output_dir, source['output_html'])
        output_carte = os.path.join(output_dir, source['output_map'])
        
        # Génère HTML et carte
        output_file = generator.generate(output_annonces)
        print(f"\n🗺️  Génération de la carte...")
        map_file = generator.generate_map_html(output_carte)
        
        print(f"\n✅ {source['name']} générée!")
        print(f"   • {os.path.basename(output_file)}")
        print(f"   • {os.path.basename(map_file)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur pour {source['name']}: {e}")
        import traceback
        traceback.print_exc()
        return False


def ftp_upload(output_dir: str):
    """Upload les fichiers HTML vers le serveur FTP"""
    from ftp_uploader import FTPUploader
    
    enable_ftp = os.getenv("ENABLE_FTP_UPLOAD", "false").lower() == "true"
    if not enable_ftp:
        return
    
    ftp_host = os.getenv("FTP_HOST", "").strip()
    ftp_port = int(os.getenv("FTP_PORT", "21"))
    ftp_user = os.getenv("FTP_USER", "").strip()
    ftp_password = os.getenv("FTP_PASSWORD", "").strip()
    ftp_remote_path = os.getenv("FTP_REMOTE_PATH", "/").strip()
    ftp_use_tls = os.getenv("FTP_USE_TLS", "false").lower() == "true"
    
    if not ftp_host or not ftp_user or not ftp_password:
        print("✗ Paramètres FTP incomplets")
        return
    
    uploader = FTPUploader(
        host=ftp_host,
        port=ftp_port,
        username=ftp_user,
        password=ftp_password,
        use_tls=ftp_use_tls
    )
    
    success, msg = uploader.connect()
    print(f"  {msg}")
    
    if not success:
        return
    
    try:
        print(f"  📁 Uploading vers {ftp_remote_path}...")
        uploaded, failed = uploader.upload_directory(output_dir, ftp_remote_path)
        
        if uploaded > 0:
            print(f"  ✓ {uploaded} fichier(s) uploadé(s)")
        if failed > 0:
            print(f"  ✗ {failed} fichier(s) échoué(s)")
    finally:
        uploader.close()


def main():
    """Fonction principale"""
    
    # Configuration
    EMAIL = os.getenv("EMAIL_ADDRESS", "").strip()
    PASSWORD = os.getenv("EMAIL_PASSWORD", "").strip()
    IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.free.fr")
    IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
    MAIL_FOLDER = os.getenv("MAIL_FOLDER", "CE")
    EMAIL_LIMIT = int(os.getenv("EMAIL_LIMIT", "50"))
    DOMAIN_FILTER = os.getenv("DOMAIN_FILTER", "").strip() or None
    PROMPT_FOR_CREDENTIALS = os.getenv("PROMPT_FOR_CREDENTIALS", "false").lower() == "true"
    
    # Demander les identifiants si nécessaire
    if PROMPT_FOR_CREDENTIALS or not EMAIL or not PASSWORD:
        if PROMPT_FOR_CREDENTIALS:
            print("\n🔐 Mode saisie interactive\n")
        
        if not EMAIL:
            EMAIL = input("📧 Email: ").strip()
        
        if not PASSWORD:
            import getpass
            PASSWORD = getpass.getpass("🔑 Mot de passe: ")
    
    if not EMAIL or not PASSWORD:
        print("❌ Email et mot de passe requis")
        return
    
    try:
        # Configuration des deux sources
        sources = [
            {
                'name': 'Sorties',
                'filter': 'crieur-des-sorties',
                'output_html': 'annonces.html',
                'output_map': 'carte_des_annonces.html',
                'title': 'Annonces Crieur'
            },
            {
                'name': 'Expression Libre',
                'filter': 'crieur-libre-expression',
                'output_html': 'expression_libre.html',
                'output_map': 'carte_expression_libre.html',
                'title': 'Expression Libre Crieur'
            }
        ]
        
        # Traite chaque source
        results = []
        for source in sources:
            print(f"\n{'='*60}")
            print(f"📰 {source['name']}")
            print(f"{'='*60}")
            
            success = process_annonces_source(
                EMAIL, PASSWORD, IMAP_SERVER, IMAP_PORT,
                MAIL_FOLDER, EMAIL_LIMIT, DOMAIN_FILTER,
                source
            )
            results.append((source['name'], success))
        
        # Upload FTP
        print(f"\n{'='*60}")
        enable_ftp = os.getenv("ENABLE_FTP_UPLOAD", "false").lower() == "true"
        if enable_ftp:
            print("📤 Upload FTP")
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(base_dir, "output")
            ftp_upload(output_dir)
        
        # Résumé
        print(f"\n{'='*60}")
        print("✅ Résumé:")
        for name, success in results:
            status = "✓" if success else "✗"
            print(f"  {status} {name}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
