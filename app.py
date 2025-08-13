# app.py (Versão com Tela de Login)
import streamlit as st
import os
from datetime import datetime

# Importações dos módulos de UI
from ui_dashboard import render_dashboard
from ui_vendas import render_vendas
from ui_contas_bancarias import render_contas_bancarias
from ui_custos import render_custos
from ui_recebimentos import render_recebimentos
from ui_despesas import render_despesas
from ui_entregas import render_entregas
from ui_configuracoes import render_configuracoes

from database import init_db

# --- LÓGICA DE AUTENTICAÇÃO ---
def check_password():
    """Retorna True se o usuário fez login."""
    
    # Função para verificar a senha digitada com a senha secreta
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] # Não mantenha a senha em memória
        else:
            st.session_state["password_correct"] = False

    # Se já fizemos login, retorna True
    if st.session_state.get("password_correct", False):
        return True

    # Mostra o formulário de senha
    st.text_input("Senha", type="password", on_change=password_entered, key="password")
    
    if "password_correct" in st.session_state and not st.session_state.password_correct:
        st.error("Senha incorreta.")
        
    return False

# --- FIM DA LÓGICA DE AUTENTICAÇÃO ---


# Configuração da página
st.set_page_config(
    page_title="Gestão Financeira MCPF Bahia",
    page_icon="🏠",
    layout="wide"
)

# APLICA A VERIFICAÇÃO DE SENHA
if not check_password():
    st.stop() # Interrompe a execução do app se a senha não estiver correta

# Se a senha estiver correta, o resto do app carrega normalmente
# -------------------------------------------------------------------

# Inicialização do banco de dados
if not os.path.exists("financeiro.db"):
    init_db()

# --- Construção da Barra Lateral de Navegação ---
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except Exception as e:
        st.info("Para adicionar um logo, salve um arquivo 'logo.png' na pasta do projeto.")

    st.title("Menu de Navegação")
    st.divider()

    pagina_selecionada = st.radio(
        "Selecione uma página:",
        ["Dashboard", "Vendas", "Contas Bancárias", "Custos", "Recebimentos", "Despesas", "Entregas", "Configuracoes"],
        label_visibility="collapsed",
        format_func=lambda x: {
            "Dashboard": "📊 Dashboard", "Vendas": "📝 Vendas", "Contas Bancárias": "🏦 Contas Bancárias",
            "Custos": "💰 Custos", "Recebimentos": "💳 Recebimentos", "Despesas": "📋 Despesas",
            "Entregas": "🚚 Entregas", "Configuracoes": "⚙️ Configurações"
        }.get(x, x.replace("_", " ").title())
    )

    st.divider()
    st.info(f"Sistema de Gestão v2.3 | © {datetime.now().year}")

# --- Renderização da Página Selecionada ---
st.title("Gestão Financeira | Minha Casa Pré-Fabricada Bahia")
st.caption("Simplificando a gestão financeira dos seus projetos.")
st.divider()

if pagina_selecionada == "Dashboard":
    render_dashboard()
elif pagina_selecionada == "Vendas":
    render_vendas()
elif pagina_selecionada == "Contas Bancárias":
    render_contas_bancarias()
elif pagina_selecionada == "Custos":
    render_custos()
elif pagina_selecionada == "Recebimentos":
    render_recebimentos()
elif pagina_selecionada == "Despesas":
    render_despesas()
elif pagina_selecionada == "Entregas":
    render_entregas()
elif pagina_selecionada == "Configuracoes":
    render_configuracoes()