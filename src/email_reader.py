"""
Lecteur d'emails et extracteur d'annonces
Connecte à une boîte aux lettres et extrait les informations d'événements
"""

import imaplib
import email
from email.message import Message
from email.header import decode_header
from datetime import datetime
import re
import json
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()


class EmailReader:
    """Classe pour lire les emails via IMAP"""
    
    def __init__(self, email_address: str, password: str, imap_server: str = "imap.free.fr", imap_port: int = 993):
        """
        Initialise la connexion à la boîte aux lettres
        
        Args:
            email_address: Adresse email
            password: Mot de passe ou token d'application
            imap_server: Serveur IMAP (par défaut Free)
            imap_port: Port IMAP (par défaut 993 pour SSL)
        """
        self.email_address = email_address
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.connection = None
        self.connect(email_address, password, imap_server, imap_port)
    
    def connect(self, email_address: str, password: str, imap_server: str, imap_port: int = 993):
        """Établit la connexion IMAP"""
        try:
            self.connection = imaplib.IMAP4_SSL(imap_server, imap_port)
            self.connection.login(email_address, password)
            print(f"✓ Connecté à {email_address}")
        except imaplib.IMAP4.error as e:
            print(f"✗ Erreur de connexion: {e}")
            raise
    
    def get_emails(self, folder: str = "INBOX", limit: int = 10, domain_filter: str = None) -> List[Dict]:
        """
        Récupère les emails d'un dossier
        
        Args:
            folder: Nom du dossier (INBOX par défaut)
            limit: Nombre d'emails à récupérer
            domain_filter: Filtrer par domaine (ex: "gco.ouvaton.net")
            
        Returns:
            Liste des emails avec métadonnées
        """
        try:
            self.connection.select(folder)
            status, messages = self.connection.search(None, "ALL")
            
            if status != "OK":
                print(f"✗ Erreur lors de la recherche dans {folder}")
                return []
            
            email_ids = messages[0].split()
            # Récupère les derniers emails en priorité
            email_ids = email_ids[-limit*2:]  # Récupère plus pour avoir assez après filtrage
            
            emails = []
            for email_id in reversed(email_ids):
                status, msg_data = self.connection.fetch(email_id, "(RFC822)")
                
                if status != "OK":
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Filtre par domaine si demandé
                if domain_filter:
                    sender = self._decode_header(msg.get("From", ""))
                    # Extrait le domaine de l'adresse email
                    if "@" in sender:
                        email_domain = sender.split("@")[-1].rstrip(">").strip()
                        if domain_filter not in email_domain:
                            continue
                
                email_dict = self._parse_email(msg)
                emails.append(email_dict)
                
                if len(emails) >= limit:
                    break
            
            print(f"✓ {len(emails)} email(s) récupéré(s)" + (f" du domaine {domain_filter}" if domain_filter else ""))
            return emails
            
        except Exception as e:
            print(f"✗ Erreur lors de la récupération: {e}")
            return []
    
    def _parse_email(self, msg: Message) -> Dict:
        """Extrait les informations d'un email"""
        subject = self._decode_header(msg.get("Subject", ""))
        sender = self._decode_header(msg.get("From", ""))
        date_str = msg.get("Date", "")
        
        # Convertit la date au format français
        formatted_date = self._format_email_date(date_str)
        
        # Récupère le contenu
        body = self._get_body(msg)
        
        return {
            "subject": subject,
            "from": sender,
            "date": formatted_date,
            "body": body,
            "message_id": msg.get("Message-ID", "")
        }
    
    def _format_email_date(self, date_str: str) -> str:
        """Convertit une date email RFC 2822 au format français avec heure locale"""
        from email.utils import parsedate_to_datetime
        from datetime import datetime, timezone
        
        try:
            # Parse la date RFC 2822
            dt = parsedate_to_datetime(date_str)
            
            # Convertit en fuseau horaire local (CET/CEST)
            # Python 3.6+: on peut utiliser astimezone() qui utilise le fuseau local du système
            if dt.tzinfo is not None:
                dt_local = dt.astimezone()
            else:
                dt_local = dt
            
            # Format français: "10 décembre 2025 à 14:40"
            mois_fr = [
                "", "janvier", "février", "mars", "avril", "mai", "juin",
                "juillet", "août", "septembre", "octobre", "novembre", "décembre"
            ]
            
            jour = dt_local.day
            mois = mois_fr[dt_local.month]
            annee = dt_local.year
            heure = dt_local.strftime("%H:%M")
            
            return f"{jour} {mois} {annee} à {heure}"
        except:
            # Si la conversion échoue, retourne la date brute
            return date_str
    
    def _decode_header(self, header: str) -> str:
        """Décode les en-têtes email"""
        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded_parts.append(part.decode(encoding or "utf-8", errors="ignore"))
            else:
                decoded_parts.append(part)
        return "".join(decoded_parts)
    
    def _get_body(self, msg: Message) -> str:
        """Extrait le corps du message (HTML ou texte)"""
        import quopri
        
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = part.get("Content-Disposition", "")
                
                if "attachment" not in content_disposition:
                    if content_type == "text/html":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        return body
                    elif content_type == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
        else:
            body = msg.get_payload(decode=True)
            if isinstance(body, bytes):
                body = body.decode("utf-8", errors="ignore")
        
        # Décode les encodages QUOTED-PRINTABLE restants
        if "=" in body and body.count("=") > 3:
            try:
                body = quopri.decodestring(body.encode()).decode("utf-8", errors="ignore")
            except:
                pass
        
        return body
    
    def close(self):
        """Ferme la connexion IMAP"""
        if self.connection:
            self.connection.close()
            print("✓ Connexion fermée")


