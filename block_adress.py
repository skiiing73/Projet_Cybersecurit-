#!/usr/bin/env python3
import csv
import subprocess
import sys
import ipaddress
from urllib.parse import urlparse

# Chemin vers le fichier CSV contenant les sites
csv_file = 'liste_sites.csv'
# Chemin vers le fichier de règles iptables
firewall_rules_file = 'firewall/firewall_rules.sh'

try:
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Ignorer la première ligne (en-têtes)

        # Ouvrir le fichier de règles en mode écriture
        with open(firewall_rules_file, 'w') as rules_file:
            # Ajouter un shebang au début
            rules_file.write("#!/bin/bash\n\n")

            # Itérer sur chaque URL
            for row in reader:
                url = row[0].strip()  # Récupérer l'URL (en supposant que chaque ligne contient une URL)
                
                # Extraire le nom de domaine sans le schéma https:// ou http://
                parsed_url = urlparse(url)
                domain = parsed_url.netloc or parsed_url.path  # Handle cases without scheme
                
                try:
                    # Résoudre l'adresse IP du domaine
                    result = subprocess.run(['nslookup', domain], capture_output=True, text=True)
                    # Extraire l'IP à partir de la sortie
                    ip = None
                    for line in result.stdout.splitlines():
                        if "Address" in line and not line.startswith("Server"):
                            ip = line.split()[-1]
                    
                    if ip:
                        # Générer la règle iptables pour bloquer l'IP
                        rule = f"iptables -A OUTPUT -d {ip} -j REJECT\n"
                        rules_file.write(rule)
                    else:
                        print(f"Impossible de résoudre l'IP pour {domain}")
                
                except subprocess.CalledProcessError:
                    print(f"Erreur lors de la résolution DNS pour {domain}", file=sys.stderr)

            print(f"Règles générées et sauvegardées dans {firewall_rules_file}")
except FileNotFoundError:
    print(f"Le fichier {csv_file} n'existe pas!", file=sys.stderr)
    sys.exit(1)
