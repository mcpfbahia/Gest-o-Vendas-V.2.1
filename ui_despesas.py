# ui_despesas.py (Versão completa com botão de exclusão)
import streamlit as st
import pandas as pd
from datetime import date
from database import get_all_vendas_options, add_despesa_paga, get_data_as_dataframe, get_config, delete_despesa_paga
from calculations import calculate_venda_totals

def format_brl(value):
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ 0,00"

def render_despesas():
    st.header("📋 Gerenciamento de Despesas por Venda")

    vendas_options = get_all_vendas_options()
    if vendas_options.empty:
        st.warning("Nenhuma venda registrada para gerenciar despesas.")
        return

    option_map = {f"#{row.id} - {row.cliente} ({row.nome_kit})": row.id for index, row in vendas_options.iterrows()}
    choice = st.selectbox("Selecione a Venda para gerenciar as despesas", options=option_map.keys())
    
    if not choice:
        return
        
    venda_id = option_map[choice]
    totals = calculate_venda_totals(venda_id)
    config = get_config()
    
    st.divider()

    st.subheader("Resumo Geral de Despesas do Projeto")
    cols = st.columns(3)
    cols[0].metric("Total de Despesas Calculado", format_brl(totals['despesas_total_calculado']))
    cols[1].metric("Total Pago", format_brl(totals['total_despesas_pagas']))
    cols[2].metric("Saldo a Pagar", format_brl(totals['saldo_despesas_a_pagar']))

    st.divider()

    with st.expander("💸 Registrar Novo Pagamento de Despesa"):
        with st.form("form_pagamento_despesa", clear_on_submit=True):
            cols = st.columns(3)
            tipo_despesa = cols[0].selectbox("Tipo de Despesa*", options=list(config.keys()))
            valor_pago = cols[1].number_input("Valor Pago*", min_value=0.01, format="%.2f")
            data_pagamento = cols[2].date_input("Data do Pagamento*", value=date.today())
            
            if st.form_submit_button("Registrar Pagamento"):
                add_despesa_paga({
                    'venda_id': venda_id, 'tipo_despesa': tipo_despesa,
                    'valor': valor_pago, 'data_pagamento': str(data_pagamento)
                })
                st.success(f"Pagamento de {tipo_despesa.capitalize()} registrado!")
                st.rerun()

    st.subheader("Controle Detalhado por Tipo de Despesa")

    for tipo, valor_calculado in totals['despesas_detalhadas'].items():
        if valor_calculado > 0:
            with st.container(border=True):
                pago_neste_tipo = totals.get('pagamentos_despesa_por_tipo', {}).get(tipo, 0)
                saldo_a_pagar = valor_calculado - pago_neste_tipo
                st.markdown(f"<h5>{tipo.capitalize()}</h5>", unsafe_allow_html=True)
                sub_cols = st.columns(3)
                sub_cols[0].metric("Valor Calculado", format_brl(valor_calculado))
                sub_cols[1].metric("Valor Pago", format_brl(pago_neste_tipo))
                sub_cols[2].metric("Saldo a Pagar", format_brl(saldo_a_pagar))
    
    st.divider()

    # --- SEÇÃO DE HISTÓRICO ATUALIZADA ---
    st.subheader("Histórico de Pagamentos de Despesas")
    hist_pag_despesas = get_data_as_dataframe("SELECT id, data_pagamento, tipo_despesa, valor FROM despesas_pagas WHERE venda_id = ? ORDER BY data_pagamento DESC", (venda_id,))
    
    if hist_pag_despesas.empty:
        st.info("Nenhum pagamento de despesa registrado para esta venda.")
    else:
        header_cols = st.columns([0.25, 0.3, 0.3, 0.15])
        header_cols[0].markdown("**Data**")
        header_cols[1].markdown("**Tipo de Despesa**")
        header_cols[2].markdown("**Valor Pago**")
        header_cols[3].markdown("**Ações**")
        st.divider()
        
        for _, row in hist_pag_despesas.iterrows():
            cols = st.columns([0.25, 0.3, 0.3, 0.15])
            cols[0].write(pd.to_datetime(row['data_pagamento']).strftime('%d/%m/%Y'))
            cols[1].write(row['tipo_despesa'].capitalize())
            cols[2].write(format_brl(row['valor']))
            
            if cols[3].button("🗑️", key=f"del_desp_{row['id']}", help="Excluir este pagamento"):
                delete_despesa_paga(row['id'])
                st.success("Pagamento de despesa excluído.")
                st.rerun()