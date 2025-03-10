# Utiliser une image Python avec MySQL
FROM python:3.11

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier le code
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port (Railway utilisera $PORT)
EXPOSE 8000

# Lancer le serveur
CMD ["gunicorn", "defi1_back.wsgi:application", "--bind", "0.0.0.0:8000"]
