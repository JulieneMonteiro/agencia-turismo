# 🌴 Agência de Turismo - Connections Viagens

Sistema de gerenciamento para uma agência de turismo local, com foco em destinos do estado do Rio de Janeiro. O sistema permite o cadastro de destinos turísticos, controle de vendas e geração de relatórios em PDF com detalhes das viagens e vendas realizadas.

## 🧭 Funcionalidades

- ✅ Cadastro de destinos turísticos:
  - Nome do destino
  - Descrição
  - Quantidade de vagas
  - Data da viagem

- 💳 Registro de vendas:
  - Nome e telefone do cliente
  - Seleção do pacote (destino)
  - Forma de pagamento
  - Atualização automática da quantidade de vagas disponíveis

- 📄 Geração de relatório em PDF:
  - Lista de vendas realizadas com dados dos clientes e pacotes adquiridos
  - Relatório de destinos com número de vagas restantes
  - Total arrecadado nas vendas

## 🛠️ Tecnologias Utilizadas

- Python 3
- PyQt6 (interface gráfica)
- Qt Designer (criação de layout .ui)
- MySQL (banco de dados)
- FPDF (geração de relatórios em PDF)

## 🖥️ Interface do Usuário

A interface é dividida em duas abas principais:

1. **Destinos**: Cadastro e visualização de pacotes turísticos.
2. **Vendas**: Registro das vendas de pacotes para clientes.

## 🚀 Como Executar o Projeto

1. Clone o repositório:
   ```bash
   git clone https://github.com/JulieneMonteiro/agencia-turismo.git

2. Instale os pacotes necessários:
   ```bash
   pip install PyQt6 mysql-connector-python fpdf

3. Configure seu banco de dados MySQL com a estrutura fornecida no arquivo banco.sql.

4. Execute o sistema:
   ```bash
   python main.py
## 🗂️ Estrutura do Projeto
    ```csharp
       agencia-turismo/
    ├── main.py
    ├── interface.ui
    ├── conexao.py
    ├── destinos.py
    ├── vendas.py
    ├── relatorio.py
    ├── imagens/
    │   └── logo.png
    ├── banco.sql
    └── README.md

## ✍️ Autor
  Juliene Monteiro
📧 [julienemonteiro83@gmail.com]
🔗 linkedin.com/in/julienemonteiro
