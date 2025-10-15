import socket
import threading
import sys  

def recibir_mensajes(socket):
    while True:
        global servidor_activo
        try:
            # Recibe el dato
            datos = socket.recv(1024)

            if not datos:
                # Servidor cerró la conexión correctamente
                print("Servidor desconectado...")
                servidor_activo = False
                break

            # Imprimir en consola
            print(datos.decode('utf-8'))

        # Error que da cuando el servidor cierra la conexión bruscamente mientras el cliente intentaba recibir datos
        except (ConnectionResetError, OSError):
            servidor_activo = False
            break

# Variable global para controlar si el servidor sigue activo
servidor_activo = True

# Crear socket del cliente
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar con el servidor
try:
    cliente.connect(("localhost", 8000))

# Cuando el cliente quiere conectarse pero no hay nadie escuchando en esa dirección y puerto
except ConnectionRefusedError:
    print("No se pudo conectar al servidor. Asegúrate de que esté en ejecución.")
    sys.exit()

# Pedir nombre
pregunta = cliente.recv(1024).decode('utf-8')
nombre = input(pregunta)

# Si está vacío, enviar "Desconocido"
if not nombre.strip():
    nombre = "Desconocido"

# Enviar nombre a servidor
cliente.send(nombre.encode('utf-8'))

print("Conectado al servidor. Escribe 'salir' para terminar.\n")

# Crear hilo para recibir mensajes
hilo_recibir = threading.Thread(target=recibir_mensajes, args=(cliente,), daemon=True)
hilo_recibir.start()

try:
    # Bucle de envío de mensajes
    while servidor_activo:
        mensaje = input()
        # Si ingresa salir se corta el bucle
        if mensaje.lower() == "salir":
            print("Saliste del grupo.")
            cliente.close()
            sys.exit()
        try:
            # Enviar mensaje al servidor
            cliente.send(mensaje.encode('utf-8'))

        # Error que da cuando el servidor cierra la conexión bruscamente mientras el cliente intentaba enviar datos
        except (ConnectionResetError, OSError):
            cliente.close()
            sys.exit()

except KeyboardInterrupt:
    print("Saliste del grupo.")
    cliente.close()
    sys.exit()

