# Sistema de Soporte Tecnico
# Autor: Gerardo Escamilla Cerda
# Fecha: Abril 2026

import time
import os
import mysql.connector
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Conexion a la base de datos usando variables de entorno
def get_db_connection():
    connection = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME', 'soporte_db')
    )
    return connection


# Pagina HTML principal con los formularios
HTML_PRINCIPAL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Sistema de Soporte Tecnico</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #f5f5f5; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        form { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        label { display: block; margin: 8px 0 4px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        button:hover { background: #2980b9; }
        .aviso { background: #fff3cd; padding: 10px; border-radius: 4px; border-left: 4px solid #ffc107; margin-bottom: 15px; }
        a { display: inline-block; margin: 5px; padding: 8px 16px; background: #ecf0f1; border-radius: 4px; text-decoration: none; color: #2c3e50; }
        a:hover { background: #bdc3c7; }
    </style>
</head>
<body>
    <h1>Sistema de Soporte Tecnico</h1>
    <p>TechNova Solutions</p>

    <div>
        <a href="/tickets">Ver Tickets Abiertos</a>
        <a href="/clientes">Ver Clientes</a>
        <a href="/tecnicos">Ver Tecnicos</a>
    </div>

    <h2>Abrir Nuevo Ticket</h2>
    <div class="aviso">Al abrir un ticket el sistema notifica al area tecnica (tarda unos segundos)</div>
    <form action="/tickets" method="POST">
        <label>Cliente ID:</label>
        <input type="number" name="cliente_id" placeholder="Ej: 1" required>
        <label>Titulo:</label>
        <input type="text" name="titulo" placeholder="Ej: No puedo acceder al sistema" required>
        <label>Descripcion:</label>
        <textarea name="descripcion" rows="3" placeholder="Describe el problema..." required></textarea>
        <label>Prioridad:</label>
        <select name="prioridad">
            <option value="baja">Baja</option>
            <option value="media" selected>Media</option>
            <option value="alta">Alta</option>
            <option value="critica">Critica</option>
        </select>
        <button type="submit">Abrir Ticket</button>
    </form>

    <h2>Asignar Tecnico a Ticket</h2>
    <form action="/tickets/asignar" method="POST">
        <label>ID del Ticket:</label>
        <input type="number" name="ticket_id" placeholder="Ej: 1" required>
        <label>ID del Tecnico:</label>
        <input type="number" name="tecnico_id" placeholder="Ej: 1" required>
        <button type="submit">Asignar Tecnico</button>
    </form>

    <h2>Actualizar Estado de Ticket</h2>
    <form action="/tickets/estado" method="POST">
        <label>ID del Ticket:</label>
        <input type="number" name="ticket_id" placeholder="Ej: 1" required>
        <label>Nuevo Estado:</label>
        <select name="estado">
            <option value="abierto">Abierto</option>
            <option value="en_progreso">En Progreso</option>
            <option value="resuelto">Resuelto</option>
        </select>
        <button type="submit">Actualizar Estado</button>
    </form>
</body>
</html>
"""


# Ruta 1 - muestra la pagina principal
@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_PRINCIPAL)


# Ruta 2 - abre un nuevo ticket y envia notificacion al area tecnica
@app.route('/tickets', methods=['POST'])
def abrir_ticket():
    connection = None
    cursor = None
    try:
        # Leer datos del formulario o JSON
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        cliente_id  = data.get('cliente_id')
        titulo      = data.get('titulo')
        descripcion = data.get('descripcion')
        prioridad   = data.get('prioridad', 'media')

        # Verificar que los campos obligatorios esten presentes
        if not all([cliente_id, titulo, descripcion]):
            return jsonify({'error': 'Faltan campos: cliente_id, titulo, descripcion'}), 400

        # Guardar el ticket en la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()

        # Se usan parametros %s para evitar inyeccion SQL
        sql = """
            INSERT INTO tickets (cliente_id, titulo, descripcion, prioridad, estado)
            VALUES (%s, %s, %s, %s, 'abierto')
        """
        cursor.execute(sql, (cliente_id, titulo, descripcion, prioridad))
        connection.commit()
        ticket_id = cursor.lastrowid

        # Tarea pesada: simula el envio de notificacion al area tecnica
        # En un sistema real aqui iria el envio de email o SMS
        print(f"Iniciando notificacion para ticket #{ticket_id}...")
        time.sleep(7)
        print(f"Notificacion enviada para ticket #{ticket_id}")

        return jsonify({
            'mensaje': f'Ticket #{ticket_id} abierto. Area tecnica notificada.',
            'ticket_id': ticket_id,
            'estado': 'abierto',
            'prioridad': prioridad
        }), 201

    except mysql.connector.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
    finally:
        # Siempre cerrar la conexion aunque haya error
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Ruta 3 - consulta todos los tickets abiertos ordenados por prioridad
@app.route('/tickets', methods=['GET'])
def ver_tickets_abiertos():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Ordenar por prioridad de mayor a menor urgencia
        sql = """
            SELECT
                t.id,
                t.titulo,
                t.descripcion,
                t.prioridad,
                t.estado,
                t.creado_en,
                c.nombre AS cliente,
                c.email AS email_cliente,
                COALESCE(tec.nombre, 'Sin asignar') AS tecnico
            FROM tickets t
            JOIN clientes c ON t.cliente_id = c.id
            LEFT JOIN tecnicos tec ON t.tecnico_id = tec.id
            WHERE t.estado = 'abierto'
            ORDER BY FIELD(t.prioridad, 'critica', 'alta', 'media', 'baja')
        """
        cursor.execute(sql)
        tickets = cursor.fetchall()

        for ticket in tickets:
            if ticket.get('creado_en'):
                ticket['creado_en'] = str(ticket['creado_en'])

        return jsonify({'total': len(tickets), 'tickets_abiertos': tickets}), 200

    except mysql.connector.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Ruta 4 - asigna un tecnico a un ticket
@app.route('/tickets/asignar', methods=['POST'])
def asignar_tecnico():
    connection = None
    cursor = None
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        ticket_id  = data.get('ticket_id')
        tecnico_id = data.get('tecnico_id')

        if not all([ticket_id, tecnico_id]):
            return jsonify({'error': 'Faltan campos: ticket_id, tecnico_id'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        # Asignar tecnico y cambiar estado a en_progreso
        sql = """
            UPDATE tickets
            SET tecnico_id = %s, estado = 'en_progreso'
            WHERE id = %s AND estado != 'resuelto'
        """
        cursor.execute(sql, (tecnico_id, ticket_id))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Ticket no encontrado o ya esta resuelto'}), 404

        return jsonify({
            'mensaje': f'Tecnico asignado al ticket #{ticket_id}.',
            'ticket_id': int(ticket_id),
            'tecnico_id': int(tecnico_id)
        }), 200

    except mysql.connector.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Ruta 5 - cambia el estado de un ticket
@app.route('/tickets/estado', methods=['POST'])
def actualizar_estado():
    connection = None
    cursor = None
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        ticket_id = data.get('ticket_id')
        estado    = data.get('estado')

        estados_validos = ['abierto', 'en_progreso', 'resuelto']
        if not ticket_id or estado not in estados_validos:
            return jsonify({'error': f'Estado invalido. Usa: {estados_validos}'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        sql = "UPDATE tickets SET estado = %s WHERE id = %s"
        cursor.execute(sql, (estado, ticket_id))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': f'Ticket #{ticket_id} no encontrado'}), 404

        return jsonify({
            'mensaje': f'Ticket #{ticket_id} actualizado a: {estado}',
            'ticket_id': int(ticket_id),
            'nuevo_estado': estado
        }), 200

    except mysql.connector.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Ruta 6 - lista todos los clientes
@app.route('/clientes', methods=['GET'])
def ver_clientes():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT id, nombre, email, creado_en FROM clientes ORDER BY id")
        clientes = cursor.fetchall()

        for cliente in clientes:
            if cliente.get('creado_en'):
                cliente['creado_en'] = str(cliente['creado_en'])

        return jsonify({'total': len(clientes), 'clientes': clientes}), 200

    except mysql.connector.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Ruta 7 - lista todos los tecnicos
@app.route('/tecnicos', methods=['GET'])
def ver_tecnicos():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT id, nombre, especialidad, creado_en FROM tecnicos ORDER BY id")
        tecnicos = cursor.fetchall()

        for tecnico in tecnicos:
            if tecnico.get('creado_en'):
                tecnico['creado_en'] = str(tecnico['creado_en'])

        return jsonify({'total': len(tecnicos), 'tecnicos': tecnicos}), 200

    except mysql.connector.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Punto de entrada de la aplicacion
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
