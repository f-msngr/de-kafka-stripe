FROM python:3.12-alpine

# For Debian
# RUN useradd -m -u 1000 user
# For Alpine
RUN adduser -D -u 1000 user

USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# requirements
# copy in WORKDIR $HOME/app
COPY --chown=user:user ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt


COPY --chown=user:user ./consumer_replicate.py .


CMD ["python", "consumer_replicate.py"]