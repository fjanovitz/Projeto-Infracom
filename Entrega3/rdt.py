from socket import *
from utils import checksum, getTime
import threading
import time

class RDTServer:
    # Configurações do servidor
    def __init__(self, addressPort=("127.0.0.1", 20001), bufferSize=1024):
        self.timeout = 0.1
        self.sender_addr = 0
        self.addressPort =  addressPort
        self.bufferSize = bufferSize
        self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
        self.UDPSocket.bind(self.addressPort)
        self.UDPSocket.settimeout(self.timeout)
        self.lista_usuarios = []    # Lista de todos os usuários ativos no servidor
        self.lista_banidos = []     # Lista de usuários banidos no servidor
        self.lista_seq = {}
        self.lista_amigos = {}  # Dicionário para listar os amigos de cada usuário
        self.ban_votes = {}     # Dicionário para rastrear os votos
        self.ban_target = None  # Nome do usuário que pode ser banido
        print("O servidor está ativo")
        self.run()

    # Função de espera, onde o servidor aguarda de prontidão para receber mensagens
    def run(self):
        while(1):
            print("Aguardando mensagens")
            data, sender_addr = self.receive()
            print("Mensagem recebida")
            if data != "" :
                self.print_message(data, sender_addr)
            
    # Função para exibir mensagens na tela
    def print_message(self, data, sender_addr):
        word = data.strip() # Remove espaços
        if word == 'bye':   # Usuário deseja sair do chat
            for x in self.lista_usuarios:
                if x[0] == sender_addr:
                    message = f"{getTime()} -> == {x[1]} saiu do chat =="
                    self.broadcast_message(message)
                    self.lista_usuarios.remove((x[0], x[1]))
                    self.lista_seq.pop(x[0])
                    
        elif word == 'list':    # Exibe a lista de pessoas no chat
            data = 'Pessoas no chat:\n'
            for x in self.lista_usuarios:
                data += x[1] + '\n'
            self.broadcast_message(data)
            
        elif word.startswith('addtomylist'):    # Adiciona um usuário como amigo
            _, nome_amigo = word.split()
            if sender_addr not in self.lista_amigos:
                self.lista_amigos[sender_addr] = []
            self.lista_amigos[sender_addr].append(nome_amigo)
            data = f"{nome_amigo} adicionado à lista de amigos."
            self.send_pkg(data, sender_addr)

        elif word.startswith('removefrommylist'):   # Remove um amigo da lista de amigos do usuário
            _, nome_amigo = word.split()
            if sender_addr in self.lista_amigos:
                try:
                    self.lista_amigos[sender_addr].remove(nome_amigo)
                    data = f"{nome_amigo} removido da lista de amigos."
                except ValueError:
                    data = f"{nome_amigo} não encontrado na lista de amigos."
            else:
                data = "Você ainda não tem amigos na lista."
            self.send_pkg(data, sender_addr)
        
        elif word == 'mylist':  # Exibe lista de amigos do usuário
            if sender_addr in self.lista_amigos:
                amigos = ', '.join(self.lista_amigos[sender_addr])
                if amigos:
                    data = f"Seus amigos são:\n{amigos}."
                else:
                    data = "Você não tem amigos na lista."
            else:
                data = "Você ainda não tem amigos na lista."
            self.send_pkg(data, sender_addr)
        
        elif word.startswith('ban'):
            _, target = word.split()
            if self.ban_target is None:
                self.ban_target = target
                self.ban_votes = {}
            
            # Verifique se o comando 'ban' é para o mesmo alvo
            if self.ban_target == target:
                self.ban_votes[sender_addr] = True
                num_votes = len(self.ban_votes)
                num_clients = len(self.lista_usuarios)
                threshold = num_clients // 2 + 1  # Mais da metade dos clientes
                
                # Enviar a atualização para todos os clientes
                for client_addr, client_name in self.lista_usuarios:
                    self.send_pkg(f"[ {target} ] ban {num_votes}/{threshold}", client_addr)
                
                # Verificar se o alvo deve ser banido
                if num_votes >= threshold:
                    self.kick_out(self.ban_target)
                    self.ban_target = None
                    self.ban_votes = {}
            
        else:
            nome = ""
            for x in self.lista_usuarios:
                if x[0] == sender_addr:
                    nome = x[1]
            self.custom_broadcast_message(data, nome, sender_addr)

    def custom_broadcast_message(self, message, sender_name, sender_addr):
        for client_addr, client_name in self.lista_usuarios:
            tag = ""
            if client_addr in self.lista_amigos and sender_name in self.lista_amigos[client_addr]:
                tag = "[amigo] "
            
            custom_message = f"{getTime()} -> {tag}{sender_name}: {message}"
            self.send_pkg(custom_message, client_addr)
    
    def broadcast_message(self, data):
        for x in self.lista_usuarios:
            self.send_pkg(data, x[0])
    
    def kick_out(self, target):
        # Encontre o endereço e o nome correspondente ao nome de usuário 'target'
        target_addr = None
        for addr, username in self.lista_usuarios:
            if username == target:
                target_addr = addr
                break

        if target_addr is not None:
            # Informe a todos os outros clientes que o usuário será banido
            for addr, _ in self.lista_usuarios:
                self.send_pkg(f"{target} foi banido.", addr)
                
            # Remova o usuário da lista de usuários e outras estruturas de dados
            if target_addr in self.lista_seq:
                del self.lista_seq[target_addr]
            if target_addr in self.lista_amigos:
                del self.lista_amigos[target_addr]
            for x in self.lista_usuarios:
                if x[0] == target_addr:
                    self.lista_usuarios.remove((x[0], x[1]))
                    self.lista_seq.pop(x[0])
        else:
            # O usuário 'target' não foi encontrado
            print(f"Usuário {target} não encontrado.")

    def send(self, data, sender_addr):
        self.UDPSocket.sendto(data, sender_addr)

    #Função para envio de pacotes
    def send_pkg(self, data, sender_addr):
        data = self.create_header(data, sender_addr)
        ack = False
        self.UDPSocket.settimeout(self.timeout)
        rcv_addr = 0
        while not ack:
            self.send(data, sender_addr)
            try:
                data, rcv_addr = self.UDPSocket.recvfrom(self.bufferSize)
            except timeout: # Ocorrência do estouro do temporizador
                print("Estouro do temporizador, reenviando pacote")
            else:
                ack = self.rcv_ack(data, sender_addr)

        self.UDPSocket.settimeout(None)

    #Função que realiza a conexão entre o cliente e o servidor
    def new_connection(self, nome, sender_addr):
        self.lista_usuarios.append((sender_addr, nome))
        self.lista_seq.update({sender_addr: 0})

    # Avisa aos outros usuários que um novo usuário entrou no chat
    def broadcast_new_user(self, nome):
        data = nome + " entrou na sala"
        for x in self.lista_usuarios:
            #print(x)
            self.send_pkg(data, x[0])

    # Função que recebe o pacote
    def receive(self):
        self.UDPSocket.settimeout(None)
        #print("Receveing package")
        data, sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
        self.UDPSocket.settimeout(self.timeout)
        #print("pkg received")
        data = self.rcv_pkg(data, sender_addr)
        #print("Received")
        return data, sender_addr

    # Função que envia ACKs e NACKs
    def send_ack(self, ack, sender_addr):
        if ack:
            #print("Sending ACK")
            data = self.create_header("ACK", sender_addr)
        else:
            #print("Sending NACK")
            data = self.create_header("NACK", sender_addr)
        self.send(data, sender_addr)

    #Função que decodifica o pacote recebido e checa se é uma nova conexão ou não
    def rcv_pkg(self, data, sender_addr):
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']
        print(data)
        try:
            x, y = payload.split()
        except:
            print("Not a new connection")           
        else:
            if(x == "new_connection"):
                print("new_connection")
                if self.checksum_(checksum, payload):
                    self.new_connection(y, sender_addr)
                    self.send_ack(1, sender_addr)
                    self.lista_seq.update({sender_addr: 1})
                    self.broadcast_new_user(y)
                    return ""
                else:
                    self.send_ack(0, sender_addr)
                    return ""
        if(self.lista_seq.get(sender_addr) != None):
            print(self.lista_seq)
            seq = self.lista_seq.get(sender_addr)
        else:
            self.send_ack(0, sender_addr)
            return ""
        if self.checksum_(checksum, payload) and seq_num == seq:
            self.send_ack(1, sender_addr)
            #print(self.lista_seq)
            self.lista_seq.pop(sender_addr)
            self.lista_seq.update({sender_addr: (1-seq)})
            #print(self.lista_seq)
            return payload
        else:
            self.send_ack(0, sender_addr)
            return ""
    

    def rcv_ack(self, data, sender_addr):
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']
        if(self.lista_seq.get(sender_addr) != None):
            seq = self.lista_seq.get(sender_addr)
        else:
            return False
        if self.checksum_(checksum, payload) and seq_num == seq and payload == "ACK":
            self.lista_seq.update({sender_addr: 1-seq})
            return True
        else:
            return False

    def checksum_(self, chcksum, payload):
        if checksum(payload) == chcksum:
            return True
        else:
            return False

    def create_header(self, data, sender_addr):
        chcksum = checksum(data)
        seq = self.lista_seq.get(sender_addr)
        return str({
            'seq': seq,
            'checksum': chcksum,
            'payload' : data
        }).encode()

    def close_connection(self):
        print("Closing socket")
        self.UDPSocket.close()