class EventExtractor:
    """Classe pour extraire les informations d'événement des emails"""
    
    def __init__(self):
        # Patterns regex pour extraire informations
        # Format Zimbra: "Quand : du samedi 13 décembre 2025 à 19:05"
        self.date_patterns = [
            # Patterns avec 4 chiffres d'année (2025) EN PREMIER car plus spécifiques
            r"(?:dimanche|lundi|mardi|mercredi|jeudi|vendredi|samedi)\s+(\d{1,2}\s+\w+\s+\d{4})(?:\s|$)",
            r"Quand\s*(?::|=)\s*du\s+(?:\w+\s+)?(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4})",
            r"(?:Quand|QUAND|quand)\s*(?::|=)\s*du\s+(?:\w+\s+)?(\d{1,2}\s+[a-zàâäéèêëïîôöùûüœæç]+\s+\d{4})",
            # Patterns avec années 2-4 chiffres (moins spécifiques, pour compatibilité)
            r"(?:date|Date|DATE|le|le\s):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4})(?:\s|$)",  # 4 chiffres avec limite
            r"(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{2})(?:\s|$)",  # 2 chiffres avec limite
            r"(?:samedi|dimanche|lundi|mardi|mercredi|jeudi|vendredi)[,]?\s+(\d{1,2}\s+\w+\s+\d{2,4})"
        ]
        
        self.location_patterns = [
            # Les patterns "Où :" et "adresse :" sont prioritaires (plus fiables)
            r"Où\s*(?::|=)\s*([^\n=]+?)(?:\n|$|=)",
            r"O=C3=B9\s*(?::|=)\s*([^\n=]+?)(?:\n|$|=)",
            r"(?:adresse|Adresse|ADRESSE):\s*([^\n]+?)(?:\n|-{2,}|$)",
            r"(?:lieu|Lieu|LIEU|location):\s*([^\n]+?)(?:\n|-{2,}|$)",
            r"(?:à|À):\s*([^\n]+?)(?:\n|,|-{2,}|$)",
            # Pour "au/aux", on doit être plus restrictif et éviter les faux positifs
            # Ne capture que si suivi d'une majuscule ET ce n'est pas un mot trivial
            r"(?:Aux|au|Au|Au)\s+(?!hommes|femmes|enfants|personnes|gens)([A-Z][^\n-]*?)(?:\s+-\s+(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)|(?:\d{1,2}\s+(?:janv|févr|mars|avril|mai|juin|juil|août|sept|oct|nov|déc))|$|\n)"
        ]
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoie le texte en supprimant les émoticons et caractères spéciaux problématiques
        """
        if not text:
            return text
        
        # Supprime les émoticons courants (🎭🎪🎨🎬🎤🎸🎹🎺🎻🥁🎵🎶🎼🎧🎙️ etc)
        # et les caractères problématiques
        import unicodedata
        
        # Enlève les caractères de catégorie "So" (symbols other) qui incluent les émoticons
        # mais garde les caractères utiles comme ©, ®, °, etc.
        text = ''.join(ch if unicodedata.category(ch) != 'So' else '' for ch in text)
        
        # Supprime aussi les caractères de contrôle et autres non-affichables
        text = ''.join(ch if unicodedata.category(ch)[0] != 'C' else '' for ch in text)
        
        # Réduit les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_event_info(self, email_dict: Dict) -> Dict | List[Dict]:
        """Extrait les informations d'événement d'un email"""
        subject = email_dict["subject"]
        body = email_dict["body"]
        sender_from = email_dict.get("from", "")
        
        # Nettoie le HTML si présent
        if "<" in body:
            soup = BeautifulSoup(body, "html.parser")
            body_text = soup.get_text()
        else:
            body_text = body
        
        full_text = f"{subject}\n{body_text}"
        
        # Si le sujet contient "Compilation", c'est un digest de mailing list
        if "Compilation" in subject and "crieur" in subject.lower():
            # Cherche TOUS les événements à l'intérieur (marqués par "* X -")
            import re
            body_lines = body_text.split('\n')
            events = []
            processed_titles = set()  # Évite les doublons
            
            for i, line in enumerate(body_lines):
                # Cherche un numéro d'événement (format "* 1 -", "* 2 -", etc)
                match = re.match(r'\*\s*\d+\s*-\s*\[', line)
                if match:
                    # NETTOYAGE IMMÉDIAT: supprime les \r\n qui cassent les regex
                    # Cela évite les problèmes d'extraction quand les titres sont sur plusieurs lignes
                    line = re.sub(r'[\r\n]+', ' ', line)
                    line = re.sub(r'\s+', ' ', line)
                    
                    # Cherche les deux crochets (catégorie et lieu)
                    brackets = re.findall(r'\[([^\]]+)\]', line)
                    
                    # Combine cette ligne avec les suivantes pour avoir la ligne complète du sommaire
                    # (souvent multi-lignes pour inclure l'adresse)
                    full_entry = line
                    j = i + 1
                    while j < len(body_lines) and not re.match(r'\*\s*\d+\s*-', body_lines[j].strip()) and not "Message-ID:" in body_lines[j]:
                        next_line = body_lines[j].strip()
                        
                        # Arrête aux marqueurs de fin de sommaire (ligne vide, tirets ou autre événement)
                        if not next_line or next_line.startswith('-'):
                            break
                        
                        if next_line:
                            full_entry += " " + next_line
                        j += 1
                    
                    # Extrait le titre :
                    # Format: * 1 - [crieur-des-sorties] [Chalais] - Atelier conte - samedi 13 décembre 2025
                    # On veut : "Atelier conte"
                    
                    title = ""
                    if len(brackets) >= 2:
                        # Après [lieu], cherche le titre avant la date complète (jour + jour-mois-année)
                        # Pattern strict: cherche un jour + chiffre + mois (format de date valide)
                        # Pas juste n'importe quel jour/mois isolé dans le titre
                        after_brackets = re.search(
                            r'\]\s*-\s*(.+?)(?:\s(?:samedi|dimanche|lundi|mardi|mercredi|jeudi|vendredi)\s+\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre))',
                            full_entry,
                            re.IGNORECASE | re.DOTALL
                        )
                        if after_brackets:
                            title = after_brackets.group(1).strip()
                            # Nettoie les tirets finaux, espaces et caractères de contrôle
                            title = title.rstrip('- /').strip()
                            # Nettoie les \r, \n et espaces en trop
                            title = re.sub(r'[\r\n]+', ' ', title)  # Remplace retours à la ligne par espace
                            title = re.sub(r'\s+', ' ', title)  # Réduit espaces multiples en un
                            title = title.strip()
                    
                    # Évite les doublons
                    if not title or title in processed_titles or len(title) < 2:
                        continue
                    processed_titles.add(title)
                    
                    # Cherche la date et le lieu
                    event_block_lines = [full_entry]
                    date = self._extract_date(full_entry)
                    
                    # NOUVELLE STRATÉGIE pour les digests:
                    # 1. Cherche une adresse après la date dans la ligne du sommaire (often present)
                    # 2. Sinon, cherche le contexte complet pour un "Où :" avec adresse
                    # 3. Fallback au bracket si aucune adresse valide trouvée
                    
                    location = ""
                    
                    # Étape 1: Cherche l'adresse après la date dans le sommaire
                    # Pattern: jour + date + heure + " - " + adresse jusqu'à email
                    addr_in_summary = re.search(
                        r'(?:dimanche|lundi|mardi|mercredi|jeudi|vendredi|samedi).*?à\s+\d{1,2}:\d{2}\s*-\s*([^<\r\n]+)',
                        full_entry,
                        re.IGNORECASE
                    )
                    if addr_in_summary:
                        potential_addr = addr_in_summary.group(1).strip()
                        # Vérifie si c'est une adresse valide (contient code postal OU rue+numéro)
                        if re.search(r'\d{5}', potential_addr) or re.search(r'^\d+\s+', potential_addr):
                            location = potential_addr
                    
                    # Étape 2: Si pas trouvé dans le sommaire, cherche le contexte complet
                    if not location or location == "Non spécifié":
                        event_context = self._find_event_context(body_text, title)
                        if event_context:
                            location = self._extract_location(event_context)
                    
                    # Vérifie si c'est une adresse valide
                    has_postal_code = bool(re.search(r'\d{5}', location))
                    has_street_number = bool(re.search(r'^\d+\s+(?:rue|avenue|boulevard|chemin|place|square|allée|quai|cour|voie)', location, re.IGNORECASE))
                    is_valid_address = has_postal_code or has_street_number
                    
                    # Étape 3: Si pas trouvé ou pas une vraie adresse, utilise le bracket
                    if location == "Non spécifié" or (not is_valid_address and len(brackets) >= 2):
                        bracket_location = brackets[1].strip() if len(brackets) >= 2 else ""
                        if bracket_location:
                            location = bracket_location
                    
                    # Cherche la description en utilisant le titre
                    description = self._extract_description_from_digest(body_text, title)
                    
                    # Extrait l'email de l'organisateur depuis la ligne du sommaire
                    organizer_email = self._extract_organizer_email(full_entry)
                    
                    if date != "Non spécifiée":
                        events.append({
                            "subject": self._clean_text(title),
                            "date": self._clean_text(date),
                            "location": self._clean_text(location),
                            "description": self._clean_text(description),
                            "links": self._extract_links(body_text),
                            "body_preview": self._clean_text(body_text[:500]),
                            "email_date": email_dict["date"],
                            "from": sender_from,
                            "organizer_email": organizer_email
                        })
            
            # Retourne la liste des événements trouvés
            if events:
                return events
        
        return {
            "subject": self._clean_text(subject),
            "date": self._clean_text(self._extract_date(full_text)),
            "location": self._clean_text(self._extract_location(full_text)),
            "description": self._clean_text(self._extract_description(full_text)),
            "links": self._extract_links(full_text),
            "body_preview": self._clean_text(body_text[:500]),
            "email_date": email_dict["date"],
            "from": sender_from,
            "organizer_email": self._extract_organizer_email(full_text)
        }
    
    def _extract_date(self, text: str) -> str:
        """Extrait la date de l'événement"""
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.UNICODE)
            if match:
                date_str = match.group(1).strip()
                # Nettoie les encodages de emails
                date_str = date_str.replace("=C3=A9", "é").replace("=C3=A8", "è").replace("=C3=AA", "ê")
                date_str = date_str.replace("=2E", ".").replace("=3D", "=")
                return date_str
        return "Non spécifiée"
    
    def _extract_links(self, text: str) -> list:
        """Extrait les liens URL du texte"""
        # Pattern pour les URLs
        url_pattern = r'https?://[^\s\n<>"\\)=]+'
        links = re.findall(url_pattern, text)
        # Nettoie les liens (supprime les caractères de fin problématiques)
        links = [link.rstrip('.,;:)]}') for link in links]
        # Filtre les liens:
        # - Pour gco.ouvaton.org: ne garder que /wp-content/ (pièces jointes)
        # - Pour les autres domaines: garder tous
        filtered_links = []
        for link in links:
            if 'gco.ouvaton.org' in link:
                # Pour gco.ouvaton.org, ne garder que les liens vers /wp-content/
                if '/wp-content/' in link:
                    filtered_links.append(link)
            else:
                # Pour les autres domaines, garder le lien
                filtered_links.append(link)
        
        # Supprime les doublons en gardant l'ordre
        seen = set()
        unique_links = []
        for link in filtered_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        return unique_links[:3]  # Limite à 3 liens max
    
    def _extract_organizer_email(self, text: str) -> str:
        """Extrait l'adresse email de l'organisateur (généralement en fin de ligne dans les digests)"""
        # Cherche une adresse email: abc@domaine.ext
        # Limite le TLD à 2-4 caractères (les vrais TLDs font 2-4 caractères typiquement)
        # Utilise une negative lookahead pour éviter de capturer du texte qui suit
        email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})(?![a-zA-Z0-9-])'
        matches = re.findall(email_pattern, text)
        
        # Retourne la dernière adresse email trouvée (généralement l'organisateur)
        if matches:
            # Filtre les adresses communes qui ne sont pas des organisateurs
            organizer_emails = [e for e in matches if 'noreply' not in e.lower() and 'no-reply' not in e.lower()]
            if organizer_emails:
                return organizer_emails[-1]  # Dernière address trouvée
            return matches[-1] if matches else ""
        
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extrait le lieu de l'événement"""
        # Liste des principales communes de Dordogne
        communes_dordogne = [
            "Nontron", "Thiviers", "Saint-Yrieix", "Périgueux", "Bergerac", "Sarlat", "Ribérac",
            "Montbron", "Chalais", "Saint-Pardoux-la-Rivière", "Champs-Romain", "Soudat",
            "Rudeau-Ladosse", "Saint-Saud-Lacoussière", "Saint-Jory", "Saint-Jory-de-Chalais",
            "Marval", "Piégut-Pluviers", "Champniers-et-Reilhac", "Champagnac-la-Rivière",
            "La Rochebeaucourt-et-Argentine", "Milhac-de-Nontron", "Chalard", "Saint-Estèphe",
            "Saint-Mathieu", "Saint-Pierre-de-Frugie", "La Coquille", "Nexon", "Limoges"
        ]
        
        # Patterns stricts : "Où :", "Adresse :", "Lieu :" 
        strict_patterns = [
            r"Où\s*(?::|=)\s*([^\n=]+?)(?:\n|$|=)",
            r"O=C3=B9\s*(?::|=)\s*([^\n=]+?)(?:\n|$|=)",
            r"(?:adresse|Adresse|ADRESSE):\s*([^\n]+?)(?:\n|-{2,}|$)",
            r"(?:lieu|Lieu|LIEU|location):\s*([^\n]+?)(?:\n|-{2,}|$)",
        ]
        
        # Patterns génériques : "à:", "au/aux"  (moins fiables)
        generic_patterns = [
            r"(?:à|À):\s*([^\n]+?)(?:\n|,|-{2,}|$)",
            r"(?:Aux|au|Au|Au)\s+(?!hommes|femmes|enfants|personnes|gens)([A-Z][^\n-]*?)(?:\s+-\s+(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)|(?:\d{1,2}\s+(?:janv|févr|mars|avril|mai|juin|juil|août|sept|oct|nov|déc))|$|\n)"
        ]
        
        # Mots à ignorer comme locations (jours, mois, mots génériques)
        rejected_words = [
            "dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi",
            "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", 
            "septembre", "octobre", "novembre", "décembre", "format", "non spécifié",
            "voir ci-après", "voir ci dessous"
        ]
        
        addresses_found = []  # Adresses valides (avec code postal ou numéro)
        generic_candidates = []  # Candidats des patterns génériques
        
        # ÉTAPE 1 : Cherche d'abord les patterns stricts
        for pattern in strict_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.UNICODE):
                location = match.group(1).strip()
                # Nettoie les encodages de emails
                location = location.replace("=C3=A9", "é").replace("=C3=A8", "è").replace("=C3=AA", "ê")
                location = location.replace("=C3=B9", "ù").replace("=C3=A0", "à").replace("=2E", ".")
                location = location.replace("=3D", "").strip()
                
                # Nettoie les caractères de contrôle
                location = re.sub(r'[\r\n]+', ' ', location)
                location = re.sub(r'\s+', ' ', location)
                location = location.strip()
                
                # Si le lieu contient un tiret séparateur date => prend avant
                if " - " in location:
                    parts = location.split(" - ")
                    if len(parts) > 1 and re.match(r'^(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|\d{1,2})', parts[1], re.IGNORECASE):
                        location = parts[0].strip()
                
                # Ignore les résultats avec HTML markers
                if "<" in location or "HTML" in location or "html" in location:
                    continue
                
                # Ignore les mots rejetés
                if location.lower() in rejected_words:
                    continue
                
                if location:
                    # Vérifie si c'est une adresse valide
                    if re.search(r'\d{5}', location) or re.search(r'^\d+\s+(?:rue|avenue|boulevard|chemin|place|square|allée)', location, re.IGNORECASE):
                        return location  # Retourne immédiatement si adresse valide trouvée
                    # Sinon ajoute aux candidats
                    addresses_found.append(location)
        
        # Si adresses trouvées par patterns stricts => retourne la première
        if addresses_found:
            return addresses_found[0]
        
        # ÉTAPE 2 : Cherche communes de Dordogne dans le texte (plus fiable que patterns génériques)
        for commune in communes_dordogne:
            if re.search(r'\b' + re.escape(commune) + r'\b', text, re.IGNORECASE):
                return commune
        
        # ÉTAPE 3 : Seulement si aucune commune trouvée, essaie les patterns génériques
        for pattern in generic_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.UNICODE):
                location = match.group(1).strip()
                location = location.replace("=C3=A9", "é").replace("=C3=A8", "è").replace("=C3=AA", "ê")
                location = location.replace("=C3=B9", "ù").replace("=C3=A0", "à").replace("=2E", ".")
                location = location.replace("=3D", "").strip()
                location = re.sub(r'[\r\n]+', ' ', location)
                location = re.sub(r'\s+', ' ', location)
                location = location.strip()
                
                if " - " in location:
                    parts = location.split(" - ")
                    if len(parts) > 1 and re.match(r'^(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|\d{1,2})', parts[1], re.IGNORECASE):
                        location = parts[0].strip()
                
                if "<" in location or "HTML" in location:
                    continue
                
                if location.lower() in rejected_words:
                    continue
                
                if location and len(location) < 150:  # Evite les descriptions longues
                    generic_candidates.append(location)
        
        # Retourne le meilleur candidat générique
        if generic_candidates:
            return generic_candidates[0]
        
        return "Non spécifié"
    
    def _extract_description(self, text: str) -> str:
        """Extrait la description/descriptif de l'événement"""
        # Cherche la section "Descriptif" ou "Description"
        lines = text.split('\n')
        description_lines = []
        empty_line_count = 0
        
        for i, line in enumerate(lines):
            # Cherche le début du descriptif
            if re.search(r'Descriptif|Description', line, re.IGNORECASE):
                # Vérifie que c'est bien une en-tête (suivi de tirets)
                if i+1 < len(lines) and re.match(r'^-+$', lines[i+1].strip()):
                    # Commence à partir de la ligne après les tirets (i+2)
                    start_idx = i + 2
                    # Saute les lignes vides initiales
                    while start_idx < len(lines) and not lines[start_idx].strip():
                        start_idx += 1
                    
                    # Collecte les lignes de descriptif
                    for j in range(start_idx, len(lines)):
                        curr_line = lines[j].strip()
                        
                        # Arrête si on trouve une séparation majeure
                        if re.match(r'^-{6,}$', curr_line):
                            # Mais vérifie qu'on a du contenu avant
                            if description_lines:
                                break
                        if re.match(r'^=+$', curr_line):
                            break
                        if curr_line.startswith('Message-ID') or curr_line.startswith('Date:'):
                            break
                        
                        # Arrête si on trouve la phrase type de fin de mailing list
                        if 'Ne répondez pas directement à la liste' in curr_line:
                            break
                        
                        # Arrête si on trouve une autre en-tête (tous les caps suivis de tirets)
                        if j+1 < len(lines) and re.match(r'^-+$', lines[j+1].strip()):
                            if curr_line.isupper() and len(curr_line) > 3 and description_lines:
                                break
                        
                        # Gère les lignes vides
                        if curr_line:
                            empty_line_count = 0  # Reset
                            description_lines.append(curr_line)
                        else:
                            # Compte les lignes vides consécutives
                            empty_line_count += 1
                            # Arrête après 2 lignes vides consécutives
                            if empty_line_count >= 2 and description_lines:
                                break
                            # Sinon ajoute une ligne vide pour préserver le formatage
                            if description_lines and empty_line_count == 1:
                                description_lines.append("")  # Marque une rupture
                    
                    break  # On a trouvé et traité le premier descriptif
        
        if description_lines:
            # Nettoie les listes en supprimant les vides excédentaires
            while description_lines and not description_lines[-1]:
                description_lines.pop()
            
            description = ' '.join(description_lines)
            description = description.replace('   ', ' ').replace('  ', ' ')  # Nettoie les espaces multiples
            
            # Supprime les références administratives gco.ouvaton.org (sauf /wp-content/)
            # Supprime la phrase "📅 Cet événement a été ajouté à l'agenda des sorties des crieurs : [URL]"
            description = re.sub(r'\s*📅[^:]*:\s*https://gco\.ouvaton\.org/[^/\s]+/[^/\s]+/\s*', ' ', description)
            description = re.sub(r'\s*Cet événement a été ajouté à l\'agenda[^:]*:\s*https://gco\.ouvaton\.org/[^/\s]+/[^/\s]+/\s*', ' ', description, flags=re.IGNORECASE)
            # Nettoie les références "Une pièce jointe est disponible" qui sont déjà dans les liens
            description = re.sub(r'\s*-->\s*', ' ', description)
            
            # Nettoie les encodages QUOTED-PRINTABLE
            # 1. Décode les caractères spéciaux
            description = description.replace("=C3=A9", "é").replace("=C3=A8", "è")
            description = description.replace("=C3=AA", "ê").replace("=C3=A7", "ç")
            description = description.replace("=E2=80=99", "'").replace("=C3=A0", "à")
            description = description.replace("=C3=B9", "ù").replace("=C3=A1", "á")
            description = description.replace("=C3=A4", "ä").replace("=C3=B1", "ñ")
            description = description.replace("=C3=B6", "ö").replace("=C3=BC", "ü")
            
            # 2. Enlève les = qui suivent un espace (soft line break)
            description = re.sub(r'\s=\s', ' ', description)
            description = re.sub(r'=\n', '', description)  # Supprime les retours à la ligne encodés
            
            # 3. Restaure la casse pour les en-têtes MIME (=?UTF-8?Q?...)
            description = re.sub(r'=\?UTF-8\?Q\?(.+?)\?=', lambda m: m.group(1).replace('_', ' '), description)
            
            # 4. Nettoie les = finaux et autres artifacts
            description = description.replace("=3D", "=")  # =3D est le code pour =
            description = re.sub(r'=(?=[^0-9A-F]|$)', '', description)  # Enlève les = solitaires
            description = re.sub(r'\s+', ' ', description)  # Élimine les espaces multiples
            
            # Limite à 800 caractères au lieu de 600
            if len(description) > 800:
                description = description[:800].rsplit(' ', 1)[0] + '...'
            
            return description.strip()
        
        return ""
    
    def _find_event_context(self, body_text: str, title: str) -> str:
        """
        Cherche le titre exact dans le corps et retourne le contexte complet de l'événement
        (les lignes qui le suivent jusqu'au prochain Message-ID ou événement)
        """
        if not title or len(title.strip()) < 3:
            return ""
        
        lines = body_text.split('\n')
        title_clean = title.strip().rstrip('-').strip()
        
        # Cherche le titre exact dans le texte - cherche l'occurrence APRÈS le sommaire
        # (pour éviter de capturer la première ligne du sommaire)
        found_sommaire_end = False
        for i, line in enumerate(lines):
            # Détecte la fin du sommaire (ligne avec "------" ou "Message-ID:")
            if line.startswith("------") or "Message-ID:" in line:
                found_sommaire_end = True
            
            # Cherche le titre APRÈS la fin du sommaire
            if found_sommaire_end and title_clean.lower() in line.lower():
                # Collecte le contexte : cette ligne + les suivantes jusqu'à "Message-ID:" ou "---" ou "* N -"
                context_lines = [line]
                j = i + 1
                while j < len(lines) and len(context_lines) < 50:  # Limite à 50 lignes
                    next_line = lines[j]
                    # Arrête au Message-ID, aux tirets, ou au prochain événement du sommaire
                    if ("Message-ID:" in next_line or 
                        next_line.startswith("------") or
                        re.match(r'\*\s*\d+\s*-\s*\[', next_line.strip())):
                        break
                    context_lines.append(next_line)
                    j += 1
                
                return '\n'.join(context_lines)
        
        return ""
    
    def _extract_description_from_digest(self, body_text: str, title: str) -> str:
        """
        Extrait la description d'un événement à partir d'une compilation email
        En cherchant le titre dans les Subject des Message-ID et récupérant le Descriptif qui suit
        """
        if not title or len(title.strip()) < 3:
            return ""
        
        lines = body_text.split('\n')
        title_clean = title.strip().rstrip('-').strip()
        
        # Stratégie 1: Cherche le titre dans un Subject: (le plus fiable)
        for i, line in enumerate(lines):
            if "Subject:" in line and title_clean.lower() in line.lower():
                # Trouve la section Descriptif qui suit ce Subject
                for j in range(i, min(i+80, len(lines))):
                    if re.search(r'^Descriptif|^Description', lines[j], re.IGNORECASE):
                        # Vérifie que c'est un en-tête (suivi de tirets ou =)
                        if j+1 < len(lines) and (re.match(r'^-+$', lines[j+1].strip()) or re.match(r'^=+$', lines[j+1].strip())):
                            result = self._extract_description_block(lines, j+2)
                            if result:
                                return result
        
        # Stratégie 2: Cherche dans une en-tête de section (ex: "[KAAG] - [Chalais]")
        for i, line in enumerate(lines):
            if line.startswith("[") and title_clean.lower() in line.lower():
                # Cherche le Descriptif dans les 80 lignes suivantes
                for j in range(i, min(i+80, len(lines))):
                    if re.search(r'^Descriptif|^Description', lines[j], re.IGNORECASE):
                        if j+1 < len(lines) and (re.match(r'^-+$', lines[j+1].strip()) or re.match(r'^=+$', lines[j+1].strip())):
                            result = self._extract_description_block(lines, j+2)
                            if result:
                                return result
        
        # Stratégie 3: Cherche le titre suivi d'une ligne de "=" (ex: "groupe de paroles...")
        # et ensuite cherche le Descriptif
        for i, line in enumerate(lines):
            if title_clean.lower() == line.strip().lower():
                # Vérifie que la ligne suivante est une ligne de tirets ou "="
                if i+1 < len(lines) and (re.match(r'^-+$', lines[i+1].strip()) or re.match(r'^=+$', lines[i+1].strip())):
                    # Cherche le Descriptif après ce titre
                    for j in range(i+2, min(i+100, len(lines))):
                        if re.search(r'^Descriptif|^Description', lines[j], re.IGNORECASE):
                            if j+1 < len(lines) and (re.match(r'^-+$', lines[j+1].strip()) or re.match(r'^=+$', lines[j+1].strip())):
                                result = self._extract_description_block(lines, j+2)
                                if result:
                                    return result
        
        # Retourne vide plutôt que une description incorrecte
        return ""
    
    def _extract_description_block(self, lines: list, start_idx: int) -> str:
        """Extrait un bloc de description à partir d'un index"""
        description_lines = []
        empty_line_count = 0
        
        # Saute les lignes vides initiales
        while start_idx < len(lines) and not lines[start_idx].strip():
            start_idx += 1
        
        # Collecte les lignes
        for i in range(start_idx, len(lines)):
            curr_line = lines[i].strip()
            
            # Arrête sur les séparateurs majeurs
            if re.match(r'^-{6,}$', curr_line):
                if description_lines:
                    break
            if re.match(r'^=+$', curr_line):
                break
            if re.match(r'Message-ID:', curr_line):
                break
            # Arrête sur en-têtes en majuscules (fin du descriptif)
            if curr_line.isupper() and len(curr_line) > 3 and description_lines:
                break
            
            if curr_line:
                empty_line_count = 0
                description_lines.append(curr_line)
            else:
                empty_line_count += 1
                if empty_line_count >= 2 and description_lines:
                    break
                if description_lines and empty_line_count == 1:
                    description_lines.append("")
        
        if description_lines:
            while description_lines and not description_lines[-1]:
                description_lines.pop()
            
            description = ' '.join(description_lines)
            description = description.replace('   ', ' ').replace('  ', ' ')
            
            # Nettoie les références administratives
            description = re.sub(r'\s*📅[^:]*:\s*https://gco\.ouvaton\.org/[^/\s]+/[^/\s]+/\s*', ' ', description)
            description = re.sub(r'\s*Cet événement a été ajouté[^.]*\.\s*', ' ', description, flags=re.IGNORECASE)
            
            # Nettoie les encodages QUOTED-PRINTABLE
            description = description.replace("=C3=A9", "é").replace("=C3=A8", "è")
            description = description.replace("=C3=AA", "ê").replace("=C3=A7", "ç")
            description = description.replace("=E2=80=99", "'").replace("=C3=A0", "à")
            description = description.replace("=C3=B9", "ù").replace("=C3=A1", "á")
            description = description.replace("=C3=A4", "ä").replace("=C3=B1", "ñ")
            description = description.replace("=C3=B6", "ö").replace("=C3=BC", "ü")
            description = re.sub(r'\s=\s', ' ', description)
            description = re.sub(r'=\n', '', description)
            description = description.replace("=3D", "=")
            description = re.sub(r'=(?=[^0-9A-F]|$)', '', description)
            description = re.sub(r'\s+', ' ', description)
            
            # Limite à 800 caractères
            if len(description) > 800:
                description = description[:800].rsplit(' ', 1)[0] + '...'
            
            return description.strip()
        
        return ""

    
    def close(self):
        """Ferme la connexion si nécessaire"""
        pass


