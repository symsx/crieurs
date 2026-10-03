#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracteur d'adresses email avec informations complètes
Connecte à une boîte aux lettres via IMAP, scrute tous les répertoires et mails,
puis stocke les adresses avec nom, prénom, organisation et autres détails dans un fichier CSV
"""

import imaplib
import email
from email.message import Message
from email.header import decode_header
import os
import csv
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Set, List, Dict, Tuple
import time

# Charge les variables d'environnement
load_dotenv()


class EmailExtractor:
    """Classe pour extraire les informations email complètes d'une boîte aux lettres"""
    
    # Colonnes du CSV
    CSV_COLUMNS = ['Répertoire', 'Adresse Email', 'Nom Complet', 'Prénom', 'Nom', 'Organisation', 'Domaine', 'Type']
    
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
        self.email_records = {}  # Dictionnaire {email -> {détails}}
        self.email_count = 0
        self.folder_count = 0
        self.processed_count = 0
        
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
    
    def list_all_folders(self) -> List[str]:
        """
        Liste tous les dossiers de la boîte aux lettres
        
        Returns:
            Liste des noms de dossiers
        """
        try:
            status, mailboxes = self.connection.list()
            
            if status != "OK":
                print(f"✗ Erreur lors de la listage des dossiers")
                return []
            
            folders = []
            for mailbox in mailboxes:
                # Parse les informations du dossier
                # Format: (flags) "separator" "folder name"
                # Exemple: (\\HasNoChildren) "/" "INBOX"
                
                # Extrait le nom du dossier (entre guillemets finaux)
                try:
                    # Decode si nécessaire
                    if isinstance(mailbox, bytes):
                        mailbox = mailbox.decode('utf-8', errors='ignore')
                    
                    # Parse le format IMAP LIST
                    # Exemple: (\\All \\HasNoChildren) "/" "[Gmail]/All Mail"
                    match = re.search(r'"([^"]*)"$', mailbox)
                    if match:
                        folder_name = match.group(1)
                    else:
                        # Fallback: prend la dernière partie
                        parts = mailbox.split('"')
                        folder_name = parts[-2] if len(parts) > 1 else mailbox
                    
                    if folder_name:
                        folders.append(folder_name)
                except Exception as e:
                    print(f"  ! Erreur parsing dossier: {e}")
                    continue
            
            print(f"✓ {len(folders)} dossier(s) trouvé(s)")
            return folders
        
        except Exception as e:
            print(f"✗ Erreur lors du listage: {e}")
            return []
    
    def extract_emails_from_folder(self, folder: str, limit: int = None) -> int:
        """
        Extrait les adresses email et informations d'un dossier
        
        Args:
            folder: Nom du dossier
            limit: Nombre maximum d'emails à traiter (None = tous)
            
        Returns:
            Nombre d'emails traités
        """
        try:
            # Sélectionne le dossier
            status, messages = self.connection.select(folder)
            
            if status != "OK":
                print(f"  ! Erreur lors de la sélection du dossier: {folder}")
                return 0
            
            # Récupère l'ID de tous les emails
            status, message_ids = self.connection.search(None, "ALL")
            
            if status != "OK":
                print(f"  ! Erreur lors de la recherche dans {folder}")
                return 0
            
            email_ids = message_ids[0].split()
            
            # Limite le nombre d'emails si demandé
            if limit and len(email_ids) > limit:
                email_ids = email_ids[-limit:]  # Prend les derniers
            
            processed = 0
            total = len(email_ids)
            
            for idx, email_id in enumerate(email_ids):
                # Affiche la barre de progression
                self._show_progress(idx + 1, total)
                
                try:
                    status, msg_data = self.connection.fetch(email_id, "(RFC822)")
                    
                    if status != "OK":
                        continue
                    
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Extrait les informations des champs d'en-tête
                    self._extract_header_info(msg, folder)
                    self.email_count += 1
                    processed += 1
                    self.processed_count += 1
                    
                except Exception as e:
                    continue
            
            # Nouvelle ligne après la barre de progression
            print()
            
            if processed > 0:
                print(f"  ✓ {processed} email(s) traité(s) - {len(self.email_records)} adresse(s) unique(s)")
            
            return processed
        
        except Exception as e:
            print(f"  ✗ Erreur dans le dossier {folder}: {e}")
            return 0
    
    def _decode_header(self, header) -> str:
        """Décode les en-têtes email, y compris MIME-encoded"""
        if header is None:
            return ""
        
        # Si c'est déjà une chaîne de caractères
        if isinstance(header, str):
            header_str = header
        else:
            # Si c'est un objet Header, convertis-le en string
            try:
                header_str = str(header)
            except:
                return ""
        
        # Décode les parties MIME encodées
        decoded_parts = []
        try:
            for part, encoding in decode_header(header_str):
                if isinstance(part, bytes):
                    decoded_parts.append(part.decode(encoding or "utf-8", errors="ignore"))
                else:
                    decoded_parts.append(str(part) if part else "")
        except:
            # Fallback: retourne la représentation string
            return header_str
        
        result = "".join(decoded_parts)
        
        # Nettoie les underscores et autres encodages restants
        result = result.replace('_', ' ').strip()
        
        return result
    
    def _show_progress(self, current: int, total: int, width: int = 40):
        """Affiche une barre de progression"""
        percent = current / total
        filled = int(width * percent)
        bar = '█' * filled + '░' * (width - filled)
        print(f'\r  [{bar}] {current:5d}/{total:5d} ({percent*100:5.1f}%)', end='', flush=True)
    
    def _parse_email_address(self, email_str: str) -> Tuple[str, str, str]:
        """
        Analyse une adresse email pour en extraire les informations
        Formats: 'email@example.com' ou 'Name Surname <email@example.com>'
        
        Returns:
            Tuple (email, full_name, email_type)
        """
        if not email_str:
            return '', '', 'unknown'
        
        email_str = email_str.strip()
        
        # Essaie d'extraire l'adresse et le nom
        match = re.match(r'([^<]*)<([^>]+)>', email_str)
        if match:
            full_name = match.group(1).strip()
            email_addr = match.group(2).strip().lower()
        else:
            # Pas de chevrons, c'est juste l'adresse
            full_name = ''
            email_addr = email_str.lower()
        
        # Extrait le nom et prénom du nom complet
        first_name, last_name = self._extract_names(full_name)
        
        # Détermine le type d'adresse
        email_type = self._determine_email_type(email_addr)
        
        return email_addr, full_name, email_type
    
    def _extract_names(self, full_name: str) -> Tuple[str, str]:
        """Extrait le prénom et nom du nom complet"""
        if not full_name:
            return '', ''
        
        # Nettoie les guillemets et espaces
        full_name = full_name.strip('"\'')
        
        # Divise par l'espace
        parts = full_name.split()
        
        if len(parts) == 0:
            return '', ''
        elif len(parts) == 1:
            # Un seul mot: considère comme nom
            return '', parts[0]
        else:
            # Premier mot = prénom, reste = nom
            return parts[0], ' '.join(parts[1:])
    
    def _determine_email_type(self, email_addr: str) -> str:
        """Détermine le type d'adresse email"""
        if 'noreply' in email_addr.lower() or 'no-reply' in email_addr.lower():
            return 'noreply'
        elif 'notification' in email_addr.lower() or 'alert' in email_addr.lower():
            return 'notification'
        elif 'info' in email_addr.lower() or 'contact' in email_addr.lower():
            return 'information'
        else:
            return 'personnel'
    
    def _extract_domain_and_org(self, email_addr: str) -> Tuple[str, str]:
        """Extrait le domaine et essaie de déterminer l'organisation"""
        if '@' not in email_addr:
            return '', ''
        
        domain = email_addr.split('@')[1].lower()
        
        # Essaie d'extraire l'organisation du domaine
        # Ex: mail.google.com -> google
        org_match = re.search(r'(?:mail\.)?([a-z0-9-]+)\.(?:com|fr|org|net|be|ch|de|eu)', domain)
        org = org_match.group(1).capitalize() if org_match else domain
        
        return domain, org
    
    def _extract_header_info(self, msg: Message, folder: str = ''):
        """Extrait les informations des champs d'en-tête"""
        # Champs à vérifier pour les adresses email
        email_fields = [
            ('From', 'sender'),
            ('To', 'recipient'),
            ('Cc', 'copy'),
            ('Bcc', 'blind_copy'),
            ('Reply-To', 'reply'),
            ('Sender', 'technical'),
            ('Return-Path', 'return'),
        ]
        
        for field, field_type in email_fields:
            field_value = msg.get(field, "")
            if field_value:
                # Décode l'en-tête si nécessaire
                field_value = self._decode_header(field_value)
                
                # Peut contenir plusieurs adresses séparées par des virgules
                addresses = [addr.strip() for addr in field_value.split(',')]
                
                for addr in addresses:
                    if addr:
                        email_addr, full_name, email_type = self._parse_email_address(addr)
                        
                        if email_addr and '@' in email_addr:
                            domain, org = self._extract_domain_and_org(email_addr)
                            first_name, last_name = self._extract_names(full_name)
                            
                            # Ajoute ou met à jour l'enregistrement
                            if email_addr not in self.email_records:
                                self.email_records[email_addr] = {
                                    'folder': folder,
                                    'email': email_addr,
                                    'full_name': full_name,
                                    'first_name': first_name,
                                    'last_name': last_name,
                                    'organization': org,
                                    'domain': domain,
                                    'type': email_type
                                }
                            else:
                                # Met à jour avec les infos les plus complètes
                                record = self.email_records[email_addr]
                                if not record['full_name'] and full_name:
                                    record['full_name'] = full_name
                                    record['first_name'] = first_name
                                    record['last_name'] = last_name
                                if not record['organization'] and org:
                                    record['organization'] = org
    
    def extract_all_emails(self, email_limit_per_folder: int = None) -> int:
        """
        Extrait les adresses email de tous les dossiers
        
        Args:
            email_limit_per_folder: Limite d'emails par dossier (None = tous)
            
        Returns:
            Nombre total d'emails traités
        """
        folders = self.list_all_folders()
        
        if not folders:
            print("✗ Aucun dossier trouvé")
            return 0
        
        total_processed = 0
        
        for folder in folders:
            print(f"\n📂 Traitement du dossier: {folder}")
            self.folder_count += 1
            processed = self.extract_emails_from_folder(folder, email_limit_per_folder)
            total_processed += processed
        
        return total_processed
    
    def save_to_csv(self, output_file: str = "data/adresses_emails.csv") -> str:
        """
        Sauvegarde les adresses email avec informations détaillées dans un fichier CSV
        
        Args:
            output_file: Chemin du fichier CSV de sortie
            
        Returns:
            Chemin du fichier CSV créé
        """
        try:
            # Crée le répertoire s'il n'existe pas
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Charge les enregistrements existants si le fichier existe
            existing_records = {}
            if output_path.exists():
                try:
                    with open(output_file, 'r', encoding='utf-8', newline='') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row and row.get('Adresse Email'):
                                email_addr = row['Adresse Email'].lower()
                                existing_records[email_addr] = row
                    print(f"\n✓ {len(existing_records)} enregistrement(s) existant(s) chargé(s)")
                except Exception as e:
                    print(f"\n! Erreur lors de la lecture du fichier existant: {e}")
            
            # Fusionne les enregistrements existants et nouveaux
            all_records = existing_records.copy()
            new_count = 0
            
            for email_addr, record in self.email_records.items():
                if email_addr not in all_records:
                    all_records[email_addr] = {
                        'Répertoire': record['folder'],
                        'Adresse Email': record['email'],
                        'Nom Complet': record['full_name'],
                        'Prénom': record['first_name'],
                        'Nom': record['last_name'],
                        'Organisation': record['organization'],
                        'Domaine': record['domain'],
                        'Type': record['type']
                    }
                    new_count += 1
                else:
                    # Met à jour les informations manquantes
                    existing = all_records[email_addr]
                    # Ajoute le répertoire s'il est manquant
                    if not existing.get('Répertoire') and record.get('folder'):
                        existing['Répertoire'] = record['folder']
                    if not existing.get('Nom Complet') and record['full_name']:
                        existing['Nom Complet'] = record['full_name']
                        existing['Prénom'] = record['first_name']
                        existing['Nom'] = record['last_name']
                    if not existing.get('Organisation') and record['organization']:
                        existing['Organisation'] = record['organization']
            
            # Écrit dans le fichier CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.CSV_COLUMNS)
                writer.writeheader()
                
                # Trie les enregistrements par adresse email
                for email_addr in sorted(all_records.keys()):
                    writer.writerow(all_records[email_addr])
            
            print(f"✓ {len(all_records)} adresse(s) email(s) sauvegardée(s)")
            if new_count > 0:
                print(f"  → {new_count} nouvelle(s) adresse(s) ajoutée(s)")
            
            return output_file
        
        except Exception as e:
            print(f"✗ Erreur lors de la sauvegarde: {e}")
            return None
    
    def close(self):
        """Ferme la connexion IMAP"""
        if self.connection:
            try:
                self.connection.close()
                print("✓ Connexion fermée")
            except:
                pass
    
    def print_summary(self):
        """Affiche un résumé détaillé de l'extraction"""
        # Calcule les statistiques
        noreply_count = sum(1 for r in self.email_records.values() if r['type'] == 'noreply')
        notification_count = sum(1 for r in self.email_records.values() if r['type'] == 'notification')
        personnel_count = sum(1 for r in self.email_records.values() if r['type'] == 'personnel')
        with_name = sum(1 for r in self.email_records.values() if r['full_name'])
        
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE L'EXTRACTION")
        print("="*60)
        print(f"Dossiers traités:           {self.folder_count}")
        print(f"Emails traités:             {self.email_count:,}")
        print(f"Adresses email uniques:     {len(self.email_records)}")
        print("-"*60)
        print(f"  • Adresses avec nom:      {with_name} ({with_name*100//len(self.email_records) if self.email_records else 0}%)")
        print(f"  • Type noreply/système:   {noreply_count} ({noreply_count*100//len(self.email_records) if self.email_records else 0}%)")
        print(f"  • Type notification:      {notification_count}")
        print(f"  • Type personnel:         {personnel_count}")
        print("="*60)


