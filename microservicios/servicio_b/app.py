# Servicio B - Sistema de Soporte Tecnico
# Responsabilidad: procesar la notificacion al area tecnica (tarea pesada)
# Este servicio NO tiene rutas de interfaz HTML
# Autor: Gerardo Escamilla Cerda
# Fecha: Abril 2026

import time
from flask import Flask, request, jsonify

app = Flask(__name__)


# Ruta unica: recibe la solicitud de notificacion del Servicio A
# y ejecuta el proceso pesado (simula envio de email/SMS al area tecnica)
@app.route('/notificar', methods=['POST'])
def notificar():
    try:
        data = request.get_json()
        ticket_id = data.get('ticket_id')
        prioridad = data.get('prioridad', 'media')

        if not ticket_id:
            return jsonify({'error': 'Falta ticket_id'}), 400

        # Tarea pesada: simula el envio de notificacion al area tecnica
        # En un sistema real aqui iria el envio de email o SMS
        print(f"[Servicio B] Iniciando notificacion para ticket #{ticket_id} con prioridad {prioridad}...")
        time.sleep(7)
        print(f"[Servicio B] Notificacion enviada para ticket #{ticket_id}")

        return jsonify({
            'estado': 'notificacion_enviada',
            'ticket_id': ticket_id,
            'prioridad': prioridad,
            'mensaje': f'Area tecnica notificada del ticket #{ticket_id}'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error en Servicio B: {str(e)}'}), 500


# Punto de entrada - corre en puerto 5001
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
