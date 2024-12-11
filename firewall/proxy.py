import socket
import requests
from bs4 import BeautifulSoup
import re
import csv
import sqlite3
from urllib.parse import urlparse
from datetime import datetime

# Charger les mots-clés depuis un fichier CSV
def load_keywords_from_csv(filename):
    """ Charger les mots-clés depuis un fichier CSV """
    keywords = []
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Chaque colonne contient un mot-clé
                keywords.extend(row)
    except Exception as e:
        print(f"Erreur lors du chargement du fichier CSV des mots-clés: {e}")
    return keywords

# Charger les URLs bloquées depuis un fichier CSV
def load_blocked_urls_from_csv(filename):
    """ Charger les URLs bloquées depuis un fichier CSV """
    blocked_urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Chaque ligne contient une URL à bloquer
                blocked_urls.append(row[0].strip())
    except Exception as e:
        print(f"Erreur lors du chargement du fichier CSV des URLs bloquées: {e}")
    return blocked_urls

# Créer la base de données SQLite et la table
def create_db():
    conn = sqlite3.connect('requests_log.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ip_address TEXT,
            request_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Inscrire la requête dans la base de données
def log_request(ip_address, request_url):
    conn = sqlite3.connect('requests_log.db')
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO requests_log (timestamp, ip_address, request_url)
        VALUES (?, ?, ?)
    ''', (timestamp, ip_address, request_url))
    conn.commit()
    conn.close()

def extract_url_from_request(request_data):
    """Extraire l'URL de la requête HTTP"""
    
    # Chercher la ligne de requête GET
    match = re.search(r"GET (.*?) HTTP", request_data)
    if match:
        url = match.group(1).strip()  # Extraire l'URL brute
        
        # Si l'URL est relative (commence par /), ajouter le domaine et le schéma
        if url.startswith("/"):
            # Extraire le domaine à partir de l'en-tête 'Host' (les requêtes HTTP incluent souvent un en-tête 'Host')
            host_match = re.search(r"Host: ([^\r\n]+)", request_data)
            if host_match:
                domain = host_match.group(1).strip()
                url = f"http://{domain}{url}"  # Ajouter le schéma http:// et le domaine
        return url  # Retourner l'URL complète
    return None  # Si l'URL n'est pas trouvée, retourner None

# Vérifier la présence de mots-clés sur une page
def check_for_keywords(url, keywords):
    """ Vérifie si les mots-clés sont présents sur la page """
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        for keyword in keywords:
            if keyword in soup.get_text():
                print(f"Mots-clés trouvés sur {url}: {keyword}")
                return False  # Site bloqué
        return True  # Site accessible
    except requests.exceptions.RequestException as e:
        return True  # En cas d'erreur, bloquer le site

def handle_connection(conn, keywords, blocked_urls, allowed_ips):
    """ Fonction pour gérer la connexion et filtrer les sites """
    try:
        # Récupérer l'adresse IP de la machine cliente
        client_ip, client_port = conn.getpeername()
        print(f"Requête reçue de {client_ip}:{client_port}")

        # Recevoir les données de la requête HTTP
        data = conn.recv(1024).decode(errors='ignore')  # Décodage avec gestion des erreurs
        if not data:
            print("Aucune donnée reçue.")
            conn.close()
            return

        url = extract_url_from_request(data)  # Extraire l'URL
        if not url:
            print("Aucune URL valide trouvée.")
            conn.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            return

        # Enregistrer la requête dans la base de données SQLite
        log_request(client_ip, url)

        # Si l'IP de la machine est autorisée, on accepte tout
        if client_ip in allowed_ips:
            print(f"Machine avec IP {client_ip} autorisée, accès sans filtrage.")
            response = requests.get(url)
            content = response.content
            conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
            conn.sendall(content)  # Envoi du contenu de la page web
            conn.close()
            return
        else:
            # Vérifier si l'URL est dans la liste des URLs bloquées
            if url in blocked_urls:
                print(f"Site bloqué car interdit : {url}")
                conn.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n")
            # Vérifier les mots-clés
            elif check_for_keywords(url, keywords):
                # Faire une requête GET vers l'URL autorisée et récupérer le contenu
                response = requests.get(url)
                content = response.content
                print(f"Site autorisé : {url}")
                conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
                conn.sendall(content)  # Envoi du contenu de la page web
            else:
                print(f"Site bloqué par mots-clés : {url}")
                conn.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n")
    except Exception as e:
        print(f"Erreur lors du traitement : {e}")
    finally:
        conn.close()

# Démarrer le serveur pour intercepter les connexions HTTP
def start_server(keywords, blocked_urls, allowed_ips):
    """ Démarrer le serveur pour intercepter les connexions HTTP """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))  # Port d'écoute pour les requêtes
    server.listen(5)
    print("Serveur de filtrage démarré sur le port 9999...")

    while True:
        conn, addr = server.accept()
        handle_connection(conn, keywords, blocked_urls, allowed_ips)

# Charger les mots-clés et les URLs bloquées depuis les fichiers CSV
keywords = load_keywords_from_csv('mots_cles.csv')  # Charger les mots-clés depuis le fichier CSV
blocked_urls = load_blocked_urls_from_csv('liste_sites.csv')  # Charger les URLs bloquées depuis le fichier CSV

# Liste des IPs autorisées (machines exceptionnelles)
allowed_ips = ["192.168.0.3", "192.168.0.4"]

# Créer la base de données SQLite et la table
create_db()

if keywords and blocked_urls:
    start_server(keywords, blocked_urls, allowed_ips)
else:
    print("Aucun mot-clé ou URL bloquée trouvé dans les fichiers CSV.")
