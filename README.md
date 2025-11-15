# dapnet.tropo.alert.final.py
script python permettant de générer un indice de propagation troposphérique en fonction de la meteo locale et d'envoyer des alerte de propagation sur le dapnet en pocsag.

Pré-requis:

Installer python sur votre ordinateur sous windows. Assurer vous ensuite d'avoir REQUESTS d'installé.

Version python stable — le script va chercher sur l'api openmeteo.com les données méteo du QTH renseigné. il calcul ensuite un indice de propagation troposphérique en fonction des informations receuillies.
En fonction de l'indice de propagation il genere un message avec  "tropo faible", "moyenne" , "bonne", "forte/DX" et les infos meteo du moment ou les calcul ont été fait. le tout est envoyé sur le dapnet.

Dans les constantes: Vous devez modifier les entrées "DAPNET_USER" et "DAPNET_PASS" avec vos identifiant DAPNET. Dans "CALLSIGNS" vous devez entrer les indicatifs des om's a qui seront envoyés les messages en pocsag Dans "TX_GROUP" vous devez renseigner sur quel groupe d'emetteurs seront envoyés les messages en pocsag. vous pouvez aussi modifier le seuil d'alert "TROPO_MIN_LEVEL" pour declencher le seuil d'envoie des messages.

Vous pour automatiser le script avec le fichier .bat sous windows. Atention à bien renseigner le chemin vers le fichier "dapnet_solar_pocsag_final" dans le fichier .bat. Un log est automatiquement généré dans le fichier spécifié dans le .bat. Vous pouvez créer une tache recurente avec le planificateur de tache sous windows pour executer le script toutes le X minutes. ( atention a ne pas saturer le reseau )

je n'assure pas le SAV ;)

Documentation pour le dapnet: https://hampager.de/dokuwiki/doku.php

Vous souhaitez vous équiper d'un Pager? voici la meilleur adresse: https://www.bi7jta.org/

Version finale et stable du script by F4IGV 11/2025

Exemple de log généré:

<img width="1181" height="618" alt="screen_log_tropo_alert" src="https://github.com/user-attachments/assets/4679f5d0-4eb4-4f50-a620-8656a6630b61" />
