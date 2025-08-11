# ui_entregas.py
import streamlit as st
import pandas as pd
from datetime import datetime
# A LINHA ABAIXO FOI CORRIGIDA para incluir 'get_data_as_dataframe'
from database import get_all_vendas_options, get_entrega_by_venda_id, update_entrega, get_data_as_dataframe

def render_entregas():
    st.header("🚚 Gerenciar Entregas")

    vendas_options = get_all_vendas_options()
    if vendas_options.empty:
        st.warning("Nenhuma venda registrada para gerenciar entregas.")
        return

    option_map = {f"#{row.id} - {row.cliente} ({row.nome_kit})": row.id for index, row in vendas_options.iterrows()}
    choice = st.selectbox("Selecione a Venda para Atualizar", options=option_map.keys(), key="entrega_venda_choice")
    
    if choice:
        venda_id = option_map[choice]
        entrega_atual = get_entrega_by_venda_id(venda_id)
        
        if entrega_atual is None:
            st.error("Não foi possível carregar os dados de entrega para esta venda.")
            return

        with st.form("form_atualizar_entrega"):
            st.subheader(f"Atualizar Status da Venda #{venda_id}")
            
            status_options = ["Aguardando", "Em Transporte", "Entregue"]
            status_index = status_options.index(entrega_atual['status_entrega']) if entrega_atual['status_entrega'] in status_options else 0
            
            data_entrega_val = None
            if entrega_atual['data_entrega']:
                try:
                    data_entrega_val = datetime.strptime(entrega_atual['data_entrega'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    data_entrega_val = None

            status = st.selectbox("Status da Entrega*", options=status_options, index=status_index)
            data_entrega = st.date_input("Data da Entrega", value=data_entrega_val)
            endereco = st.text_area("Endereço de Entrega", value=entrega_atual['endereco_entrega'] or "")
            obs = st.text_area("Observações", value=entrega_atual['observacoes'] or "")
            
            submitted = st.form_submit_button("Atualizar Entrega")
            if submitted:
                update_entrega({
                    'venda_id': venda_id, 'status_entrega': status,
                    'endereco_entrega': endereco, 'data_entrega': str(data_entrega) if data_entrega else None,
                    'observacoes': obs
                })
                st.success("Status da entrega atualizado com sucesso!")
                st.rerun()

    st.divider()
    st.subheader("📦 Status de Todas as Entregas")
    # Esta linha agora funcionará, pois a função foi importada corretamente
    entregas_df = get_data_as_dataframe("""
        SELECT v.id, v.cliente, e.status_entrega, e.data_entrega 
        FROM vendas v 
        LEFT JOIN entregas e ON v.id = e.venda_id 
        ORDER BY v.id DESC
    """)
    if not entregas_df.empty:
        entregas_df.rename(columns={'id': 'ID Venda', 'cliente': 'Cliente', 'status_entrega': 'Status', 'data_entrega': 'Data Prevista'}, inplace=True)
        st.dataframe(entregas_df, use_container_width=True)