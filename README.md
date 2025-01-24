Projet de Cybersécurité. 
Coté Défense.
DEGOUEY Corentin BERCIER Thomas WILHELM Arno


image pour construire le conteneur Docker : 

_docker build -t xtrm0/quagga_

Lancez le réseau :
_kathara lstart_

Dans le powershell du firewal lancez le proxy: 
_python3 proxy.py_

Vous pouvez maintenant essayez les différents fonctionnalités suivantes : 
-réseau filtré par mots clés et par sites pour les habitants mais pas le ministre et la banque
-enregistrement de toutes les connexions au réseau extérieur dans un fichier.

Les mots clés et les sites interdits sont dans les fichiers csv. 