def get_credentials():
    """
    Récupère les identifiants depuis .env ou demande à l'utilisateur
    
    Returns:
        Tuple (email_address, password, imap_server, imap_port)
    """
    email_address = os.getenv('EMAIL_ADDRESS', '').strip()
    password = os.getenv('EMAIL_PASSWORD', '').strip()
    imap_server = os.getenv('IMAP_SERVER', 'imap.free.fr').strip()
    imap_port = int(os.getenv('IMAP_PORT', '993'))
    prompt_for_creds = os.getenv('PROMPT_FOR_CREDENTIALS', 'false').lower() == 'true'
    
    # Si PROMPT_FOR_CREDENTIALS=true ou si les identifiants sont vides
    if prompt_for_creds or not email_address or not password:
        print("📧 Configuration Email")
        print("-" * 30)
        
        if not email_address:
            email_address = input("Adresse email: ").strip()
        
        if not password:
            import getpass
            password = getpass.getpass("Mot de passe: ")
        
        if not imap_server:
            imap_server = input(f"Serveur IMAP (défaut: imap.free.fr): ").strip() or "imap.free.fr"
        
        if not imap_port:
            port_input = input(f"Port IMAP (défaut: 993): ").strip()
            imap_port = int(port_input) if port_input else 993
    
    return email_address, password, imap_server, imap_port


def main():
    """Fonction principale"""
    print("🔍 EXTRACTEUR D'ADRESSES EMAIL")
    print("=" * 50)
    
    try:
        # Récupère les identifiants
        email_address, password, imap_server, imap_port = get_credentials()
        
        # Crée l'extracteur
        extractor = EmailExtractor(email_address, password, imap_server, imap_port)
        
        # Extrait les adresses de tous les dossiers
        print("\n🔎 Extraction des adresses email en cours...")
        extractor.extract_all_emails()
        
        # Affiche le résumé
        extractor.print_summary()
        
        # Sauvegarde dans un fichier CSV
        print("\n📁 Sauvegarde des adresses...")
        csv_file = extractor.save_to_csv("data/adresses_emails.csv")
        
        if csv_file:
            print(f"\n✓ Fichier créé: {csv_file}")
        
        # Ferme la connexion
        extractor.close()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
