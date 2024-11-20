import subprocess
import pandas as pd

# Charger la liste des sites depuis un fichier CSV
csv_file = "liste_sites.csv"  # Remplace par le chemin de ton fichier
df = pd.read_csv(csv_file)

# Extraire la liste des sites
site_list = df['url'].tolist()
print(f"Liste des sites à bloquer : {site_list}")

def block_sites(sites):
    for site in sites:
        try:
            # Résoudre le nom de domaine en adresse IP
            print(f"Résolution DNS pour {site}...")
            result = subprocess.run(
                ["nslookup", site],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Filtrer l'adresse IP dans la sortie
            ip_lines = [line for line in result.stdout.splitlines() if "Address" in line]
            ip = ip_lines[-1].split(":")[-1].strip() if ip_lines else None

            if ip:
                # Ajouter une règle iptables pour bloquer cette IP
                print(f"Blocage de {site} ({ip}) via iptables...")
                subprocess.run(["iptables", "-A", "OUTPUT", "-d", ip, "-j", "REJECT"], check=True)
            else:
                print(f"Impossible de résoudre l'adresse IP pour {site}")

        except Exception as e:
            print(f"Erreur lors du blocage du site {site}: {e}")

    # Sauvegarder les règles iptables
    print("Sauvegarde des règles iptables...")
    subprocess.run(["iptables-save", ">", "/etc/iptables/rules.v4"], shell=True, check=True)

# Bloquer les sites
block_sites(site_list)
