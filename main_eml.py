#!/usr/bin/env python3
"""
Script pour lire les fichiers .eml d'un dossier local (Export Zimbra)
et générer une page HTML avec les annonces d'événements

Utile pour tester l'extraction avant de se connecter à IMAP
"""

import os
import sys
import email
from pathlib import Path
from email.header import decode_header as decode_header_func
from email_reader import EventExtractor, HTMLGenerator


def read_eml_files(folder_path: str, limit: int = 50) -> list:
    """Lit les fichiers .eml d'un dossier"""
    emails = []
    
    if not os.path.isdir(folder_path):
        print(f"❌ Le dossier n'existe pas: {folder_path}")
        return emails
    
    eml_files = sorted(
        Path(folder_path).glob("*.eml"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:limit]
    
    print(f"📂 Lecture de {len(eml_files)} fichier(s) EML...")
    
    for eml_file in eml_files:
        try:
            with open(eml_file, 'rb') as f:
                msg = email.message_from_binary_file(f)
                
            subject = decode_header(msg.get("Subject", ""))
            sender = decode_header(msg.get("From", ""))
            date_str = msg.get("Date", "")
            body = get_body(msg)
            
            emails.append({
                "subject": subject,
                "from": sender,
                "date": date_str,
                "body": body,
                "message_id": msg.get("Message-ID", ""),
                "filename": eml_file.name
            })
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la lecture de {eml_file.name}: {e}")
            continue
    
    print(f"✓ {len(emails)} email(s) lu(s)")
    return emails


def decode_header(header: str) -> str:
    """Décode les en-têtes email"""
    decoded_parts = []
    for part, encoding in decode_header_func(header):
        if isinstance(part, bytes):
            decoded_parts.append(part.decode(encoding or "utf-8", errors="ignore"))
        else:
            decoded_parts.append(str(part) if part else "")
    return "".join(decoded_parts)


def get_body(msg: email.message.Message) -> str:
    """Extrait le corps du message (texte ou HTML)"""
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = part.get("Content-Disposition", "")
            
            if "attachment" not in content_disposition:
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body = payload.decode("utf-8", errors="ignore")
                        else:
                            body = str(payload)
                        return body
                    except:
                        pass
    
    try:
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            body = payload.decode("utf-8", errors="ignore")
        else:
            body = str(payload) if payload else ""
    except:
        body = msg.get_payload(decode=False)
        if isinstance(body, bytes):
            try:
                body = body.decode("utf-8", errors="ignore")
            except:
                body = str(body)
    
    return body


def main():
    """Fonction principale"""
    
    email_folder = "./CE"
    
    if not os.path.isdir(email_folder):
        print(f"❌ Dossier '{email_folder}' non trouvé")
        return
    
    print(f"📧 Lecture des emails depuis: {os.path.abspath(email_folder)}\n")
    
    try:
        # Étape 1: Lecture des fichiers .eml
        emails = read_eml_files(email_folder, limit=50)
        
        if not emails:
            print("❌ Aucun email trouvé")
            return
        
        # Étape 2: Extraction des informations d'événement
        print("\n🔍 Extraction des informations d'événement...")
        extractor = EventExtractor()
        events = []
        
        for email_dict in emails:
            try:
                event_info = extractor.extract_event_info(email_dict)
                events.append(event_info)
                
                # Affiche les infos extraites
                print(f"\n  📌 {event_info['subject'][:60]}...")
                print(f"     📅 Date: {event_info['date']}")
                print(f"     📍 Lieu: {event_info['location']}")
                
            except Exception as e:
                print(f"⚠️  Erreur lors de l'extraction: {e}")
                continue
        
        print(f"\n✓ {len(events)} événement(s) extrait(s)")
        
        # Filtre les événements avec une date
        events_filtered = [e for e in events if e['date'] != 'Non spécifiée']
        print(f"✓ {len(events_filtered)} événement(s) avec date trouvée(s)")
        
        # Étape 3: Génération de la page HTML
        print("\n🎨 Génération de la page HTML...")
        generator = HTMLGenerator("Annonces d'événements - Test EML")
        generator.add_events(events_filtered if events_filtered else events)
        output_file = generator.generate("events.html")
        
        print(f"\n✅ Succès! Ouvrez le fichier: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
