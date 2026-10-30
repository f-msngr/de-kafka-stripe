# Use a lightweight Python image
FROM python:3.12-slim


# Install necessary tools
RUN apt-get update && apt-get install -y \
    #nano \
    #lsof \
    curl \
    #net-tools \
    #build-essential \
    #libglib2.0-0 \
    #libsm6 \
    #libxext6 \
    #libxrender-dev \
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

# Define streamlit env variables
ENV SERVER_ADDRESS=0.0.0.0
#ENV SERVER_PORT=${CTNR_DASHBOARD_PORT}
#ENV STREAMLIT_SERVER_HEADLESS=true
# Streamlit listens to URL/dashboard
# Streamlit automatically prepends '/' to SERVER_BASEURLPATH (as opposed to fastapi root_path=)
#ENV SERVER_BASEURLPATH=${SERVER_BASEURLPATH}

WORKDIR $HOME/app

# ========================================
# BUILD TIME
# ========================================
# Copy necessary files into the image
# In local development, they will be overwritten by a volume mount
# Explicitly create working directories
# so they can be referred to in the WORKDIR directive
# REMEMBER: RUN, COPY, ADD are run as root by default in Docker
# NEED TO chown, chmod...

# requirements
# copy in WORKDIR $HOME/app
COPY ./requirements.txt ./requirements.txt
# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt


# pipeline files


# streamlit files
# Create streamlit dir
RUN mkdir -p ./streamlit && \
    chown -R user:user ./streamlit && \
    chmod -R g+w ./streamlit
# Copy dashboard files
COPY --chown=user:user ./.streamlit ./streamlit/.streamlit
COPY --chown=user:user ./src ./streamlit/src


# ========================================
# PYTHON PATH
# ========================================
ENV PYTHONPATH="${HOME}/app/streamlit/src"

# ========================================
# RUNTIME
# ========================================

# Command to run the Streamlit app
CMD ["sh", "-c", "streamlit run streamlit/src/app.py --server.address=$SERVER_ADDRESS --server.port=$SERVER_PORT --server.baseUrlPath=$SERVER_BASEURLPATH"]