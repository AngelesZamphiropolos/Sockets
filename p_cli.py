'''import socket

# Crear socket
cliente = socket.socket()

# Conectar, recibe una tupla (direccion, puerto)
cliente.connect(("localhost", 8000))

while True:
    # Enviar mensaje al servidor
    mensaje = input("Tú: ")
    cliente.send(mensaje.encode('utf-8'))

    # Si escribes 'salir', se termina la conexión
    if mensaje.lower() == "salir":
        print("Cerrando conexión...")
        break

    # Esperar respuesta del servidor
    respuesta = cliente.recv(1024).decode('utf-8')

    # Si el servidor escribe 'salir', se termina
    if respuesta.lower() == "salir":
        print("El servidor cerró la conexión.")
        break

    print(f"Servidor: {respuesta}")

# Cerrar socket
cliente.close()
print("Cliente cerrado.")'''




import socket
import threading

def recibir(socket):
    while True:
        try:
            mensaje = socket.recv(1024).decode()
            print(mensaje)
        except:
            break

cliente = socket.socket()

cliente.connect(("localhost",8000))

hilo_recibir = threading.Thread(target=recibir,args=(cliente,),daemon=True)

while True:
    mensaje = input()
    cliente.send(mensaje.encode())

    if mensaje.lower() == 'salir':
        break

    
cliente.close()



