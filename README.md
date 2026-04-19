# Sistema de Soporte Tecnico

**Alumno:** Gerardo Escamilla Cerda  
**Dominio:** Dominio 4 — Soporte Tecnico  
**Fecha:** Abril 2026

---

## ¿Qué problema resuelve?

Este sistema permite gestionar tickets de soporte tecnico dentro de una empresa. Los clientes pueden reportar problemas, los tickets se asignan a tecnicos y se hace seguimiento del estado hasta que se resuelven. Todo corre en contenedores Docker sobre una instancia EC2 en AWS, con base de datos en RDS MySQL.

---

## Estructura de la Base de Datos

| Tabla | Descripcion | Relacion |
|-------|-------------|----------|
| `clientes` | Guarda los datos de los clientes que abren tickets | — |
| `tecnicos` | Guarda los datos de los tecnicos que atienden tickets | — |
| `tickets` | Guarda cada ticket con su estado y prioridad | FK a clientes y tecnicos |

---

## Rutas de la API

| Metodo | Ruta | Que hace |
|--------|------|----------|
| GET | `/` | Interfaz HTML principal con formularios |
| POST | `/tickets` | Abre un nuevo ticket y notifica al area tecnica |
| GET | `/tickets` | Consulta todos los tickets abiertos ordenados por prioridad |
| POST | `/tickets/asignar` | Asigna un tecnico a un ticket existente |
| POST | `/tickets/estado` | Actualiza el estado de un ticket |
| GET | `/clientes` | Lista todos los clientes registrados |
| GET | `/tecnicos` | Lista todos los tecnicos registrados |

---

## ¿Cual es la tarea pesada y por qué bloquea el sistema?

La tarea pesada esta en la ruta `POST /tickets`. Cuando se abre un nuevo ticket, el sistema simula el envio de una notificacion al area tecnica usando `time.sleep(7)`. Esto representa lo que en un sistema real seria el envio de un email o SMS.

El problema es que Flask por defecto atiende una peticion a la vez. Si un usuario abre un ticket y el sistema entra al `time.sleep`, todos los demas usuarios tienen que esperar esos 7 segundos. Esto se vuelve critico con muchos usuarios simultaneos, ya que el sistema se bloquea completamente mientras procesa una sola notificacion.

---

## Como levantar el proyecto

### Requisitos previos
- Docker instalado en la maquina
- Acceso a una instancia de RDS MySQL en AWS
- Puerto 5000 abierto en el grupo de seguridad de EC2

---

### Monolito

```bash
# 1. Clonar el repositorio
git clone https://github.com/GeraEsc/gerardo-escamilla-soporte.git
cd gerardo-escamilla-soporte

# 2. Crear las tablas en RDS (solo la primera vez)
#    Reemplaza ENDPOINT_RDS con tu endpoint real de RDS
mysql -h ENDPOINT_RDS -u admin -p < schema.sql

# 3. Construir la imagen Docker
docker build -t soporte-tecnico .

# 4. Correr el contenedor con las variables de entorno
#    Reemplaza ENDPOINT_RDS y PASSWORD con tus valores reales
docker run -d -p 5000:5000 \
  -e DB_HOST=ENDPOINT_RDS \
  -e DB_USER=admin \
  -e DB_PASSWORD=PASSWORD \
  -e DB_NAME=soporte_db \
  -e PYTHONUNBUFFERED=1 \
  --name soporte-tecnico \
  soporte-tecnico

# 5. Verificar que el contenedor esta corriendo
docker ps

# 6. Abrir en el navegador
#    Reemplaza IP_EC2 con la IP publica de tu instancia EC2
#    http://IP_EC2:5000
```

---

### Microservicios 

```bash
# 1. Clonar el repositorio (si no lo hiciste antes)
git clone https://github.com/GeraEsc/gerardo-escamilla-soporte.git
cd gerardo-escamilla-soporte

# 2. Crear las tablas en RDS (solo la primera vez)
mysql -h ENDPOINT_RDS -u admin -p < schema.sql

# 3. Entrar a la carpeta de microservicios
cd microservicios

# 4. Crear el archivo .env con las credenciales de la base de datos
#    (nunca subir este archivo a GitHub)
cat > .env << EOF
DB_HOST=ENDPOINT_RDS
DB_USER=admin
DB_PASSWORD=PASSWORD
DB_NAME=soporte_db
EOF

# 5. Levantar ambos servicios con Docker Compose
docker-compose up --build -d

# 6. Verificar que ambos contenedores estan corriendo
#    servicio_a debe mostrar 0.0.0.0:5000->5000/tcp
#    servicio_b no debe tener puerto expuesto externamente
docker ps

# 7. Abrir en el navegador
#    http://IP_EC2:5000

# 8. Para detener los servicios
docker-compose down
```

---

### Comandos utiles de diagnostico

```bash
# Ver logs del monolito en tiempo real
docker logs -f soporte-tecnico

# Ver logs de los microservicios
docker logs -f servicio_a
docker logs -f servicio_b

# Detener el monolito
docker stop soporte-tecnico

# Eliminar el contenedor del monolito
docker rm soporte-tecnico
```

---

## Decisiones tecnicas

Las tres tablas se diseñaron pensando en las relaciones reales del negocio: un ticket siempre pertenece a un cliente, pero puede no tener tecnico asignado todavia, por eso `tecnico_id` permite valores NULL. Se usaron ENUMs para prioridad y estado para garantizar que solo entren valores validos. Para el manejo de errores, cada ruta tiene su propio bloque try/except con un finally que siempre cierra la conexion a la base de datos, evitando que se acumulen conexiones abiertas. Lo mas dificil fue configurar la comunicacion entre microservicios usando el nombre del contenedor como hostname, ya que Docker no resuelve conexiones por IP directa entre contenedores de la misma red.

---

## Arquitectura de Microservicios

### Separacion de servicios

**Servicio A** se encarga de toda la interfaz de usuario y las rutas HTTP. Recibe las peticiones, guarda los datos en la base de datos y llama al Servicio B para la notificacion. No tiene ninguna logica pesada ni `time.sleep()`.

**Servicio B** solo recibe la solicitud de notificacion y ejecuta el proceso pesado con `time.sleep(7)`. No tiene rutas HTML ni acceso directo desde el exterior.

### Comunicacion interna

El Servicio A llama al Servicio B usando `http://servicio_b:5001/notificar`. Docker resuelve el nombre `servicio_b` automaticamente gracias al DNS interno de la red creada por docker-compose. No se usa la IP de la EC2 ni localhost.

### Resiliencia

Si el Servicio B se cae, el Servicio A detecta el error pero el ticket igual se guarda en la base de datos. La respuesta cambia de `"estado":"notificacion_enviada"` a `"estado":"servicio_b_no_disponible"`, demostrando que el sistema principal sigue operando aunque falle el componente de notificaciones.
