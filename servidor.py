import socket
import selectors
import threading

# Leer consola del servidor
def leer_consola():
    global servidor_activo
    while True:
        try:
            mensaje = input()
            if mensaje.lower() == "salir":
                print("Servidor cerrado.")

                # Avisar al bucle principal
                servidor_activo = False  

                # Avisar a todos los clientes antes de cerrar (clientes.keys() devuelve todos los sockets conectados)
                for cliente_sock in list(clientes.keys()):
                    # Dejar de vigilar el socket
                    sel.unregister(cliente_sock)

                    # Cierra conexion del socket
                    cliente_sock.close()

                    # Eliminar de clientes conectados
                    clientes.pop(cliente_sock, None)

        # Si es fin de entrada
        except EOFError:
            break

# Aceptar conexion
def aceptar_conexion(socket):
    # Aceptar cliente (conexion = socket de ese cliente, addr = direccion del cliente, es tupla (IP, Puerto))
    conexion, addr = socket.accept()  

    # No bloquea el servidor si el cliente aún no envía datos
    conexion.setblocking(False)

    # Guardamos el socket con nombre None y la dirección
    clientes[conexion] = {"nombre": None, "direccion": addr}

    # Registrar este cliente para lectura
    sel.register(conexion, selectors.EVENT_READ, data=addr)

    # Preguntar el nombre al cliente
    conexion.send("Nombre: ".encode('utf-8'))

# Desconexion del cliente
def desconectar_cliente(socket):
    # Obtener datos del cliente, si no hay info devuelve {}
    info = clientes.get(socket, {})

    # Extrae nombre del cliente, si no tiene usa Desconocido
    nombre = info.get("nombre") or "Desconocido"

    # Avisar a los demás clientes y al servidor
    for cliente_sock, cliente_info in list(clientes.items()):
        if cliente_sock != socket and cliente_info.get("nombre") is not None:
            try:
                cliente_sock.send(f"{nombre} abandonó el chat.".encode('utf-8'))

            # Si un cliente se desconecta bruscamente
            except (ConnectionResetError, OSError):
                # Cerrar ese socket también
                sel.unregister(cliente_sock)
                cliente_sock.close()
                clientes.pop(cliente_sock, None)
                
        elif cliente_sock == socket:
            print(f"{nombre} desconectado.")

    # Sacar del selector y cerrar socket
    sel.unregister(socket)
    socket.close()
    clientes.pop(socket, None)

# Manejar mensajes de clientes
def manejar_cliente(socket):
    try:
        # Recibe el dato que manda el cliente
        # 1024 indica la cantidad máxima de bytes a recibir en esta llamada.
        datos = socket.recv(1024)

        if datos:
            if clientes[socket]["nombre"] is None:
                # Primer mensaje = nombre
                nombre = datos.decode('utf-8').strip()

                # Asignamos al socket
                clientes[socket]["nombre"] = nombre

                # Obtener la direccion del socket
                addr = clientes[socket]["direccion"]

                # Avisar a los demás clientes
                for cliente_sock, _ in list(clientes.items()):
                    # Para que no le mande al cliente que esta ingresando
                    if clientes[cliente_sock]["direccion"] != addr:
                        cliente_sock.send(f"{nombre} se conectó".encode('utf-8'))

                print(f"Cliente ({nombre}) conectado desde {addr}")

               
            else:
                # Mensaje normal
                mensaje = datos.decode('utf-8').strip()
                nombre = clientes[socket]["nombre"]

                # Mostrar mensaje
                print(f"{nombre}: {mensaje}")

                # Broadcast a todos los demás
                for cliente_sock, cliente_nombre in clientes.items():
                    if cliente_sock != socket and cliente_nombre is not None:
                        cliente_sock.send(f"{nombre}: {mensaje}".encode('utf-8'))


        else:
            # Cliente se desconecta normalmente
            desconectar_cliente(socket)
            # Salir de la función para no usar sockets cerrados
            return  

    except ConnectionResetError:
        desconectar_cliente(socket)

# Variable de control
servidor_activo = True

# Diccionario para guardar info de clientes
clientes = {}

# Puerto determinado
PUERTO = 8000

# Selector para manejar múltiples sockets
sel = selectors.DefaultSelector()

# Hilo para manejar exclusivamente la entrada del servidor
hilo_consola = threading.Thread(target=leer_consola, daemon=True)
hilo_consola.start()

# Crear socket de servidor TCP por defecto
servidor = socket.socket()

# Indica IP y puerto donde escuchará
servidor.bind(("localhost", PUERTO))

# Habilita la escucha de clientes
servidor.listen()

# Modo no bloqueante, para que accept() o recv() no detengan todo el programa si no hay datos.
servidor.setblocking(False)  

print(f"Servidor escuchando en puerto {PUERTO}...")

# Registrar el socket del servidor para aceptar conexiones
sel.register(servidor, selectors.EVENT_READ, data='servidor')

try:
    # Bucle principal del servidor
    while servidor_activo:
        # Lista de sockets listos para algun evento (lectura/escritura)
        # timeout = None → espera indefinidamente hasta que al menos un socket esté listo.
        eventos = sel.select(timeout=1)

        # Iterar sobre los sockets que estan listos
        # info --> socket y dato extra
        # evento --> tipo de evento (lectura/escritura)
        for info, evento in eventos:
            if info.data == 'servidor':
                # Es el socket principal → aceptar nuevo cliente
                aceptar_conexion(info.fileobj)
            else:
                # Es un cliente existente → manejar mensaje
                manejar_cliente(info.fileobj)

# Si se aprieta ctrl + C
except KeyboardInterrupt:
    servidor_activo = False

# Cerrar el socket del servidor
servidor.close()

