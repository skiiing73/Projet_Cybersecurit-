# -*- coding: utf-8 -*-

import socket
import requests
from bs4 import BeautifulSoup
import re

def extract_url_from_request(request_data):
    """Extraire l'URL de la requête HTTP"""
    # Utilisation d'une expression régulière pour extraire l'URL du GET request
    match = re.search(r"GET (.*?) HTTP", request_data)
    if match:
        return match.group(1)  # Retourner l'URL extraite
    return None  # Si l'URL n'est pas trouvée, retourner None

# Liste de mots-clés à bloquer
keywords = ["malware", "phishing", "hack"]

def check_for_keywords(url):
    """ Fonction pour vérifier la présence de mots-clés sur une page """
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        for keyword in keywords:
            if keyword in soup.get_text():
                return False  # Site bloqué
        return True  # Site accessible
    except requests.exceptions.RequestException as e:
        
        return False  # En cas d'erreur, bloquer le site

def handle_connection(conn):
    """ Fonction pour gérer la connexion et filtrer les sites """
    data = conn.recv(1024).decode()
    url = extract_url_from_request(data)  # Implémentez cette fonction pour extraire l'URL du trafic HTTP
    if check_for_keywords(url):
        conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")  # Réponse si le site est autorisé
    else:
        conn.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n")  # Réponse si le site est bloqué
    conn.close()

# Code pour créer un serveur et intercepter les connexions
def start_server():
    """ Démarrer le serveur pour intercepter les connexions HTTP """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))  # Port d'écoute pour les requêtes
    server.listen(5)
    print("Serveur de filtrage démarré sur le port 9999...")
    
    while True:
        conn, addr = server.accept()
        handle_connection(conn)

if __name__ == "__main__":
    start_server()
