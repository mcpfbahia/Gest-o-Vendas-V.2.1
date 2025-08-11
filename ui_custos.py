# ui_custos.py (substitua o arquivo todo)
import streamlit as st
import pandas as pd
from datetime import date
from database import get_all_vendas_options, update_custo, add_pagamento_custo, get_data_as_dataframe
from calculations import calculate_venda_totals

def format_brl(value): # Adicionando a função aqui
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ 0,00"

def render_custos():
    st.header("💰 Gerenciamento de Custos por Fornecedor")
    # ... (resto do código não muda)
    vendas_options = get_all_vendas_options()
    if vendas_options.empty:
        st.warning("Nenhuma venda registrada para gerenciar custos.")
        return
    option_map = {f"#{row.id} - {row.cliente} ({row.nome_kit})": row.id for index, row in vendas_options.iterrows()}
    choice = st.selectbox("Selecione a Venda para gerenciar os custos", options=option_map.keys())
    if not choice:
        st.info("Por favor, selecione uma venda acima.")
        return
    venda_id = option_map[choice]
    totals = calculate_venda_totals(venda_id)
    st.divider()
    with st.expander("Definir Custos Totais da Venda", expanded=True):
        with st.form("form_atualizar_custos"):
            cols = st.columns(2)
            c_mcpf = cols[0].number_input("Custo Total - Fornecedor MCPF", value=float(totals.get('custo_mcpf', 0)), format="%.2f", help="Digite o valor total negociado com o fornecedor MCPF para este projeto.")
            c_madeireira = cols[1].number_input("Custo Total - Fornecedor Madeireira", value=float(totals.get('custo_madeireira', 0)), format="%.2f", help="Digite o valor total negociado com a Madeireira para este projeto.")
            submitted = st.form_submit_button("Salvar Custos Totais")
            if submitted:
                update_custo(venda_id, c_mcpf, c_madeireira)
                st.success("Custos totais da venda foram salvos!")
                st.rerun()
    st.divider()
    st.subheader("Controle de Pagamentos aos Fornecedores")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("<h5>Fornecedor: MCPF</h5>", unsafe_allow_html=True)
            saldo_mcpf = totals['custo_mcpf'] - totals['pagamentos_mcpf']
            st.metric("Saldo a Pagar", format_brl(saldo_mcpf)) # MUDANÇA APLICADA
            with st.expander("Registrar Pagamento para MCPF"):
                with st.form(f"form_pag_mcpf", clear_on_submit=True):
                    valor_pago = st.number_input("Valor Pago*", min_value=0.01, format="%.2f", key=f"val_mcpf_{venda_id}")
                    data_pagamento = st.date_input("Data do Pagamento*", value=date.today(), key=f"data_mcpf_{venda_id}")
                    if st.form_submit_button("Registrar"):
                        add_pagamento_custo({'venda_id': venda_id, 'tipo_fornecedor': 'MCPF', 'valor': valor_pago, 'data_pagamento': str(data_pagamento)})
                        st.success("Pagamento para MCPF registrado!")
                        st.rerun()
    with col2:
        with st.container(border=True):
            st.markdown("<h5>Fornecedor: Madeireira</h5>", unsafe_allow_html=True)
            saldo_madeireira = totals['custo_madeireira'] - totals['pagamentos_madeireira']
            st.metric("Saldo a Pagar", format_brl(saldo_madeireira)) # MUDANÇA APLICADA
            with st.expander("Registrar Pagamento para Madeireira"):
                with st.form(f"form_pag_madeireira", clear_on_submit=True):
                    valor_pago = st.number_input("Valor Pago*", min_value=0.01, format="%.2f", key=f"val_mad_{venda_id}")
                    data_pagamento = st.date_input("Data do Pagamento*", value=date.today(), key=f"data_mad_{venda_id}")
                    if st.form_submit_button("Registrar"):
                        add_pagamento_custo({'venda_id': venda_id, 'tipo_fornecedor': 'Madeireira', 'valor': valor_pago, 'data_pagamento': str(data_pagamento)})
                        st.success("Pagamento para Madeireira registrado!")
                        st.rerun()
    st.divider()
    st.subheader("Histórico de Pagamentos de Custos")
    hist_pag_custos = get_data_as_dataframe("SELECT data_pagamento, tipo_fornecedor, valor FROM pagamentos_custos WHERE venda_id = ? ORDER BY data_pagamento DESC", (venda_id,))
    if hist_pag_custos.empty:
        st.info("Nenhum pagamento de custo registrado para esta venda.")
    else:
        st.dataframe(hist_pag_custos, use_container_width=True)