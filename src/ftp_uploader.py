"""
Module pour l'upload FTP des fichiers HTML vers un serveur distant
Supporte FTP et FTPS (FTP sécurisé)
"""

import os
import ftplib
from typing import Tuple


class FTPUploader:
    """Classe pour gérer l'upload FTP"""
    
    def __init__(self, host: str, port: int = 21, username: str = "", password: str = "", 
                 use_tls: bool = False):
        """
        Initialise la connexion FTP
        
        Args:
            host: Serveur FTP
            port: Port FTP (21 par défaut, 990 pour FTPS)
            username: Nom d'utilisateur
            password: Mot de passe
            use_tls: Utiliser FTPS (FTP sécurisé)
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.ftp = None
        self.connected = False
    
    def connect(self) -> Tuple[bool, str]:
        """
        Établit la connexion FTP/FTPS
        
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            if self.use_tls:
                # Connexion FTPS (FTP avec TLS/SSL)
                self.ftp = ftplib.FTP_TLS()
                self.ftp.connect(self.host, self.port, timeout=10)
                self.ftp.auth()
                self.ftp.prot_p()  # Mode de données chiffré
            else:
                # Connexion FTP standard
                self.ftp = ftplib.FTP()
                self.ftp.connect(self.host, self.port, timeout=10)
            
            # Login
            self.ftp.login(self.username, self.password)
            self.connected = True
            return True, f"✓ Connecté à {self.host}"
        
        except ftplib.all_errors as e:
            return False, f"✗ Erreur de connexion FTP: {str(e)}"
        except Exception as e:
            return False, f"✗ Erreur inattendue: {str(e)}"
    
    def upload_file(self, local_path: str, remote_path: str) -> Tuple[bool, str]:
        """
        Upload un fichier unique
        
        Args:
            local_path: Chemin local du fichier
            remote_path: Chemin distant (complet avec nom de fichier)
        
        Returns:
            Tuple (succès: bool, message: str)
        """
        if not self.connected:
            return False, "✗ Non connecté au serveur FTP"
        
        try:
            if not os.path.exists(local_path):
                return False, f"✗ Fichier non trouvé: {local_path}"
            
            # Upload le fichier
            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_path}', f)
            
            return True, f"✓ {os.path.basename(local_path)} uploadé"
        
        except ftplib.all_errors as e:
            return False, f"✗ Erreur FTP lors de l'upload: {str(e)}"
        except Exception as e:
            return False, f"✗ Erreur: {str(e)}"
    
    def upload_directory(self, local_dir: str, remote_dir: str) -> Tuple[int, int]:
        """
        Upload tous les fichiers d'un répertoire
        
        Args:
            local_dir: Répertoire local
            remote_dir: Répertoire distant
        
        Returns:
            Tuple (fichiers_uploadés: int, fichiers_échoués: int)
        """
        if not self.connected:
            print("✗ Non connecté au serveur FTP")
            return 0, 0
        
        uploaded = 0
        failed = 0
        
        if not os.path.isdir(local_dir):
            print(f"✗ Répertoire non trouvé: {local_dir}")
            return 0, 0
        
        # Fichiers à exclure de l'upload
        excluded_files = {'.gitkeep', '.DS_Store', 'Thumbs.db', '.git'}
        
        try:
            # Crée le répertoire distant s'il n'existe pas
            try:
                self.ftp.mkd(remote_dir)
            except ftplib.error_perm:
                pass  # Répertoire existe déjà
            
            # Change vers le répertoire distant
            self.ftp.cwd(remote_dir)
            
            # Liste les fichiers locaux (en excluant certains fichiers techniques)
            files = [f for f in os.listdir(local_dir) 
                    if os.path.isfile(os.path.join(local_dir, f)) and f not in excluded_files]
            
            for filename in files:
                local_path = os.path.join(local_dir, filename)
                success, msg = self.upload_file(local_path, filename)
                
                if success:
                    print(f"  {msg}")
                    uploaded += 1
                else:
                    print(f"  {msg}")
                    failed += 1
        
        except ftplib.all_errors as e:
            print(f"✗ Erreur FTP: {str(e)}")
            return 0, len(files) if files else 0
        except Exception as e:
            print(f"✗ Erreur: {str(e)}")
            return 0, len(files) if files else 0
        
        return uploaded, failed
    
    def close(self):
        """Ferme la connexion FTP"""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                self.ftp.close()
            self.connected = False
    
    def __enter__(self):
        """Context manager: entrée"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: sortie"""
        self.close()
