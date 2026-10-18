FROM python:3.12-slim

# For Debian
RUN useradd -m -u 1000 user

# For Alpine
# RUN adduser -D -u 1000 user
# Utiliser apk et build-base (équivalent de build-essential)
# RUN apk update && apk add --no-cache \
#    build-base \
#    libffi-dev

# Ajout de Git
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Évite que Python n'écrive des fichiers .pyc sur le disque
ENV PYTHONDONTWRITEBYTECODE=1
# Force Python à afficher immédiatement les logs dans le terminal sans mise en cache
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH    

# Définit le dossier de travail dans le conteneur
WORKDIR $HOME/app
RUN chown user:user $HOME/app

USER user

# ========================================
# BUILD TIME
# ========================================
# Copy necessary files into the image
# In local development, they will be overwritten by a volume bind mount
# REMEMBER: RUN, COPY, ADD are run as root by default in Docker
# NEED TO chown, chmod...

# requirements
# copy in WORKDIR $HOME/app
COPY --chown=user:user ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# profiles.yml
COPY --chown=user:user ./profiles.yml $HOME/.dbt/profiles.yml

# ======================
# COPIE DU PROJECT
# ======================
# En local, <host>/project est un bind mount
# En déploiement, il faut copier le contenu du rep dans app/
COPY --chown=user:user ./project/ $HOME/app/

# ======================
# START SCRIPT
# ======================
COPY --chown=user:user ./start.sh $HOME/start.sh
RUN chmod +x $HOME/start.sh


# ========================================
# PYTHON PATH
# ========================================
# Make /app/<PROJECT_LIBS> importable as python module
# <PROJECT_LIBS> copied inside container in deploy mode
# OVERRIDEN by pipeline bind mounted as volume in docker-compose.yml
# Make ~/app/<PROJECT_LIBS> visible from within ~/app/src/*.py
ENV PYTHONPATH="${HOME}/app"

# Commande par défaut (à adapter selon le script ou dbt)
CMD ["/home/user/start.sh"]