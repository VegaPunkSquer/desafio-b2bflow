import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# ---------------------------------------------------------
# SETUP DE CAMINHOS ABSOLUTOS
# ---------------------------------------------------------
# Pega o caminho absoluto da pasta atual (src/)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Volta um nível para a raiz do projeto (onde está o .env)
ROOT_DIR = os.path.dirname(CURRENT_DIR)
ENV_PATH = os.path.join(ROOT_DIR, ".env")

# Carrega as variáveis de ambiente
load_dotenv(ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")

# ---------------------------------------------------------
# FUNÇÕES DO FLUXO
# ---------------------------------------------------------
def buscar_contatos(supabase: Client) -> list:
    """Busca até 3 contatos cadastrados na tabela do Supabase."""
    print("🔍 Conectando ao Supabase para buscar contatos...")
    try:
        # A regra do desafio: "Envie para até 3 números diferentes"
        resposta = supabase.table("contatos").select("*").limit(3).execute()
        return resposta.data
    except Exception as e:
        print(f"❌ Erro catastrófico ao buscar no Supabase: {e}")
        return []

def enviar_mensagem_whatsapp(telefone: str, nome: str):
    """Dispara a mensagem via Z-API usando as credenciais do .env."""
    # A regra do desafio: enviar a mensagem EXATA: "Olá, <nome_contato> tudo bem com você?"
    mensagem = f"Olá, {nome} tudo bem com você?"
    
    # Endpoint padrão da Z-API para envio de texto
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
    
    payload = {
        "phone": telefone,
        "message": mensagem
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Lança exceção se o HTTP Status for de erro (ex: 400, 401, 500)
        print(f"✅ Z-API: Mensagem disparada com sucesso para {nome} ({telefone}).")
    except requests.exceptions.RequestException as e:
        print(f"❌ Z-API: Erro ao enviar mensagem para {nome} ({telefone}): {e}")

# ---------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ---------------------------------------------------------
def main():
    print("🚀 Iniciando automação b2bflow...")
    
    # Validação inicial de ambiente
    if not all([SUPABASE_URL, SUPABASE_KEY, ZAPI_INSTANCE_ID, ZAPI_TOKEN]):
        print("❌ Erro: Alguma variável de ambiente está faltando no seu .env!")
        return

    # Inicializa o cliente do Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Puxa os dados
    contatos = buscar_contatos(supabase)
    
    if not contatos:
        print("⚠️ Nenhum contato encontrado na tabela ou houve um erro. Abortando missão.")
        return
        
    print(f"🎯 {len(contatos)} contato(s) encontrado(s). Iniciando os disparos...")
    
    # 2. Varre a lista e envia as mensagens
    for contato in contatos:
        telefone = contato.get("telefone")
        nome = contato.get("nome_contato")
        
        if telefone and nome:
            enviar_mensagem_whatsapp(telefone, nome)
        else:
            print(f"⚠️ Contato ignorado por falta de dados (telefone ou nome em branco): {contato}")
            
    print("🎉 Fluxo finalizado de ponta a ponta!")

if __name__ == "__main__":
    main()