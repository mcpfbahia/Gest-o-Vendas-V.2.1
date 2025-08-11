# app.py (Versão completa e corrigida com o menu Contas Bancárias)
import streamlit as st
import os
from datetime import datetime # <<< 1. ADICIONE ESTA LINHA

# 1. IMPORTAÇÃO DOS MÓDULOS DE UI (INTERFACE DO USUÁRIO)
from ui_dashboard import render_dashboard
from ui_vendas import render_vendas
from ui_contas_bancarias import render_contas_bancarias # <<< AQUI
from ui_custos import render_custos
from ui_recebimentos import render_recebimentos
from ui_despesas import render_despesas
from ui_entregas import render_entregas
from ui_configuracoes import render_configuracoes

from database import init_db

# Configuração da página
st.set_page_config(
    page_title="Gestão Financeira MCPF Bahia",
    page_icon="🏠",
    layout="wide"
)

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

    # 2. LISTA DE OPÇÕES DO MENU
    pagina_selecionada = st.radio(
        "Selecione uma página:",
        # Adicionada a nova opção na lista
        ["Dashboard", "Vendas", "Contas Bancárias", "Custos", "Recebimentos", "Despesas", "Entregas", "Configurações"],
        label_visibility="collapsed",
        format_func=lambda x: {
            "Dashboard": "📊 Dashboard",
            "Vendas": "📝 Vendas",
            "Contas Bancárias": "🏦 Contas Bancárias", # <<< AQUI
            "Custos": "💰 Custos",
            "Recebimentos": "💳 Recebimentos",
            "Despesas": "📋 Despesas",
            "Entregas": "🚚 Entregas",
            "Configurações": "⚙️ Configurações"
        }.get(x, x)
    )

    st.divider()
    # Adicionando a data e hora atual dinamicamente
    st.info(f"Sistema de Gestão v1.1 | © {datetime.now().year}")


# --- Renderização da Página Selecionada ---
st.title("Gestão Financeira | Minha Casa Pré-Fabricada Bahia")
st.caption("Simplificando a gestão financeira dos seus projetos.")
st.divider()


# 3. CONDIÇÃO PARA RENDERIZAR A PÁGINA
if pagina_selecionada == "Dashboard":
    render_dashboard()
elif pagina_selecionada == "Vendas":
    render_vendas()
elif pagina_selecionada == "Contas Bancárias": # <<< AQUI
    render_contas_bancarias()
elif pagina_selecionada == "Custos":
    render_custos()
elif pagina_selecionada == "Recebimentos":
    render_recebimentos()
elif pagina_selecionada == "Despesas":
    render_despesas()
elif pagina_selecionada == "Entregas":
    render_entregas()
elif pagina_selecionada == "Configurações":
    render_configuracoes()