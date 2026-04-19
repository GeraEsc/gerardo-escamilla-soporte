# 1. Clonar el repositorio
git clone https://github.com/GeraEsc/gerardo-escamilla-soporte.git

# 2. Crear las tablas en RDS
mysql -h ENDPOINT_RDS -u admin -p < schema.sql

# 3. Construir la imagen del monolito
docker build -t soporte-tecnico .

# 4. Correr el contenedor del monolito
docker run -d -p 5000:5000 -e DB_HOST=ENDPOINT_RDS -e DB_USER=admin -e DB_PASSWORD=PASSWORD -e DB_NAME=soporte_db --name soporte-tecnico soporte-tecnico

# 5. Abrir en navegador
# http://IP_EC2:5000

# --- Para los microservicios ---

# 6. Entrar a la carpeta de microservicios
cd microservicios

# 7. Crear archivo .env con las credenciales
# DB_HOST=ENDPOINT_RDS
# DB_USER=admin
# DB_PASSWORD=PASSWORD
# DB_NAME=soporte_db

# 8. Levantar los servicios
docker-compose up --build -d

# 9. Verificar que ambos corren
docker ps
