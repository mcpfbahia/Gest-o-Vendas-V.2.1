# ui_dashboard.py (Versão Final com alinhamento e cards de lucro)
import streamlit as st
from calculations import calculate_global_totals

def format_brl(value):
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ 0,00"

def styled_card(title, value, subtitle="", icon="", bg_color="linear-gradient(135deg, #FF8C00, #1E1E1E)"):
    # AJUSTE: Altura ligeiramente aumentada para melhor alinhamento
    st.markdown(f"""
    <div class="custom-card" style="background:{bg_color};">
        <div class="card-title">{icon} {title}</div>
        <div class="card-value">{value}</div>
        <div class="card-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard():
    st.markdown("""
    <style>
    .custom-card {
        border-radius: 12px;
        padding: 20px; /* AJUSTE: Padding ajustado */
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        height: 165px; /* AJUSTE: Altura fixa para todos os cards principais */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .card-title { font-size: 1.1em; font-weight: 500; opacity: 0.9; } /* AJUSTE: Fonte do título */
    .card-value { font-size: 2.2em; font-weight: 700; line-height: 1.2; } /* AJUSTE: Fonte do valor */
    .card-subtitle { font-size: 0.9em; opacity: 0.8; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

    st.header("📊 Dashboard Estratégico")
    st.markdown("---")
    
    totals = calculate_global_totals()

    col1, col2, col3 = st.columns(3)

    # --- COLUNA 1: ATIVOS (O QUE VOCÊ TEM) ---
    with col1:
        st.subheader("↙️ Disponível (Caixa + A Receber)")
        styled_card(
            title="Saldo em Contas Bancárias",
            value=format_brl(totals['total_saldo_bancario']),
            subtitle="Dinheiro em caixa hoje", icon="🏦",
            bg_color="linear-gradient(135deg, #007bff, #0056b3)"
        )
        styled_card(
            title="Saldo de Clientes a Receber",
            value=format_brl(totals['total_a_receber']),
            subtitle="Créditos pendentes", icon="⏳",
            bg_color="linear-gradient(135deg, #ffc107, #d39e00)"
        )
        styled_card(
            title="TOTAL DISPONÍVEL",
            value=format_brl(totals['total_disponivel']),
            subtitle="Caixa Atual + Futuras Entradas", icon="💰",
            bg_color="linear-gradient(135deg, #28a745, #1e7e34)"
        )

    # --- COLUNA 2: PASSIVOS (O QUE VOCÊ DEVE) ---
    with col2:
        st.subheader("↗️ Dívidas (Custos + Despesas a Pagar)")
        styled_card(
            title="Saldo de Custos a Pagar",
            value=format_brl(totals['debitos_pendente_custos']),
            subtitle="Dívida com Fornecedores", icon="🛒",
            bg_color="linear-gradient(135deg, #dc3545, #a71d2a)"
        )
        styled_card(
            title="Saldo de Despesas a Pagar",
            value=format_brl(totals['debitos_pendente_despesas']),
            subtitle="Impostos, comissões, etc.", icon="🧾",
            bg_color="linear-gradient(135deg, #fd7e14, #c7640f)"
        )
        styled_card(
            title="TOTAL A PAGAR",
            value=format_brl(totals['total_a_pagar_geral']),
            subtitle="Total de Dívidas Pendentes", icon="💸",
            bg_color="linear-gradient(135deg, #6f42c1, #59369a)"
        )

    # --- COLUNA 3: SAÚDE FINANCEIRA (COM ALINHAMENTO CORRIGIDO) ---
    with col3:
        st.subheader("📊 Saúde Financeira")
        
        cor_provisao = "linear-gradient(135deg, #17a2b8, #117a8b)"
        if totals['provisao_saldo_final'] < 0:
            cor_provisao = "linear-gradient(135deg, #343a40, #23272b)"
        
        # 1. Card de Provisão de Saldo Final (agora alinhado no topo)
        styled_card(
            title="PROVISÃO DE SALDO FINAL",
            value=format_brl(totals['provisao_saldo_final']),
            subtitle="(Total Disponível - Total a Pagar)", icon="🎯",
            bg_color=cor_provisao
        )
        
        # 2. Novos Cards para Lucro e Margem
        styled_card(
            title="Lucro Líquido Total",
            value=format_brl(totals['lucro_liquido']),
            subtitle="Soma do lucro de todos os projetos", icon="✨",
            bg_color="linear-gradient(135deg, #20c997, #1ba784)" # Tom de verde-água
        )

        styled_card(
            title="Margem de Lucro Média",
            value=f"{totals['percentual_lucro']:.2f}%",
            subtitle="(Lucro Líquido / Vendas)", icon="💡",
            bg_color="linear-gradient(135deg, #e83e8c, #bf3474)" # Rosa/Magenta
        )