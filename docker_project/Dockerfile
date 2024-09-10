# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install necessary packages and dependencies
RUN apt-get update && \
    apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    libglib2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxtst6 \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 libasound2 libu2f-udev libvulkan1 xdg-utils fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy  and install Google Chrome
COPY google-chrome-stable_current_amd64.deb /google-chrome-stable_current_amd64.deb
RUN  apt-get install -y /google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb


# Copy the rest of your application code
COPY filter_feed.py /app

# Set the working directory
WORKDIR /app

# Specify the default command
CMD ["python3", "filter_feed.py"]

