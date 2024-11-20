#!/usr/bin/env python3
import csv
import subprocess
import sys
from urllib.parse import urlparse

# Chemin vers le fichier CSV contenant les sites
csv_file = 'liste_sites.csv'

# Vérifier si le fichier existe
try:
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Ignorer la première ligne (en-têtes)
        
        # Itérer sur chaque URL
        for row in reader:
            url = row[0].strip()  # Récupérer l'URL (en supposant que chaque ligne contient une URL)
            
            # Extraire le nom de domaine sans le schéma https:// ou http://
            parsed_url = urlparse(url)
            domain = parsed_url.netloc  # Cela récupère le domaine sans le schéma
            
            try:
                # Résoudre l'adresse IP du domaine
                result = subprocess.run(['nslookup', domain], capture_output=True, text=True)
                # Extraire l'IP à partir de la sortie
                ip = None
                for line in result.stdout.splitlines():
                    if "Address" in line:
                        ip = line.split()[-1]
                
                if ip:
                    # Générer la commande iptables pour bloquer l'IP
                    print(f"iptables -A FORWARD -d {ip} -j REJECT")
                else:
                    print(f"Impossible de résoudre l'IP pour {domain}")
            
            except subprocess.CalledProcessError:
                print(f"Erreur lors de la résolution DNS pour {domain}", file=sys.stderr)
except FileNotFoundError:
    print(f"Le fichier {csv_file} n'existe pas!", file=sys.stderr)
    sys.exit(1)
