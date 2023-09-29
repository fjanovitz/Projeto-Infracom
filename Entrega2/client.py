import os
from server.rdt import *

BUFFER_SIZE = 1024

def main():
    filename = input("Escreva o nome e tipo do arquivo que deseja enviar (por exemplo: teste.txt):")
    # Conexão foi abstraída para a classe Rdt, que fornece uma conexão UDT com RDT3.0
    client = Rdt('client')

    if os.path.exists(filename): # Verificar se o arquivo existe

        # Enviar o nome do arquivo para que o servidor escreva igual.
        client.rdt_send(filename)
        
        # Enviar o arquivo para o servidor
        with(open(filename, "rb")) as file:
            data = file.read()

        # Particionar e enviar o os chunks do arquivo
            for i in range(0, len(data), BUFFER_SIZE):
                chunk = data[i:i+BUFFER_SIZE]
                client.rdt_send(chunk)
            
            # Enviando o último bloco
            client.rdt_send(b'')
        
        print('Os blocos de arquivo foram enviados para o servidor')
    
        filename = 'file_received.txt' # Arquivo enviado pelo servidor

        data = bytearray()
        while True:
            chunk = client.rdt_rcv()['data']
            if not chunk:   # Se não houver mais dados para receber, sair do loop
                break
            data += chunk   # Adicionando o chunk ao arquivo

        with open(filename, "wb") as newFile:
            newFile.write(data)
            newFile.close()

        print("Os blocos de arquivo foram recebidos pelo servidor")
        
    else:
        print("Por favor, insira o arquivo que se deseja enviar no diretório do cliente")
    

if __name__ == '__main__':
    while True:
        main()