class RDTClient:

    # Configuração do cliente
    def __init__(self, isServer = 0, addressPort = ("127.0.0.1", 20001), bufferSize = 1024):
        self.sender_addr = 0
        self.timeout = 0.1
        self.endFlag = False
        self.addressPort =  addressPort
        self.bufferSize = bufferSize
        self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
        self.isServer = isServer
        self.seq_num = 0
        self.lista_amigos = []
        self.UDPSocket.settimeout(self.timeout)
        print("Digite alguma coisa:")
        aux = input().split('hi, meu nome eh')
        # hi, meu nome eh <nome do usuario>
        while len(aux[0]):
            # loop até botar o comando
            aux = input().split('hi, meu nome eh')
        self.nome = aux[1].strip()
        print("-------- CHAT --------")
        self.lock = threading.Lock()
        data = "new_connection " + self.nome
        self.send_pkg(data.encode())
        self.run()
    
    def send(self, data):
        #print("Sending to server")
        self.UDPSocket.sendto(data, self.addressPort)

    def send_pkg(self, data):
        data = self.create_header(data.decode())
        ack = False
        self.UDPSocket.settimeout(self.timeout)
        while not ack:
            self.send(data)

            try:
                data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
            except timeout:
                #print("Did not receive ACK. Sending again.")
                z = 1
            else:
                ack = self.rcv_ack(data)

    def thread_input(self):
        #print("Thread input started")
        while(1):
            entrada = input()
            print("==============================")
            #print("Entrada: ", entrada)
            self.lock.acquire()
            #print("Thread input locked\nEnviando para o servidor: ")
            self.send_pkg(entrada.encode())
            self.lock.release()
            if entrada.strip() == 'bye':
                self.endFlag = True
                break
            #print("Thread input unlocked")
            

    def thread_rcv(self):
        #print("Thread rcv started")
        self.UDPSocket.settimeout(self.timeout)
        while(1):
            if self.endFlag:
                break
            try:
                self.lock.acquire()
                #print("Thread rcv locked")
                data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
            except timeout:
                #print("Did not receive input for 2 sec, giving space to send msg")
                z = 1
            else:
                data = self.rcv_pkg(data)
                print(data)
            self.lock.release()
            time.sleep(0.1)
            #print("Thread rcv unlocked")
            
            
            
    def run(self):
        entrada = ""
        th1 = threading.Thread(target=self.thread_input)
        th2 = threading.Thread(target=self.thread_rcv)
        th1.start()
        th2.start()
        th1.join()
        th2.join()
        while True:
            if self.endFlag:
                self.close_connection()
                break


    def receive(self):
        #print("Receveing package")
        data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
        data = self.rcv_pkg(data)

        #print("Received")
        return data.encode()

    def send_ack(self, ack):
        if ack:
            data = self.create_header("ACK")
        else:
            data = self.create_header("NACK")
        self.send(data)


    def rcv_pkg(self, data):
        
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']

        #print("rck_pkg: ")
        #print(data)

        if self.checksum_(checksum, payload) and seq_num == self.seq_num:
            self.send_ack(1)
            self.seq_num = 1 - self.seq_num
            return payload
        else:
            self.send_ack(0)
            return ""
    

    def rcv_ack(self, data):
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']

        #print("rck_ack: ")
        #print(data)
        
        
        if self.checksum_(checksum, payload) and seq_num == self.seq_num and payload == "ACK":
            self.seq_num = 1 - self.seq_num
            return True
        else:
            return False


    def checksum_(self, chcksum, payload):
        if checksum(payload) == chcksum:
            return True
        else:
            return False


    def create_header(self, data):

        chcksum = checksum(data)

        return str({
            'seq': self.seq_num,
            'checksum': chcksum,
            'payload' : data
        }).encode()

    def close_connection(self):
        print("Closing socket")
        self.UDPSocket.close()