class HTMLGenerator:
    """Classe pour générer une page HTML des événements"""
    
    def __init__(self, title: str = "Annonces d'événements"):
        self.title = title
        self.events = []
        self.source_type = "Sorties"  # "Sorties" ou "Expression Libre"
    
    def add_events(self, events: List[Dict]):
        """Ajoute des événements à afficher"""
        self.events = events
    
    def generate(self, output_file: str = "annonces.html"):
        """Génère la page HTML"""
        from datetime import datetime
        
        # Détermine les liens du menu selon le type
        if self.source_type == "Expression Libre":
            menu_annonces = "annonces.html"
            menu_map = "carte_expression_libre.html"
            header_title = "📢 Expression Libre Crieur"
            map_text = "🗺️ Carte des contributions"
        else:
            menu_annonces = "annonces.html"
            menu_map = "carte_des_annonces.html"
            header_title = "📅 Annonces Crieur"
            map_text = "🗺️ Carte des sorties"
        
        # Menu de navigation entre sorties et expression libre
        navigation_menu = """    <div class="top-navigation">
        <a href="annonces.html" class="nav-link active-if-sorties">📋 Sorties</a>
        <a href="expression_libre.html" class="nav-link active-if-libre">📢 Expression Libre</a>
    </div>
"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crieur des sorties</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Ysabeau+Office:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../public/style.css">
    <script>
        // Initialise le menu de navigation au chargement
        window.currentPage = '{"libre" if self.source_type == "Expression Libre" else "sorties"}';
    </script>
</head>
<body>
    {navigation_menu}
    
    <button class="burger-menu" aria-label="Menu">
        <span></span>
        <span></span>
        <span></span>
    </button>
    
    <div class="mobile-menu">
        <a href="annonces.html">📋 Sorties</a>
        <a href="expression_libre.html">📢 Expression Libre</a>
        <div style="border-top: 1px solid #ccc; margin: 10px 0;"></div>
        <a href="{menu_map}">{map_text}</a>
    </div>
    
    <div class="container">
        <header>
            <h1>{header_title}</h1>
            <a href="{menu_map}" class="map-link">{map_text}</a>
            <p>Générée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </header>

        
        <div class="events-grid">
"""
        
        if not self.events:
            html_content += """            <div class="empty-state">
                <p>Aucun événement trouvé</p>
            </div>
"""
        else:
            # Groupe les événements par date de réception
            from collections import defaultdict
            from datetime import datetime
            
            events_by_date = defaultdict(list)
            date_sort_keys = {}  # Pour stocker la clé de tri numérique
            
            for event in self.events:
                date_received = event.get('email_date', 'Non spécifiée')
                events_by_date[date_received].append(event)
                
                # Crée une clé de tri numérique (YYYYMMDDHHMMSS) pour un tri correct
                if date_received != 'Non spécifiée' and date_received not in date_sort_keys:
                    try:
                        # Parse le format "10 décembre 2025 à 14:40"
                        date_str = date_received.split(' à ')[0] if ' à ' in date_received else date_received
                        time_str = date_received.split(' à ')[1] if ' à ' in date_received else '00:00'
                        
                        # Converti les mois français en numéros
                        mois_fr = {
                            "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
                            "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12
                        }
                        
                        parts = date_str.split()
                        jour = int(parts[0])
                        mois = mois_fr.get(parts[1], 1)
                        annee = int(parts[2])
                        heures, minutes = map(int, time_str.split(':'))
                        
                        # Crée une clé de tri: YYYYMMDDHHMMSS (plus grand = plus récent)
                        sort_key = f"{annee:04d}{mois:02d}{jour:02d}{heures:02d}{minutes:02d}00"
                        date_sort_keys[date_received] = sort_key
                    except:
                        date_sort_keys[date_received] = "00000000000000"
            
            # Trie les dates en ordre décroissant (plus récentes en premier)
            sorted_dates = sorted(events_by_date.keys(), key=lambda x: date_sort_keys.get(x, "00000000000000"), reverse=True)
            
            for date in sorted_dates:
                # Formate la date sans l'heure
                date_display = date.split(' à ')[0] if ' à ' in date else date
                html_content += f'        <div class="date-section">\n'
                html_content += f'            <div class="date-section-title">📅 {date_display}</div>\n'
                html_content += f'            <div class="events-grid-section">\n'
                
                for event in events_by_date[date]:
                    html_content += self._generate_event_card(event)
                
                html_content += f'            </div>\n'
                html_content += f'        </div>\n'
        
        html_content += """        </div>
        
        <footer>
            <p>Total: """ + str(len(self.events)) + """ événement(s)</p>
        </footer>
    </div>
    
    <script src="../public/script.js"></script>
</body>
</html>
"""
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"✓ Page HTML générée: {output_file}")
        return output_file
    
    def _generate_event_card(self, event: Dict) -> str:
        """Génère la carte HTML d'un événement"""
        # Génère les liens HTML s'il y en a
        links_html = ""
        if event.get('links'):
            links_html = '<div class="event-info">\n'
            links_html += '                    <span class="event-info-icon">🔗</span>\n'
            links_html += '                    <div class="event-info-content">\n'
            links_html += '                        <div class="event-info-label">Liens</div>\n'
            for link in event['links']:
                # Pour les liens wp-content, affiche "pièce jointe"
                if '/wp-content/' in link:
                    link_text = '📎 Pièce jointe'
                # Pour les liens agenda, affiche "agenda"
                elif 'agenda-des-crieurs' in link:
                    link_text = 'agenda'
                else:
                    # Pour les autres liens, extrait le domaine pour l'affichage
                    link_text = link.replace('https://', '').replace('http://', '').split('/')[0]
                links_html += f'                        <div class="event-info-value"><a href="{link}" target="_blank" rel="noopener noreferrer">{link_text}</a></div>\n'
            links_html += '                    </div>\n'
            links_html += '                </div>\n'
        
        # Génère le tooltip de description s'il y a du contenu
        description = event.get('description', '').replace('\n', '<br>')
        tooltip_html = ""
        if description:
            tooltip_html = f'<div class="event-description-tooltip">{description}</div>'
        
        # Génère le HTML pour le téléphone s'il y a
        phone_html = ""
        if event.get('telephone'):
            phone = event['telephone']
            phone_html = f'<div class="event-info"><span class="event-info-icon">📞</span><div class="event-info-content"><div class="event-info-label">Téléphone</div><div class="event-info-value"><a href="tel:{phone}">{phone}</a></div></div></div>'
        
        # Génère le HTML pour WhatsApp s'il y a
        whatsapp_html = ""
        if event.get('whatsapp'):
            whatsapp = event['whatsapp']
            whatsapp_html = f'<div class="event-info"><span class="event-info-icon">💬</span><div class="event-info-content"><div class="event-info-label">WhatsApp</div><div class="event-info-value"><a href="{whatsapp}" target="_blank" rel="noopener noreferrer">Groupe WhatsApp</a></div></div></div>'
        
        # Génère le HTML pour mail contact s'il y a
        mailcontact_html = ""
        if event.get('mailcontact'):
            mailcontact = event['mailcontact']
            mailcontact_html = f'<div class="event-info"><span class="event-info-icon">✉️</span><div class="event-info-content"><div class="event-info-label">Mail contact</div><div class="event-info-value"><a href="mailto:{mailcontact}" style="color: #667eea; text-decoration: none;">{mailcontact}</a></div></div></div>'
        
        # Génère le HTML pour l'email de l'organisateur
        organizer_email_html = ""
        if event.get('organizer_email'):
            organizer_email = event['organizer_email']
            organizer_email_html = f'<div class="event-info"><span class="event-info-icon">📧</span><div class="event-info-content"><div class="event-info-label">Organisateur</div><div class="event-info-value"><a href="mailto:{organizer_email}" style="color: #667eea; text-decoration: none;">{organizer_email}</a></div></div></div>'
        
        # Formate la date de réception (sans heure, format: "10 décembre 2025")
        email_date_formatted = event.get('email_date', '')
        if ' à ' in email_date_formatted:
            email_date_formatted = email_date_formatted.split(' à ')[0]
        
        return f"""            <div class="event-card">
                <h3>{event['subject']}</h3>
                {tooltip_html}
                
                <div class="event-info">
                    <span class="event-info-icon">📅</span>
                    <div class="event-info-content">
                        <div class="event-info-label">Date de l'événement</div>
                        <div class="event-info-value">{event['date']}</div>
                    </div>
                </div>
                
                <div class="event-info">
                    <span class="event-info-icon">📍</span>
                    <div class="event-info-content">
                        <div class="event-info-label">Lieu</div>
                        <div class="event-info-value">{event['location']}</div>
                    </div>
                </div>
                
                {links_html}
                
                {phone_html}
                
                {whatsapp_html}
                
                {mailcontact_html}
                
                {organizer_email_html}
            </div>
"""
    
    def generate_map_html(self, output_file: str = "carte_des_annonces.html") -> str:
        """
        Génère une page HTML avec une carte interactive Leaflet.js
        Affiche les annonces avec des marqueurs positionnés géographiquement
        """
        # Import ici pour éviter la dépendance si pas utilisé
        from geocoding import add_coordinates_to_events
        
        # Ajoute les coordonnées aux événements
        events_with_coords = add_coordinates_to_events(self.events)
        
        # Filtre les événements avec coordonnées valides
        events_on_map = [e for e in events_with_coords if e.get('latitude') and e.get('longitude')]
        
        # Calcule le centre de la carte (moyenne des coordonnées)
        if events_on_map:
            avg_lat = sum(e['latitude'] for e in events_on_map) / len(events_on_map)
            avg_lon = sum(e['longitude'] for e in events_on_map) / len(events_on_map)
        else:
            # Périgord-Limousin par défaut
            avg_lat, avg_lon = 45.2, 1.0
        
        # Génère les marqueurs
        markers_json = self._generate_markers_json(events_on_map)
        
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carte Crieur des sorties</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Ysabeau+Office:wght@400;600;700&display=swap" rel="stylesheet">
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.0/MarkerCluster.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.0/MarkerCluster.Default.min.css">
    
    <link rel="stylesheet" href="../public/style.css">
