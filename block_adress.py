import subprocess
import sys

# Nom du site à bloquer
site = "www.example.com"

# Résoudre l'IP du site avec 'nslookup'
try:
    result = subprocess.run(['nslookup', site], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Récupérer l'IP à partir du résultat de nslookup
    site_ip = None
    for line in result.stdout.splitlines():
        if "Address" in line:
            site_ip = line.split()[-1]  # L'adresse IP se trouve à la fin de la ligne
            break

    if site_ip:
        # Bloquer l'IP dans iptables
        subprocess.run(['iptables', '-A', 'FORWARD', '-d', site_ip, '-j', 'REJECT'])
        print(f"Site {site} ({site_ip}) bloqué.")
    else:
        print(f"L'adresse IP de {site} n'a pas pu être trouvée.")

except subprocess.CalledProcessError as e:
    print(f"Erreur lors de la résolution DNS ou de l'exécution de la commande: {e}")
    sys.exit(1)
