# Desafio b2bflow: Automação de Disparo Z-API

Automação desenvolvida em Python para buscar contatos cadastrados em um banco de dados Supabase e disparar mensagens personalizadas via WhatsApp utilizando a Z-API.

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **Supabase** (Banco de dados e API)
* **Z-API** (Integração WhatsApp)
* **uv** (Gerenciador de dependências ultrarrápido)
* **Rich** (Interface interativa no terminal)

## 🗄️ Setup da Tabela (Supabase)

Foi criada uma tabela chamada `contatos` com a seguinte estrutura:

* `id` (int8, chave primária)
* `created_at` (timestamptz)
* `nome_contato` (text) - *Ex: João*
* `telefone` (text) - *Ex: 5511999999999 (formato internacional sem formatação)*

*Nota: A tabela possui uma política RLS (Row Level Security) habilitada para permitir operações de SELECT (leitura).*

## 🔐 Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto contendo as seguintes credenciais:

```env
# SUPABASE
SUPABASE_URL="sua_url_publica_aqui"
SUPABASE_KEY="sua_chave_anon_public_aqui"

# Z-API
ZAPI_INSTANCE_ID="id_da_sua_instancia"
ZAPI_TOKEN="seu_token_aqui"
