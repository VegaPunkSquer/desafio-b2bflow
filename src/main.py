import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from rich.prompt import Prompt

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

def enviar_mensagem_whatsapp(telefone: str, nome: str, mensagem: str) -> bool:
    """Dispara a mensagem via Z-API usando as credenciais do .env."""
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
        time.sleep(1) # Pausa intencional
    
    if not contatos:
        console.print("[bold yellow]⚠️ Nenhum contato encontrado na tabela ou RLS bloqueando. Abortando.[/bold yellow]")
        return
        
    # 1. Filtra os contatos zoados (ignora os que tem nome ou telefone vazios)
    contatos_validos = [c for c in contatos if c.get("nome_contato") and c.get("telefone")]

    if not contatos_validos:
        console.print("[bold yellow]⚠️ Só tinha contato com dados faltando. Abortando.[/bold yellow]")
        return

    console.print(f"\n[bold green]🎯 {len(contatos_validos)} contato(s) válido(s) encontrado(s).[/bold green]\n")

    # 2. UX TOP: Escolha de contato
    console.print("[0] 🚀 Enviar para TODOS")
    for i, contato in enumerate(contatos_validos, 1):
        console.print(f"[{i}] {contato['nome_contato']} - {contato['telefone']}")
        
    escolha = Prompt.ask("\n[cyan]Digite os números (ex: 1,3 para múltiplos, ou 0 para todos)[/cyan]")
    
    try:
        if escolha.strip() == '0':
            selecionados = contatos_validos
        else:
            # Pega os índices, separa por vírgula, converte pra int e ajusta para a lista (subtrai 1)
            indices = [int(x.strip()) - 1 for x in escolha.split(',')]
            selecionados = [contatos_validos[i] for i in indices if 0 <= i < len(contatos_validos)]
    except (ValueError, IndexError):
        console.print("[bold red]❌ Opção inválida. Digite apenas números correspondentes. Abortando.[/bold red]")
        return

    # 3. UX TOP: Edição da mensagem (com a padrão da vaga como default)
    console.print("\n[dim]A mensagem padrão exigida pela vaga é: 'Olá, {nome} tudo bem com você?'[/dim]")
    msg_base = Prompt.ask("[cyan]Digite a nova mensagem (use {nome} para personalizar), ou aperte ENTER para a padrão[/cyan]", default="Olá, {nome} tudo bem com você?")

    # Tabela de resultados
    table = Table(title="📊 Status dos Disparos", show_header=True, header_style="bold magenta")
    table.add_column("Nome", style="dim")
    table.add_column("Telefone", justify="center")
    table.add_column("Status", justify="center")
    
    console.print("\n[bold green]🚀 Iniciando disparos...[/bold green]\n")

    for contato in selecionados:
        telefone = contato["telefone"]
        nome = contato["nome_contato"]
        
        # Substitui a tag {nome} pelo nome real do banco
        mensagem_final = msg_base.replace("{nome}", nome)
        
        sucesso = enviar_mensagem_whatsapp(telefone, nome, mensagem_final)
        status_text = "[green]✅ Enviado[/green]" if sucesso else "[red]❌ Falha[/red]"
        table.add_row(nome, telefone, status_text)
        time.sleep(1) 
            
    console.print(table)
    console.print("\n[bold cyan]🎉 Fluxo finalizado de ponta a ponta![/bold cyan]\n")
# ------------------------------------------

if __name__ == "__main__":
    main()