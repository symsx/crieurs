#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script exemple pour utiliser le fichier CSV d'adresses email généré par extract_mail.py
Montre comment charger, filtrer et analyser les adresses
"""

import csv
import re
from pathlib import Path
from collections import Counter


def load_emails_from_csv(csv_file: str) -> list:
    """Charge les adresses email depuis le fichier CSV"""
    emails = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Saute l'en-tête
            for row in reader:
                if row and row[0].strip():
                    emails.append(row[0].strip())
    except FileNotFoundError:
        print(f"✗ Fichier non trouvé: {csv_file}")
        return []
    except Exception as e:
        print(f"✗ Erreur de lecture: {e}")
        return []
    
    return emails


def filter_by_domain(emails: list, domain: str) -> list:
    """Filtre les adresses par domaine"""
    return [e for e in emails if e.endswith(f"@{domain}") or f"@{domain}." in e]


def filter_noreply(emails: list) -> list:
    """Supprime les adresses noreply"""
    return [e for e in emails if 'noreply' not in e.lower() and 'no-reply' not in e.lower()]


def extract_domains(emails: list) -> dict:
    """Extrait les domaines et compte les adresses par domaine"""
    domains = Counter()
    for email in emails:
        if '@' in email:
            domain = email.split('@')[1]
            domains[domain] += 1
    return dict(domains)


def get_statistics(emails: list) -> dict:
    """Génère des statistiques sur les adresses"""
    domains = extract_domains(emails)
    
    return {
        'total': len(emails),
        'unique': len(set(emails)),
        'domains_count': len(domains),
        'top_domains': sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10],
        'noreply_count': len([e for e in emails if 'noreply' in e.lower() or 'no-reply' in e.lower()])
    }


def export_emails_by_domain(emails: list, output_dir: str = "data/emails_by_domain"):
    """Exporte les adresses groupées par domaine dans des fichiers séparés"""
    domains = extract_domains(emails)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for domain in domains:
        domain_emails = filter_by_domain(emails, domain)
        filename = f"{output_dir}/{domain}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for email in sorted(domain_emails):
                    f.write(email + '\n')
            print(f"✓ {len(domain_emails)} adresse(s) exportée(s) vers {filename}")
        except Exception as e:
            print(f"✗ Erreur lors de l'export {filename}: {e}")


def main():
    """Fonction principale"""
    print("📧 Analyseur d'adresses email")
    print("=" * 50)
    
    # Charge les emails
    csv_file = "data/adresses_emails.csv"
    print(f"\n📂 Chargement de {csv_file}...")
    emails = load_emails_from_csv(csv_file)
    
    if not emails:
        print("✗ Aucune adresse trouvée")
        return
    
    # Affiche les statistiques
    print("\n📊 Statistiques:")
    print("-" * 50)
    stats = get_statistics(emails)
    print(f"Total d'adresses: {stats['total']}")
    print(f"Adresses uniques: {stats['unique']}")
    print(f"Nombre de domaines: {stats['domains_count']}")
    print(f"Adresses noreply: {stats['noreply_count']}")
    
    # Affiche les domaines les plus fréquents
    print("\n🏆 Top 10 domaines:")
    print("-" * 50)
    for i, (domain, count) in enumerate(stats['top_domains'], 1):
        print(f"{i:2d}. {domain:40s} ({count:4d})")
    
    # Exemples de filtrage
    print("\n🔍 Exemples de filtrage:")
    print("-" * 50)
    
    # Filtre par domaine
    gmail_count = len(filter_by_domain(emails, 'gmail.com'))
    print(f"Adresses Gmail: {gmail_count}")
    
    # Filtre noreply
    valid_emails = filter_noreply(emails)
    print(f"Adresses valides (sans noreply): {len(valid_emails)}")
    
    # Export par domaine
    print("\n💾 Export par domaine:")
    print("-" * 50)
    export_emails_by_domain(emails)
    
    print("\n✓ Analyse terminée!")


if __name__ == "__main__":
    main()
