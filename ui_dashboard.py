# ui_dashboard.py (Versão com o card de Saldo Total em Contas)
import streamlit as st
from calculations import calculate_global_totals

def format_currency(value):
    """Formata um número para o padrão monetário brasileiro."""
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ 0,00"

def styled_metric(title, value, icon=""):
    """Cria um card de métrica customizado com HTML e CSS."""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{icon} {title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def styled_balance_card(title, value, background_color):
    """Cria um card de saldo final com cor de fundo customizada."""
    st.markdown(f"""
    <div class="balance-card" style="background: {background_color};">
        <div class="balance-title">{title}</div>
        <div class="balance-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_dashboard():
    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #FF8C00, #1E1E1E);
        border-radius: 12px; padding: 25px; color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2); transition: all 0.3s ease-in-out;
        margin-bottom: 10px;
    }
    .metric-card:hover { transform: scale(1.03); box-shadow: 0 8px 16px rgba(0,0,0,0.3); }
    .metric-title { font-size: 1.1em; font-weight: 500; margin-bottom: 8px; opacity: 0.9; }
    .metric-value { font-size: 1.9em; font-weight: 700; line-height: 1.2; white-space: nowrap; }
    .balance-panel {
        border-radius: 12px; padding: 20px; margin-bottom: 10px;
        border: 1px solid #ddd;
    }
    .balance-panel.credits { background-color: #E8F5E9; border-left: 5px solid #4CAF50; }
    .balance-panel.debits { background-color: #FFF3E0; border-left: 5px solid #FF9800; }
    .balance-panel h3 { margin-top: 0; }
    .balance-card {
        border-radius: 12px; padding: 25px; color: white; text-align: center;
        margin-bottom: 10px;
    }
    .balance-title { font-size: 1.2em; font-weight: 600; margin-bottom: 8px; }
    .balance-value { font-size: 2.3em; font-weight: 700; }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #4CAF50, #8BC34A);
    }
    .debits-progress .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #FF9800, #FFC107);
    }
    </style>
    """, unsafe_allow_html=True)

    st.header("📊 Dashboard Geral")
    totals = calculate_global_totals()

    st.subheader("Visão Geral")
    cols = st.columns(5)
    with cols[0]: styled_metric(title="Total de Vendas", value=format_currency(totals.get('total_vendas', 0)), icon="💰")
    with cols[1]: styled_metric(title="Total Recebido", value=format_currency(totals.get('total_recebido', 0)), icon="✅")
    with cols[2]: styled_metric(title="Total a Receber", value=format_currency(totals.get('total_a_receber', 0)), icon="⏳")
    with cols[3]: styled_metric(title="Total de Custos", value=format_currency(totals.get('total_custos', 0)), icon="🛒")
    with cols[4]: styled_metric(title="Total de Despesas", value=format_currency(totals.get('total_despesas', 0)), icon="🧾")
    
    st.subheader("Resultados Financeiros e Caixa")
    cols = st.columns(4)
    with cols[0]: styled_metric(title="Lucro Bruto", value=format_currency(totals.get('lucro_bruto', 0)), icon="📈")
    with cols[1]: styled_metric(title="Lucro Líquido", value=format_currency(totals.get('lucro_liquido', 0)), icon="🎯")
    with cols[2]: styled_metric(title="% de Lucro", value=f"{totals.get('percentual_lucro', 0):.2f}%", icon="💡")
    
    # ESTE É O CARD QUE ESTAVA FALTANDO
    with cols[3]:
        styled_metric(
            title="Saldo Total em Contas",
            value=format_currency(totals.get('total_saldo_bancario', 0)),
            icon="🏦"
        )

    st.divider()

    st.subheader("Balanço Financeiro")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="balance-panel credits">', unsafe_allow_html=True)
        st.markdown("<h3>✅ Créditos (Entradas)</h3>", unsafe_allow_html=True)
        total_entradas = totals.get('creditos_realizado', 0) + totals.get('creditos_pendente', 0)
        st.metric(label="Potencial de Vendas", value=format_currency(total_entradas))
        percent_realizado_cr = (totals.get('creditos_realizado', 0) / total_entradas) if total_entradas > 0 else 0
        st.progress(percent_realizado_cr, text=f"{percent_realizado_cr:.0%} Realizado")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="balance-panel debits">', unsafe_allow_html=True)
        st.markdown("<h3>❌ Débitos (Saídas)</h3>", unsafe_allow_html=True)
        total_saidas = totals.get('total_pago_geral', 0) + totals.get('total_a_pagar_geral', 0)
        st.metric(label="Total de Saídas Previstas", value=format_currency(total_saidas))
        percent_realizado_db = (totals.get('total_pago_geral', 0) / total_saidas) if total_saidas > 0 else 0
        st.markdown('<div class="debits-progress">', unsafe_allow_html=True)
        st.progress(percent_realizado_db, text=f"{percent_realizado_db:.0%} Realizado")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Ver detalhamento de Créditos e Débitos"):
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.markdown("#### Detalhes de Créditos")
            st.metric("Recebido de Clientes (Realizado)", format_currency(totals.get('creditos_realizado', 0)))
            st.metric("A Receber de Clientes (Pendente)", format_currency(totals.get('creditos_pendente', 0)))
            
        with sub_col2:
            st.markdown("#### Detalhes de Débitos")
            st.metric("Pago a Fornecedores (Realizado)", format_currency(totals.get('debitos_pago_custos', 0)))
            st.metric("Pago de Despesas (Realizado)", format_currency(totals.get('debitos_pago_despesas', 0)))
            st.metric("A Pagar a Fornecedores (Pendente)", format_currency(totals.get('debitos_pendente_custos', 0)))
            st.metric("A Pagar de Despesas (Pendente)", format_currency(totals.get('debitos_pendente_despesas', 0)))

    st.divider()

    st.subheader("Balanço de Caixa (Projeção Final)")
    col1, col2 = st.columns(2)
    with col1:
        cor_saldo_realizado = "linear-gradient(135deg, #2E7D32, #4CAF50)"
        styled_balance_card(
            title="Saldo de Caixa Atual (Realizado)",
            value=format_currency(totals.get('saldo_realizado', 0)),
            background_color=cor_saldo_realizado
        )
    with col2:
        cor_saldo_futuro = "linear-gradient(135deg, #1565C0, #42A5F5)"
        if totals.get('balanco_futuro', 0) < 0:
            cor_saldo_futuro = "linear-gradient(135deg, #C62828, #F44336)"
        styled_balance_card(
            title="Balanço Futuro (Projeção)",
            value=format_currency(totals.get('balanco_futuro', 0)),
            background_color=cor_saldo_futuro
        )