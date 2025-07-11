# Gerador de Relatório de Disponibilidade Zabbix

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Uma ferramenta de desktop com interface gráfica para gerar relatórios de disponibilidade de ativos monitorados pelo Zabbix. A aplicação se conecta à API do Zabbix, coleta dados de um grupo de hosts específico e gera um relatório profissional em formato PDF.

## Funcionalidades

* **Conexão com Zabbix:** Se conecta a qualquer instância do Zabbix via API para buscar dados em tempo real.
* **Seleção de Parâmetros:** Permite definir o grupo de hosts e o período (em dias) para a análise.
* **Geração de PDF Formatado:** Cria um relatório em PDF com layout profissional, incluindo:
    * Cabeçalho com título e data de geração.
    * Tabela com os dados de disponibilidade.
    * Cores condicionais para identificar rapidamente ativos com baixa disponibilidade (verde, amarelo, vermelho).
    * Paginação automática.
* **Multiplataforma:** Por ser feito em Python, pode rodar em Windows, macOS e Linux (com as dependências corretas).

## Tecnologias Utilizadas

* **Python 3.9+**
* **CustomTkinter:** Para a construção da interface gráfica moderna.
* **pyzabbix:** Para a comunicação com a API do Zabbix.
* **Pandas:** Para a manipulação e estruturação dos dados.
* **WeasyPrint:** Para a conversão do relatório (HTML + CSS) para PDF.

## Pré-requisitos

Antes de começar, garanta que você tem os seguintes pré-requisitos:

1.  **Python 3.9 ou superior** instalado.
2.  **(Apenas para Windows)** A aplicação requer o **GTK3 Runtime** para que o WeasyPrint possa renderizar os PDFs. Se você não o tiver, a aplicação apresentará um erro.
    * Faça o download a partir do [instalador oficial do GTK3 para Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) e siga as instruções de instalação.
    * **Lembre-se de adicionar o GTK ao PATH do sistema**, como explicado anteriormente.

## Instalação

Siga os passos abaixo para configurar o ambiente e rodar o projeto:

1.  **Clone ou baixe este repositório:**
    ```bash
    git clone https://github.com/SchiavonNathan/gerador-relatorio-zabbix.git
    cd gerador-relatorio-zabbix
    ```
    Ou simplesmente baixe os arquivos `.py` e `requirements.txt` para a mesma pasta.

2.  **Crie e ative um ambiente virtual (Recomendado):**
    ```bash
    # Cria o ambiente virtual
    python -m venv venv

    # Ativa o ambiente no Windows
    .\venv\Scripts\activate

    # Ativa o ambiente no Linux/macOS
    source venv/bin/activate
    ```

3.  **Instale as dependências Python:**
    Use o arquivo `requirements.txt` para instalar todas as bibliotecas necessárias de uma só vez.
    ```bash
    pip install -r requirements.txt
    ```

## Como Usar

Com o ambiente configurado, execute o script principal para abrir a interface gráfica:

```bash
python main.py
```

1. Preencha os campos na interface com os dados do seu ambiente Zabbix (URL, usuário, senha).
2. Informe o nome exato do Grupo de Hosts que deseja analisar.
3. Defina o período do relatório em dias (o padrão é 30).
4. Clique no botão "Gerar Relatório PDF".
5. Uma caixa de diálogo será aberta para você escolher o nome e o local onde deseja salvar o arquivo PDF.
6. Acompanhe o progresso na caixa de log na parte inferior da janela.

Este projeto está licenciado sob a Licença MIT.

## Créditos

Desenvolvido por Nathan Schiavon
