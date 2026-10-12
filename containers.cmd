pour relancer un build, sans son cache, avec téléchargement des images quand c'est nécessaire,
en affichant toute la sortie du build
docker compose build --no-cache --pull --progress=plain kafka-connect

