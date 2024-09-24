FROM python:3.11.5-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install necessary dependencies for installing Java
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg2 \
    software-properties-common \
    ca-certificates \
    curl

# Install the default JDK, which will pull the correct Java version (typically OpenJDK 11)
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jdk

# Set JAVA_HOME environment variable for Java
# ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
# ENV PATH="$JAVA_HOME/bin:$PATH"

WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --system --deploy

# Create the logs directory and set permissions
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Creates a non-root user and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

# Switch to the non-root user
USER appuser