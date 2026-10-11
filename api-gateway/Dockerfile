FROM python:3.12-slim


# Install system dependencies for debugging from within the container
# curl : needed by healthcheck 
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ========================================
# USER CREATION
# ========================================
# Create a non-root user
RUN useradd -m -u 1000 user
USER user
# Define his environment
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH


# ========================================
# APPLICATION CONFIGURATION
# ========================================
# Set environment variables
# Possibly modified by Makefile commands

# Sets the working directory for the API
WORKDIR $HOME/app

# ========================================
# BUILD TIME
# ========================================
# Copy necessary files into the image
# In local development, they will be overwritten by a volume bind mount
# REMEMBER: RUN, COPY, ADD are run as root by default in Docker
# NEED TO chown, chmod...

# requirements
# copy in WORKDIR
COPY --chown=user:user ./api-gateway/requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user:user ./api-gateway/src ./src

# Set environment variables
ENV PROJECT_ROOT="/app"


# ========================================
# PYTHON PATH
# ========================================
# Make /app/<PROJECT_LIBS> importable as python module
# <PROJECT_LIBS> copied inside container in deploy mode
# OVERRIDEN by pipeline bind mounted as volume in docker-compose.yml
# Make ~/app/<PROJECT_LIBS> visible from within ~/app/src/*.py
ENV PYTHONPATH="${HOME}/app"

# --reload pour appliquer les modifs du code en live
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port=$CTNR_APIGATEWAY_PORT --reload"]