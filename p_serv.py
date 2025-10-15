'''
# importar modulo socket para crear conexiones de red
import socket


# Crear un socket
servidor = socket.socket()

# Establecer conexion, recibe 2 parametros (host, puerto)
servidor.bind(("localhost", 8000))

# Establecer cantidad de peticiones en cola que podra manejar antes de rechazar
servidor.listen(1)

print("Servidor esperando conexión...")

# Ciclo inf. para aceptar peticiones
while True:
    # Aceptar conexión, devuelve 2 valores (conexion, direccion)
    conexion, addr = servidor.accept()
    print("Cliente conectado desde:", addr)

    # Obtener lo que el cliente envia
    mensaje_cliente = conexion.recv(1024).decode('utf-8')

    # Si el cliente escribe 'salir', se corta la conexión
    if mensaje_cliente.lower() == "salir":
        print("El cliente cerró la conexión.")
        break

    print(f"Cliente: {mensaje_cliente}")

    # Enviar mensaje al cliente
    mensaje_servidor = input("Tú: ")
    conexion.send(mensaje_servidor.encode('utf-8'))

    # Si el servidor escribe 'salir', también se corta
    if mensaje_servidor.lower() == "salir":
        print("Cerrando conexión con el cliente...")
        break


# Cerrar conexion con el cliente y socket
conexion.close()
servidor.close()
print("Servidor cerrado.")

'''

import socket
import selectors

servidor = socket.socket()

servidor.bind(("localhost",8000))

servidor.listen()

sel = selectors.DefaultSelector()

servidor.setblocking(False)

sel.register(servidor,selectors.EVENT_READ,'servidor')

print("Servidor activo...")

clientes = []
try:
    while True:
        sockets_listos = sel.select(timeout=1)
        for info, evento in sockets_listos:
            if info.data == 'servidor':
                cliente, direc = servidor.accept()
                
                cliente.setblocking(False)

                sel.register(cliente,selectors.EVENT_READ,data=direc)

                clientes.append(cliente)
            else:
                mensaje = info.fileobj.recv(1024).decode()
                if mensaje:
                    for cliente in clientes:
                        if cliente != info.fileobj:
                            servidor.send(f"{mensaje}".encode())
                else:
                    print(f"{direc} se desconectó")
                    sel.unregister(info.fileobj)
                    info.fileobj.close()
                    clientes.remove(info.fileobj)

except KeyboardInterrupt:
    print ("Servidor cerrado...")





