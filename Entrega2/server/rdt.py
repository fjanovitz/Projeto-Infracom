from socket import *

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 5500
BUFFER_SIZE = 1024

class Rdt:
    
    def __init__(self, type : str, addrPort = SERVER_PORT, addrName = SERVER_ADDRESS):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.addrPort = addrPort
        self.addrName = addrName
        self.type = type
        self.sec_client = 0
        self.sec_server = 0
        
        # Para facilitar ambos tem a mesma porta com endereços diferentes.
        if(type == 'server'):
            self.socket.bind(("", addrPort))
    
    def __del__(self):
        self.socket.close()
    
    def close(self):
        self.__del__()
    
    def reset_num_seq(self):
        self.sec_client = 0
        self.sec_server = 0
    
    def send(self, data):
        # Se os dados não forem do tipo bytes, converte para bytes:
        if not isinstance(data, bytes):
            data = data.encode()  

        # Envio de dados usando o método sendto() do socket
        if self.type == 'client':
            self.socket.sendto(data, (self.addrName, self.addrPort))
        else:
            self.socket.sendto(data, self.addrName)
    
    def receive(self):
        # métodos recv() e recvfrom() do socket para receber os dados.
        if(self.type == 'client'):
            bytes_read = self.socket.recv(BUFFER_SIZE)
        else:
            bytes_read, self.addrName = self.socket.recvfrom(BUFFER_SIZE)
        return bytes_read
    
    def rdt_send(self, data):
        # Se os dados não forem do tipo bytes, converte para bytes:
        if not isinstance(data, bytes):
            data = data.encode()

        sum = checksum(data)
        payload = make_pkt(data, sum, self.sec_client)
        payload.encode()

        rcvpkt = None
        # Enquanto não houver recebido um pacote de confirmação válido: 
        while(not rcvpkt or corrupt(rcvpkt) or rcvpkt['num_seq'] != self.sec_client or not rcvpkt['is_ack']):
            # Inicia o timeout do socket e envia o pacote:
            self.socket.settimeout(1)
            self.send(payload)  
            print('Pacote enviado\n')

            try:
                print('Aguardando ACK...\n')
                # Tenta receber o ACK usando o método `rdt_rcv`
                rcvpkt = self.rdt_rcv('wait_ack')  
            except:
                print('Estouro do temporizador, reenviando arquivo')
                continue  # Em caso de timeout, continua o loop para reenviar o pacote de envio.
            else: 
                # Se não entrar no except, remove o timeout do socket:
                self.socket.settimeout(None)  
                print('Pacote recebido com sucesso\n')
                break

        self.sec_client = 1 - self.sec_client  # Atualiza o número de sequência para o próximo pacote a ser enviado

    
    def rdt_rcv(self, state: str = 'null'):
        # Ou ele espera um pacote ou espera um ACK
        if(state != 'wait_ack'):
            print('Aguardando pacotes...\n')

            rcvpkt = None 
            # Enquanto não houver recebido um pacote válido.
            while(not rcvpkt or corrupt(rcvpkt) or rcvpkt['num_seq'] != self.sec_server):
                rcvpkt = eval(self.receive().decode()) ## Decodifica os bytes
            print('O pacote foi recebido.\n')

            ack_data = make_ack(self.sec_server)  
            self.send(ack_data)  
            print('ACK enviado\n')

            # Atualiza o número de sequência para o próximo pacote a ser recebido
            self.sec_server = 1 - self.sec_server  
        else:
            print('Aguardando ACK\n')

            rcvpkt = None
            # Enquanto não houver recebido um pacote válido.
            while(not rcvpkt or corrupt(rcvpkt) or rcvpkt['num_seq'] != self.sec_client):
                rcvpkt = eval(self.receive().decode())  ## Decodifica os bytes
            print('ACK recebido.\n')

        # Retorna o pacote recebido (ou o pacote de confirmação recebido)
        return rcvpkt  

# A função foi criada para que o código fique semelhante a maquina de estados:
def make_pkt(data, checksum, num_seq):
    return str({
        'data': data,
        'checksum': checksum,
        'num_seq': num_seq,
        'is_ack': False
    })

# A função foi criada para que o código fique semelhante a maquina de estados:
def make_ack(num_seq):
    return str({
        'data': "ACK",
        'num_seq': num_seq,
        'checksum': checksum("ACK".encode()),
        'is_ack': True
    })

# A função foi criada para que o código fique semelhante a maquina de estados:
def corrupt(pkt):
    try:
        return pkt['checksum'] != checksum(pkt['data'])
    except:
        return pkt['checksum'] != checksum(pkt['data'].encode())

def checksum(data):
    addr = 0 
    sum = 0

    count = len(data)
    while (count > 1):
        sum += data[addr] << 8 + data[addr+1]
        addr += 2
        count -= 2
        
    if (count > 0):
        sum += data[addr]

    while (sum>>16):
        sum = (sum & 0xffff) + (sum >> 16)

    checksum = ~sum
    return checksum

