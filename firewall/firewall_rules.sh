#!/bin/bash

# Journaliser les connexions acceptées et refusées
#iptables -A INPUT -p icmp --icmp-type echo-request -j LOG --log-prefix "PING: "
#iptables -A OUTPUT -p icmp --icmp-type echo-reply -j LOG --log-prefix "PING: "
#iptables -A FORWARD -j LOG --log-prefix "ACCEPT: " --log-level 4
#iptables -A FORWARD -j LOG --log-prefix "REJECT: " --log-level 4


# Règles pour la banque centrale et le ministre(exception)
iptables -A FORWARD -s 192.168.0.3 -j ACCEPT
iptables -A FORWARD -s 192.168.0.4 -j ACCEPT

# Activer les règles du firewall au démarrage
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 9999
iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 9999
