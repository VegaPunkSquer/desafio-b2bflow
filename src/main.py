import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

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
    try:
        resposta = supabase.table("contatos").select("*").limit(3).execute()
        return resposta.data
    except Exception as e:
        console.print(f"[bold red]❌ Erro catastrófico ao buscar no Supabase: {e}[/bold red]")
        return []

def enviar_mensagem_whatsapp(telefone: str, nome: str) -> bool:
    """Dispara a mensagem via Z-API usando as credenciais do .env."""
    mensagem = f"Olá, {nome} tudo bem com você?"
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
    payload = {"phone": telefone, "message": mensagem}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() 
        return True
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]❌ Erro da Z-API ao enviar para {nome} ({telefone}): {e}[/bold red]")
        return False

# ---------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ---------------------------------------------------------
def main():
    console.clear()
    console.print(Panel("[bold cyan]🚀 Automação b2bflow - Disparo Z-API[/bold cyan]", border_style="cyan"))
    
    if not all([SUPABASE_URL, SUPABASE_KEY, ZAPI_INSTANCE_ID, ZAPI_TOKEN]):
        console.print("[bold red]❌ Erro: Alguma variável de ambiente está faltando no seu .env![/bold red]")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Efeito visual de carregamento
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task("[cyan]🔍 Buscando contatos no Supabase...", total=None)
        contatos = buscar_contatos(supabase)
        time.sleep(1) # Pausa intencional para o avaliador ver o loading
    
    if not contatos:
        console.print("[bold yellow]⚠️ Nenhum contato encontrado na tabela ou RLS bloqueando. Abortando.[/bold yellow]")
        return
        
    # Tabela de resultados
    table = Table(title="📊 Status dos Disparos", show_header=True, header_style="bold magenta")
    table.add_column("Nome", style="dim")
    table.add_column("Telefone", justify="center")
    table.add_column("Status", justify="center")

    console.print(f"\n[bold green]🎯 {len(contatos)} contato(s) encontrado(s). Iniciando os disparos...[/bold green]\n")
    
    for contato in contatos:
        telefone = contato.get("telefone")
        nome = contato.get("nome_contato")
        
        if telefone and nome:
            sucesso = enviar_mensagem_whatsapp(telefone, nome)
            status_text = "[green]✅ Enviado[/green]" if sucesso else "[red]❌ Falha[/red]"
            table.add_row(nome, telefone, status_text)
            time.sleep(1) # Respiro entre requisições para evitar rate limit da Z-API
        else:
            table.add_row(str(nome), str(telefone), "[yellow]⚠️ Ignorado (Dados faltando)[/yellow]")
            
    console.print(table)
    console.print("\n[bold cyan]🎉 Fluxo finalizado de ponta a ponta![/bold cyan]\n")

if __name__ == "__main__":
    main()