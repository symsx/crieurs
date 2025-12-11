#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal pour lire les emails et générer une page HTML
Adapté pour Zimbra Free avec dossier "CE"
Utilise l'extraction consolidée des événements
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


# ==================== END EXTRACTION FUNCTIONS ====================


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
    
    # Demander les identifiants si l'option est activée ou s'ils ne sont pas fournis
    if PROMPT_FOR_CREDENTIALS or not EMAIL or not PASSWORD:
        if PROMPT_FOR_CREDENTIALS:
            print("\n🔐 Mode saisie interactive activé\n")
        else:
            print("\n⚠️  Identifiants manquants dans le fichier .env\n")
        
        if not EMAIL:
            EMAIL = input("📧 Adresse email: ").strip()
        elif PROMPT_FOR_CREDENTIALS:
            email_input = input(f"📧 Adresse email [{EMAIL}]: ").strip()
            if email_input:
                EMAIL = email_input
        
        if not PASSWORD:
            import getpass
            PASSWORD = getpass.getpass("🔑 Mot de passe: ")
        elif PROMPT_FOR_CREDENTIALS:
            import getpass
            password_input = getpass.getpass("🔑 Mot de passe [***]: ")
            if password_input:
                PASSWORD = password_input
    
    if not EMAIL or not PASSWORD:
        print("❌ Erreur: Email et mot de passe requis")
        return
    
    try:
        # Étape 1: Connexion et récupération des emails
        print(f"\n📧 Connexion à {EMAIL} sur {IMAP_SERVER}...")
        reader = EmailReader(EMAIL, PASSWORD, IMAP_SERVER, IMAP_PORT)
        
        # Récupère les emails du dossier spécifié
        print(f"📂 Lecture du dossier '{MAIL_FOLDER}'...")
        if DOMAIN_FILTER:
            print(f"🔍 Filtre: domaine *{DOMAIN_FILTER}")
        
        emails = reader.get_emails(folder=MAIL_FOLDER, limit=EMAIL_LIMIT, domain_filter=DOMAIN_FILTER)
        reader.close()
        
        if not emails:
            print(f"❌ Aucun email trouvé dans le dossier '{MAIL_FOLDER}'")
            if DOMAIN_FILTER:
                print(f"   (avec le filtre domaine: *{DOMAIN_FILTER})")
            print("\n💡 Vérifiez:")
            print("  - Le nom du dossier dans .env (sensible à la casse)")
            print("  - Que le dossier existe dans votre boîte mail")
            if DOMAIN_FILTER:
                print("  - Que le filtre DOMAIN_FILTER est correct")
            return
        
        # Filtre les emails pour ne garder que "crieur-des-sorties"
        print(f"🔍 Filtre: sujet contenant 'crieur-des-sorties'")
        emails_filtered = [e for e in emails if 'crieur-des-sorties' in e.get('subject', '').lower()]
        print(f"✓ {len(emails_filtered)}/{len(emails)} email(s) avec le sujet 'crieur-des-sorties'")
        
        if not emails_filtered:
            print("❌ Aucun email avec le sujet 'crieur-des-sorties' trouvé")
            return
        
        emails = emails_filtered
        
        # Étape 2: Extraction consolidée des événements
        print("\n🔍 Extraction consolidée des événements...")
        all_events_consolidated = []
        
        for email in emails:
            email_content = email['body']
            email_date = email['date']  # Date formatée en français
            
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
            print("❌ Aucun événement extrait")
            return
        
        # Applique les corrections manuelles d'annonces si le fichier existe
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
                            print(f"  Correction appliquée: {event_title}")
                            for field, value in corrections[event_title].items():
                                if field == "date":
                                    event['date_heure_sommaire'] = value
                                else:
                                    event[field] = value
            except json.JSONDecodeError:
                print("  ⚠️  Impossible de lire corrections_annonces.json")
        
        # Étape 3: Conversion au format pour HTMLGenerator
        print("\n🎨 Génération de la page HTML...")
        
        # Convertit les événements consolidés au format attendu par HTMLGenerator
        events_html_format = []
        for event in all_events_consolidated:
            # Prépare les liens (agenda, site, pièces jointes)
            links = []
            if event['lien']:
                links.append(event['lien'])
            if event['agenda']:
                links.append(event['agenda'])
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
                'email_date': event.get('email_date', 'Non spécifiée'),  # Date de réception
                'organizer_email': event['mailorga']
            }
            events_html_format.append(event_html)
        
        generator = HTMLGenerator("Annonces Crieur")
        generator.add_events(events_html_format)
        
        # Déterminer les chemins de sortie (depuis src/, on remonte au root)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "output")
        output_annonces = os.path.join(output_dir, "annonces.html")
        output_carte = os.path.join(output_dir, "carte_des_annonces.html")
        
        output_file = generator.generate(output_annonces)
        
        # Étape 4: Génération de la carte interactive
        print("\n🗺️  Génération de la carte interactive...")
        map_file = generator.generate_map_html(output_carte)
        
        print(f"\n✅ Succès!")
        print(f"   • Page HTML: {os.path.abspath(output_file)}")
        print(f"   • Carte interactive: {os.path.abspath(map_file)}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

