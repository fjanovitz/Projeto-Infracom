import os
from server.rdt import *

BUFFER_SIZE = 1024

def main():
    file_name = input("Escreva o nome e tipo do arquivo que deseja enviar (test_file.txt):")
    # Conexão foi abstraída para a classe Rdt
    client = Rdt('client')
    # No qual fornece uma conexão UDT com os príncipios de RDT3.0

    if os.path.exists(file_name): # Verificar se o arquivo existe

        # Enviar o nome do arquivo para que o servidor escreva igual.
        client.rdt_send(file_name)
        
        # Enviar o arquivo para o servidor
        with(open(file_name, "rb")) as file:
            data = file.read()

            for i in range(0, len(data), BUFFER_SIZE):
                # Enviando parte a parte até finalizar o arquivo
                chunk = data[i:i+BUFFER_SIZE]
                client.rdt_send(chunk)
            
            # Enviando o último bloco
            client.rdt_send(b'')
            
        print('Blocos de arquivo enviados para o servidor')
        
        # Receber o arquivo do servidor
        file_name = 'file_received.txt'

        data = bytearray()
        while True:
            chunk = client.rdt_rcv()['data']
            # Se não houver mais dados para receber, sair do loop
            if not chunk:
                break
            data += chunk # Adicionando o chunk ao arquivo

        with open(file_name, "wb") as newFile:
            newFile.write(data)
            newFile.close()

        print("Blocos recebidos pelo servidor")
        
    else:
        print("Crie o arquivo e põe no diretório do cliente!")
    

if __name__ == '__main__':
    while True:
        main()