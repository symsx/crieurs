"""
Module de géocodage simplifié pour convertir des noms de lieux en coordonnées GPS
Utilise une base de données pré-construite des communes + fallback API Nominatim
"""

import json
import re
import time
import os
import requests
from typing import Optional, Tuple

class Geocoder:
    """Convertit des noms de lieux en coordonnées GPS"""
    
    def __init__(self, coordinates_file: str = None, corrections_file: str = None, lieux_cache_file: str = None):
        """
        Initialise le géocodeur avec base locale, corrections manuelles et cache de lieux
        
        Args:
            coordinates_file: Fichier JSON avec les coordonnées pré-construites
            corrections_file: Fichier JSON avec les corrections manuelles
            lieux_cache_file: Fichier JSON avec le cache des lieux d'annonces
        """
        # Déterminer les chemins des fichiers si non fournis
        if coordinates_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            coordinates_file = os.path.join(base_dir, "data", "communes_coordinates.json")
        
        if corrections_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            corrections_file = os.path.join(base_dir, "data", "corrections_geolocalisation.json")
        
        if lieux_cache_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            lieux_cache_file = os.path.join(base_dir, "data", "lieux_coordinates.json")
        
        self.coordinates_db = self._load_coordinates_db(coordinates_file)
        self.corrections = self._load_corrections(corrections_file)
        self.lieux_cache_file = lieux_cache_file
        self.lieux_cache = self._load_lieux_cache(lieux_cache_file)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'CrieursPeriord/1.0'})
    
    def _load_coordinates_db(self, coordinates_file: str) -> dict:
        """Charge la base de données de coordonnées locales"""
        try:
            with open(coordinates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _load_corrections(self, corrections_file: str) -> dict:
        """Charge les corrections manuelles de géolocalisation"""
        try:
            with open(corrections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('corrections', {}).get('corrections', {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _load_lieux_cache(self, lieux_cache_file: str) -> dict:
        """Charge le cache des lieux d'annonces avec leurs coordonnées"""
        try:
            with open(lieux_cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Exclure les clés spéciales (_comment, _example)
                return {k: v for k, v in data.items() if not k.startswith('_')}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_lieux_cache(self):
        """Sauvegarde le cache des lieux dans le fichier JSON"""
        try:
            # Charger d'abord pour préserver les commentaires
            try:
                with open(self.lieux_cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = {
                    "_comment": "Cache de géolocalisation des lieux d'annonces",
                    "_example": {"Nontron": {"lat": 45.5233, "lon": 0.7667, "source": "manual"}}
                }
            
            # Mettre à jour les lieux (sans overwrite les commentaires)
            for lieu, coords in self.lieux_cache.items():
                if not lieu.startswith('_'):
                    data[lieu] = coords
            
            # Écrire le fichier
            with open(self.lieux_cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠ Erreur lors de la sauvegarde du cache: {e}")
    
    def _add_to_cache(self, lieu: str, lat: float, lon: float, source: str = "api"):
        """Ajoute un lieu au cache"""
        from datetime import date
        self.lieux_cache[lieu] = {
            "lat": lat,
            "lon": lon,
            "source": source,
            "date_added": str(date.today())
        }
        self._save_lieux_cache()
    
    def _get_from_cache(self, lieu: str) -> Optional[Tuple[float, float]]:
        """Récupère un lieu du cache s'il existe"""
        if lieu in self.lieux_cache:
            coords = self.lieux_cache[lieu]
            return (coords['lat'], coords['lon'])
        return None
    
    def geocode(self, location: str) -> Optional[Tuple[float, float, str]]:
        """
        Convertit un nom de lieu en coordonnées GPS
        
        Args:
            location: Nom du lieu (ex: "Montbron" ou "Place des Droits de l'Homme 24300 Nontron")
        
        Returns:
            Tuple (latitude, longitude, adresse) ou None si pas trouvé
        """
        if not location or location.lower() == "non spécifié":
            return None
        
        location_clean = location.strip()
        
        # Normaliser les apostrophes courbes (U+2019) en apostrophes droites (U+0027)
        location_clean = location_clean.replace('\u2019', "'")  # Apostrophe courbe → droite
        location_clean = location_clean.replace('\u2018', "'")  # Guillemet gauche → apostrophe
        
        # 0. Vérifier le cache des lieux d'annonces EN PREMIER
        cached = self._get_from_cache(location_clean)
        if cached:
            lat, lon = cached
            print(f"✓ {location_clean} → ({lat}, {lon}) [cache local]")
            return (lat, lon, location_clean)
        
        # 1. Vérifier les corrections manuelles
        if location_clean in self.corrections:
            lat, lon, adresse = self.corrections[location_clean]
            print(f"✓ {location_clean} → ({lat}, {lon}) [correction manuelle]")
            return (lat, lon, adresse)
        
        # 1. Si l'adresse contient un code postal, utilise l'API directement (plus précis)
        if re.search(r'\d{5}', location_clean):
            print(f"⚠ Adresse détaillée trouvée, recherche API...")
            result = self._geocode_with_api(location_clean)
            if result:
                return result
        
        # 2. Pour les communes simples (sans code postal), utilise l'API Nominatim
        #    car elle donne le centre-ville plutôt que le centre géographique
        if len(location_clean.split()) <= 2 and not re.search(r'\d+', location_clean):
            # Pas de numéro dans l'adresse et max 2 mots = commune simple
            print(f"⚠ Commune simple trouvée, recherche API pour meilleure précision...")
            result = self._geocode_with_api(location_clean)
            if result:
                return result
        
        # 3. Essaie la correspondance dans la base locale (fallback)
        for commune, coords in self.coordinates_db.items():
            if commune.lower() in location_clean.lower() or location_clean.lower() in commune.lower():
                lat, lon = coords[0], coords[1]
                print(f"✓ {location_clean} → ({lat}, {lon}) [base locale]")
                return (lat, lon, commune)
        
        # 4. Extrait le nom de commune depuis une adresse complexe
        commune_name = self._extract_commune_name(location_clean)
        if commune_name and commune_name in self.coordinates_db:
            coords = self.coordinates_db[commune_name]
            lat, lon = coords[0], coords[1]
            print(f"✓ {location_clean} → ({lat}, {lon}) [extracté: {commune_name}]")
            return (lat, lon, commune_name)
        
        # 5. Fallback : recherche API Nominatim pour la commune extraite (lent, utilisé en dernier recours)
        if commune_name:
            print(f"⚠ {commune_name} non trouvé localement, recherche API...")
            return self._geocode_with_api(commune_name)
        
        print(f"✗ Impossible d'extraire une commune de: {location_clean}")
        return None
    
    def _extract_commune_name(self, location: str) -> Optional[str]:
        """
        Extrait le nom de commune d'une adresse complexe
        Par exemple: "923 Route du Moulin 24800 Chalais" → "Chalais"
                    "Place des Droits de l'Homme 24300 Nontron" → "Nontron"
        """
        # Cherche code postal (5 chiffres) suivi d'un mot
        postal_pattern = r'(\d{5})\s+([A-Za-zÀ-ÿ\s\-]+?)(?:\s|$)'
        match = re.search(postal_pattern, location)
        if match:
            postal_code = match.group(1)
            commune_part = match.group(2).strip()
            # Nettoie : prend le premier mot après code postal
            words = [w.strip() for w in commune_part.split() if w.strip()]
            if words:
                # Cherche la commune complète (peut être multi-mots comme "Saint-Yrieix")
                candidate = words[0]
                # Si le mot suivant commence par une majuscule, peut faire partie du nom
                if len(words) > 1 and words[1][0].isupper():
                    candidate = f"{words[0]}-{words[1]}"
                # Nettoie les caractères spéciaux
                candidate = re.sub(r'[,\.\-\(\)]', '', candidate)
                if len(candidate) > 2:
                    return candidate
        
        # Essaie de prendre le dernier mot significatif (commune)
        words = [w.strip() for w in location.split() if w.strip() and not w.isdigit()]
        if words:
            # Retourne le dernier mot (supposé être la commune)
            candidate = words[-1]
            # Nettoie les caractères spéciaux mais garde les tirets pour les noms composés
            candidate = re.sub(r'[,\.\(\)]', '', candidate)
            return candidate if len(candidate) > 2 else None
        
        return None
    
    def _geocode_with_api(self, location: str) -> Optional[Tuple[float, float, str]]:
        """
        Utilise l'API Nominatim d'OpenStreetMap (gratuit) pour géocoder
        Avec fallback progressif : adresse complète → commune seule
        Priorise les résultats dans la Dordogne (département 24)
        Ajoute les résultats au cache local
        """
        try:
            # Essai 1 : adresse complète en France
            print(f"  → Essai 1: Adresse complète '{location}'")
            params = {
                'q': f"{location}, Dordogne, France",
                'format': 'json',
                'limit': 5,  # Augmente le nombre de résultats pour filtrer
                'addressdetails': 1,
                'timeout': 10
            }
            
            response = self.session.get(
                'https://nominatim.openstreetmap.org/search',
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            results = response.json()
            if results:
                # Priorise les résultats en Dordogne
                result = self._best_result_in_dordogne(results, location)
                if result:
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    address = result.get('display_name', location)
                    postal_code = result.get('address', {}).get('postcode', '')
                    print(f"✓ {location} → ({lat}, {lon}) [API - adresse précise]")
                    # Ajoute au cache
                    self._add_to_cache(location, lat, lon, source="api")
                    return (lat, lon, address)
            
            # Essai 2 : essaie juste la commune en Dordogne
            commune_name = self._extract_commune_name(location)
            if commune_name and commune_name != location:
                print(f"  → Essai 2: Commune seule '{commune_name}' en Dordogne")
                params['q'] = f"{commune_name}, Dordogne, France"
                
                response = self.session.get(
                    'https://nominatim.openstreetmap.org/search',
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                
                results = response.json()
                if results:
                    result = self._best_result_in_dordogne(results, commune_name)
                    if result:
                        lat = float(result['lat'])
                        lon = float(result['lon'])
                        address = result.get('display_name', location)
                        print(f"✓ {location} → ({lat}, {lon}) [API - commune Dordogne]")
                        # Ajoute au cache
                        self._add_to_cache(location, lat, lon, source="api")
                        return (lat, lon, address)
            
            print(f"✗ {location} introuvable en Dordogne")
            return None
        
        except Exception as e:
            print(f"✗ Erreur géocodage {location}: {e}")
            return None
        finally:
            # Respecte rate limiting d'OpenStreetMap (1 req/sec)
            time.sleep(1)
    
    def _best_result_in_dordogne(self, results: list, search_term: str) -> Optional[dict]:
        """
        Priorise les résultats en Dordogne parmi les résultats Nominatim
        Retourne le meilleur résultat
        """
        # Priorise les résultats avec code postal 24xxx
        for result in results:
            postal_code = result.get('address', {}).get('postcode', '')
            if postal_code.startswith('24'):
                return result
        
        # Priorise les résultats en Dordogne
        for result in results:
            display_name = result.get('display_name', '').lower()
            if 'dordogne' in display_name:
                return result
        
        # Si rien trouvé en Dordogne, retourne le premier résultat
        return results[0] if results else None


def add_coordinates_to_events(events: list) -> list:
    """
    Ajoute les coordonnées GPS à chaque événement
    
    Args:
        events: Liste des événements extraits
    
    Returns:
        Liste des événements avec coordonnées
    """
    geocoder = Geocoder()
    
    for event in events:
        location = event.get('location', '')
        if location:
            coords = geocoder.geocode(location)
            if coords:
                event['latitude'], event['longitude'], event['full_address'] = coords
            else:
                event['latitude'] = None
                event['longitude'] = None
                event['full_address'] = location
        else:
            event['latitude'] = None
            event['longitude'] = None
            event['full_address'] = None
    
    # Filtre les événements sans coordonnées
    events_with_coords = [e for e in events if e.get('latitude') and e.get('longitude')]
    print(f"\n📍 {len(events_with_coords)}/{len(events)} événements géocodés")
    
    return events_with_coords
