pour relancer un build, sans son cache, avec téléchargement des images quand c'est nécessaire,
en affichant toute la sortie du build
docker compose build --no-cache --pull --progress=plain kafka-connect


pour lancer un nombre de replicas d'un service, l'option --scale en ligne de commande l'emporte sur le .yaml
docker compose up -d --build --scale consumer-tnx=2
attention il ne faut pas de container nommé pour que compose puisse attribuer un indice par rapport à l'image