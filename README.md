# 2º entrega do projeto de Infraestrutura de Comunicações (Transmissão Confiável)
Este projeto implementa um sistema de transmissão confiável, baseado no RDT 3.0 (Receptor-Transmissor de Dados) apresentado na disciplina. O projeto é dedicado à segunda entrega da do trabalho e visa demonstrar a eficiência do RDT 3.0 implementado, incluindo a capacidade de lidar com perdas de pacotes aleatórios.

## Funcionamento 
O cliente solicita o arquivo que deseja enviar, verifica sua existência, estabelece uma conexão com o servidor via RDT 3.0 e envia o arquivo em blocos confiáveis. O servidor, por sua vez, recebe o arquivo, evita erros de nome de arquivo, escreve os dados recebidos e reenvia o arquivo de volta ao cliente, tudo isso mantendo a confiabilidade por meio do protocolo RDT 3.0

## Requisitos
Python 3.7 ou superior

## Funcionamento do projeto

1. Comece abrindo duas abas separadas no PowerShell.
2. Na primeira aba, navegue até o diretório onde o servidor está localizado e execute o comando `py server.py`.
3. Na segunda aba, vá para o diretório onde o cliente está localizado e execute o comando `py client.py`.
4. Quando você executar o `client.py`, o programa solicitará que você forneça o nome do arquivo de onde deseja obter informações. Digite o nome do arquivo desejado, por exemplo, "teste.txt" (sem as aspas e incluindo a extensão .txt).

## Testando a eficiência
Para testar a eficiência do RDT 3.0 implementado, um gerador de perdas de pacotes aleatórios foi incorporado. Isso resultará em timeouts no transmissor para pacotes perdidos, demonstrando como o protocolo lida com esse tipo de situação.

### Equipe
- Frederico Janovitz Novais
- Gabriel Pierre Carvalho Coelho
- Gustavo Santana de Almeida
- Klarissa de Andrade Morais
- Leandro Luiz de Lima Freitas
- Mateus Galdino de Lima Guilherme 