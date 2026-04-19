# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codigo de la aplicacion
COPY app.py .

# Exponer el puerto 5000
EXPOSE 5000

# Comando para iniciar la aplicacion
CMD ["python", "app.py"]