</head>
<body class="map-page">
    <button class="burger-menu" aria-label="Menu">
        <span></span>
        <span></span>
        <span></span>
    </button>
    
    <div class="mobile-menu">
        <a href="annonces.html">📋 Annonces</a>
        <a href="carte_des_annonces.html">🗺️ Carte des sorties</a>
    </div>
    
    <div class="map-header">
        <h1>🗺️ Carte Crieur des sorties</h1>
        <p>Crieurs Périgord-Limousin - {len(events_on_map)} annonce(s) localisée(s) sur {len(self.events)} annonce(s) au total</p>
        <a href="annonces.html" class="map-header-link">📋 Voir les annonces</a>
    </div>
    
    <div class="map-container">
        <div id="map"></div>
        
        <div class="sidebar">
            <div class="sidebar-title">📍 Annonces ({len(events_on_map)})</div>
"""
        
        if events_on_map:
            for event in events_on_map:
                html_content += f"""            <div class="event-list-item" onclick="focusEvent({event['latitude']}, {event['longitude']})">
                <div class="event-list-item-title">{event['subject']}</div>
                <div class="event-list-item-meta">
                    <div class="event-list-item-meta-item">📍 {event['location']}</div>
                    <div class="event-list-item-meta-item">📅 {event['date']}</div>
                </div>
            </div>
