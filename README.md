### 2º entrega do projeto de Infraestrutura de Comunicações (Transmissão Confiável)
Este projeto implementa um sistema de transmissão confiável, baseado no RDT 3.0 (Receptor-Transmissor de Dados) apresentado na disciplina. O projeto é dedicado à segunda entrega da do trabalho e visa demonstrar a eficiência do RDT 3.0 implementado, incluindo a capacidade de lidar com perdas de pacotes aleatórios.

# Requisitos
Python 3.7 ou superior

## Funcionamento do projeto

1. Comece abrindo duas abas separadas no PowerShell.
2. Na primeira aba, navegue até o diretório onde o servidor está localizado e execute o comando `py server.py`.
3. Na segunda aba, vá para o diretório onde o cliente está localizado e execute o comando `py client.py`.
4. Quando você executar o `client.py`, o programa solicitará que você forneça o nome do arquivo de onde deseja obter informações. Digite o nome do arquivo desejado, por exemplo, "teste.txt" (sem as aspas e incluindo a extensão .txt).

## Testando a Eficiência
Para testar a eficiência do RDT 3.0 implementado, um gerador de perdas de pacotes aleatórios foi incorporado. Isso resultará em timeouts no transmissor para pacotes perdidos, demonstrando como o protocolo lida com esse tipo de situação.

# Equipe
- Frederico Janovitz Novais
- Gabriel Pierre Carvalho Coelho
- Gustavo Santana de Almeida
- Klarissa de Andrade Morais
- Leandro Luiz de Lima Freitas
- Mateus Galdino de Lima Guilherme 