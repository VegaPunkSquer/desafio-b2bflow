# Desafio b2bflow: Automação de Disparo Z-API

Automação desenvolvida em Python para buscar contatos cadastrados em um banco de dados Supabase e disparar mensagens personalizadas via WhatsApp utilizando a Z-API.

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **Supabase** (Banco de dados e API)
* **Z-API** (Integração WhatsApp)
* **uv** (Gerenciador de dependências)
* **Rich** (Interface interativa no terminal)

## 🗄️ Setup da Tabela (Supabase)

Foi criada uma tabela chamada `contatos` com a seguinte estrutura:

* `id` (int8, chave primária)
* `created_at` (timestamptz)
* `nome_contato` (text)
* `telefone` (text) - Formato internacional sem formatação

Nota: A tabela possui uma política RLS habilitada para permitir operações de SELECT.

## 🔐 Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto contendo as seguintes credenciais:

SUPABASE_URL="sua_url_publica_aqui"
SUPABASE_KEY="sua_chave_anon_public_aqui"
ZAPI_INSTANCE_ID="id_da_sua_instancia"
ZAPI_TOKEN="seu_token_aqui"

## 🚀 Como Rodar o Projeto

1. Clone o repositório.
2. Certifique-se de ter o uv instalado.
3. Sincronize o ambiente com o comando: uv sync
4. Execute o script principal com o comando: uv run src/main.py

O script abrirá uma interface interativa no terminal para escolha dos contatos e personalização da mensagem antes do disparo.
