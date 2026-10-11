FROM python:3.12-alpine

# For Debian
# RUN useradd -m -u 1000 user
# For Alpine
RUN adduser -D -u 1000 user

USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

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
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt


COPY --chown=user:user ./worker_incoming_tnx.py .


# ========================================
# PYTHON PATH
# ========================================
# Make /app/<PROJECT_LIBS> importable as python module
# <PROJECT_LIBS> copied inside container in deploy mode
# OVERRIDEN by pipeline bind mounted as volume in docker-compose.yml
# Make ~/app/<PROJECT_LIBS> visible from within ~/app/src/*.py
ENV PYTHONPATH="${HOME}/app"

CMD ["python", "worker_incoming_tnx.py"]