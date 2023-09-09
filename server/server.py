from rdt import *

BUFFER_SIZE = 1024

def main():
    # Conexão foi abstraída para a classe Rdt, que fornece uma conexão UDT com RDT3.0
    servidor = Rdt('server')

    while True:
        print('O servidor está pronto para receber arquivos')
        servidor.reset_num_seq()

        # Com intuito de criar o mesmo arquivo no servidor:
        filename = servidor.rdt_rcv()['data'].decode()

        # Para que evite erros (abrir o mesmo arquivo do cliente)
        filename = 'server_' + filename[0:]
        
        # Abrimos o arquivo para escrever os dados recebidos
        with open(filename, "wb") as file:
            while True:
                bytes_read = servidor.rdt_rcv()['data']
                if not bytes_read:
                    file.close()
                    break
                file.write(bytes_read)

        print("Dados recebidos pelo receptor")

        # Enviando o arquivo de volta para o cliente
        with(open(filename, "rb")) as file:
            while True:
                bytes_read = file.read(BUFFER_SIZE)
                servidor.rdt_send(bytes_read)
                if not bytes_read:
                    file.close()
                    break
        
        print(" O arquivo foi enviado para o receptor")

if __name__ == '__main__':
    main()