"""
        else:
            html_content += """            <div class="no-locations">
                <p>Aucune annonce n'a pu être géolocalisée.</p>
                <p style="font-size: 0.85em; margin-top: 10px;">Les lieux doivent être spécifiés dans les emails.</p>
            </div>
"""
        
        html_content += f"""        </div>
    </div>
    
    <div class="map-footer">
        <p>Carte basée sur OpenStreetMap • Localisation via Nominatim</p>
    </div>
    
    <!-- Leaflet JavaScript -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.0/leaflet.markercluster.min.js"></script>
    
    <script>
        // Données des marqueurs
        window.markersData = {markers_json};
        
        // Initialise la carte au chargement
        document.addEventListener('DOMContentLoaded', function() {{
            initializeMap({avg_lat}, {avg_lon});
        }});
    </script>
    
    <script src="../public/script_carte.js"></script>
</body>
</html>
"""
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"✓ Carte générée: {output_file} ({len(events_on_map)} événement(s) localisé(s))")
        return output_file
    
    def _generate_markers_json(self, events: list) -> str:
        """Génère la liste des marqueurs en format JSON"""
        markers = []
        for event in events:
            # Formate la description (max 200 caractères)
            description = event.get('description', '')
            if description:
                description = description.replace('\n', ' ')[:200]
                if len(event.get('description', '')) > 200:
                    description += '...'
            
            marker = {
                'lat': event['latitude'],
                'lng': event['longitude'],
                'title': event['subject'],
                'location': event['location'],
                'date': event['date'],
                'description': description,
                'links': event.get('links', []) or []  # Garantit toujours un tableau
            }
            markers.append(marker)
        
        # Sérialise en JSON avec gestion spéciale des quotes
        import json
        return json.dumps(markers, ensure_ascii=False)
