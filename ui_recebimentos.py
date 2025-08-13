# ui_recebimentos.py (Versão Final com todos os botões)
import streamlit as st
import pandas as pd
from datetime import date, datetime
from database import (
    get_all_vendas_options, get_data_as_dataframe, add_parcela_plano, 
    registrar_pagamento_parcela, get_contas_bancarias, delete_parcela_plano,
    update_parcela_plano
)
from calculations import calculate_venda_totals

def format_brl(value):
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ 0,00"

def render_recebimentos():
    st.header("💳 Plano de Recebimentos")
    if 'edit_parcela_id' not in st.session_state:
        st.session_state.edit_parcela_id = None

    vendas_options = get_all_vendas_options()
    if vendas_options.empty:
        st.warning("Nenhuma venda registrada."); return

    option_map = {f"#{row.id} - {row.cliente} ({row.nome_kit})": row.id for index, row in vendas_options.iterrows()}
    choice = st.selectbox("Selecione a Venda para gerenciar o plano", options=option_map.keys())
    
    if not choice: return
        
    venda_id = option_map[choice]
    totals = calculate_venda_totals(venda_id)
    plano_df = get_data_as_dataframe("SELECT * FROM plano_recebimentos WHERE venda_id = ? ORDER BY data_vencimento ASC", (venda_id,))

    st.divider()
    cols = st.columns(3)
    cols[0].metric("Valor Total da Venda", format_brl(totals.get('venda', {}).get('valor_venda', 0)))
    cols[1].metric("Total Recebido", format_brl(totals.get('total_recebido', 0)))
    cols[2].metric("Saldo a Receber", format_brl(totals.get('saldo_a_receber', 0)))
    total_venda_valor = totals.get('venda', {}).get('valor_venda', 0)
    total_recebido_valor = totals.get('total_recebido', 0)
    percentual_recebido = (total_recebido_valor / total_venda_valor) if total_venda_valor > 0 else 0
    st.progress(percentual_recebido, text=f"{percentual_recebido:.0%} Recebido")
    st.divider()

    with st.expander("➕ Adicionar Marco de Pagamento ao Plano"):
        with st.form("form_add_parcela", clear_on_submit=True):
            cols = st.columns([2, 1, 1])
            desc = cols[0].text_input("Descrição*", help="Ex: Sinal de 30%, Pagamento Final")
            val_previsto = cols[1].number_input("Valor Previsto*", min_value=0.01, format="%.2f")
            data_venc = cols[2].date_input("Data de Vencimento")
            if st.form_submit_button("Adicionar ao Plano"):
                if desc and val_previsto:
                    add_parcela_plano({'venda_id': venda_id, 'descricao': desc, 'valor_previsto': val_previsto, 'data_vencimento': str(data_venc)})
                    st.success("Marco de pagamento adicionado ao plano!"); st.rerun()
                else: st.error("Descrição e Valor Previsto são obrigatórios.")

    st.subheader("Plano de Pagamento Detalhado")

    if plano_df.empty:
        st.info("Nenhum marco de pagamento foi definido para esta venda ainda.")
    else:
        contas = get_contas_bancarias()
        for _, row in plano_df.iterrows():
            parcela_id = row['id']
            
            if st.session_state.edit_parcela_id == parcela_id:
                with st.form(f"form_edit_{parcela_id}"):
                    st.markdown(f"**Editando Parcela: {row['descricao']}**")
                    cols_edit = st.columns([2, 1, 1]); new_desc = cols_edit[0].text_input("Descrição", value=row['descricao'])
                    new_valor = cols_edit[1].number_input("Valor Previsto", value=float(row['valor_previsto']), format="%.2f")
                    data_venc_obj = None
                    if row['data_vencimento']:
                        try: data_venc_obj = datetime.strptime(row['data_vencimento'], '%Y-%m-%d').date()
                        except (ValueError, TypeError): pass
                    new_data = cols_edit[2].date_input("Data Vencimento", value=data_venc_obj)
                    submit_cols = st.columns(2)
                    if submit_cols[0].form_submit_button("Salvar Alterações"):
                        update_parcela_plano(parcela_id, {'descricao': new_desc, 'valor_previsto': new_valor, 'data_vencimento': str(new_data)})
                        st.session_state.edit_parcela_id = None; st.success("Parcela atualizada!"); st.rerun()
                    if submit_cols[1].form_submit_button("Cancelar"):
                        st.session_state.edit_parcela_id = None; st.rerun()
            else:
                with st.container(border=True):
                    cols = st.columns([0.4, 0.2, 0.2, 0.2])
                    cols[0].markdown(f"**{row['descricao']}**"); cols[1].markdown(f"Vencimento: {pd.to_datetime(row['data_vencimento']).strftime('%d/%m/%Y') if row['data_vencimento'] else 'N/A'}")
                    cols[2].markdown(f"Valor Previsto: **{format_brl(row['valor_previsto'])}**")

                    if row['status'] == 'Pendente':
                        # --- A MUDANÇA ESTÁ AQUI ---
                        status_col = cols[3].columns([1, 1, 1]) # Criamos 3 mini-colunas para os botões
                        status_col[0].warning("PENDENTE")
                        if status_col[1].button("✏️", key=f"edit_{parcela_id}", help="Editar Parcela"):
                            st.session_state.edit_parcela_id = parcela_id
                            st.rerun()
                        # Adicionamos o botão de exclusão
                        if status_col[2].button("🗑️", key=f"del_parcela_{parcela_id}", help="Excluir Parcela do Plano"):
                            delete_parcela_plano(parcela_id)
                            st.success("Parcela excluída do plano.")
                            st.rerun()
                            
                        with st.expander("Registrar Pagamento para este Marco"):
                            if contas.empty:
                                st.warning("Nenhuma conta bancária cadastrada.")
                            else:
                                with st.form(f"form_pay_{row['id']}", clear_on_submit=True):
                                    c = st.columns(4); val_pago = c[0].number_input("Valor Pago", value=row['valor_previsto'], format="%.2f", key=f"val_{row['id']}")
                                    data_pag = c[1].date_input("Data do Pagamento", value=date.today(), key=f"data_{row['id']}")
                                    forma_pag = c[2].selectbox("Forma", ["PIX", "Cartão", "Boleto", "Dinheiro", "Transferência"], key=f"forma_{row['id']}")
                                    conta_id = c[3].selectbox("Conta de Destino*", options=contas['id'], format_func=lambda x: contas[contas['id'] == x]['nome_banco'].iloc[0], key=f"conta_{row['id']}")
                                    if st.form_submit_button("Confirmar Pagamento"):
                                        if conta_id is None: st.error("ERRO: Nenhuma conta de destino foi selecionada.")
                                        else:
                                            registrar_pagamento_parcela(row['id'], {'valor_pago': val_pago, 'data_pagamento': str(data_pag), 'forma_pagamento': forma_pag, 'conta_id': int(conta_id)})
                                            st.success("Pagamento registrado!"); st.rerun()
                    else:
                        cols[3].success("PAGO")
                        info_cols = st.columns(3); info_cols[0].info(f"Valor Pago: {format_brl(row['valor_pago'])}")
                        info_cols[1].info(f"Data: {pd.to_datetime(row['data_pagamento']).strftime('%d/%m/%Y')}")
                        info_cols[2].info(f"Forma: {row['forma_pagamento']}")# ui_recebimentos.py (Versão Final com todos os botões)
import streamlit as st
import pandas as pd
from datetime import date, datetime
from database import (
    get_all_vendas_options, get_data_as_dataframe, add_parcela_plano, 
    registrar_pagamento_parcela, get_contas_bancarias, delete_parcela_plano,
    update_parcela_plano
)
from calculations import calculate_venda_totals

def format_brl(value):
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ 0,00"

def render_recebimentos():
    st.header("💳 Plano de Recebimentos")
    if 'edit_parcela_id' not in st.session_state:
        st.session_state.edit_parcela_id = None

    vendas_options = get_all_vendas_options()
    if vendas_options.empty:
        st.warning("Nenhuma venda registrada."); return

    option_map = {f"#{row.id} - {row.cliente} ({row.nome_kit})": row.id for index, row in vendas_options.iterrows()}
    choice = st.selectbox("Selecione a Venda para gerenciar o plano", options=option_map.keys())
    
    if not choice: return
        
    venda_id = option_map[choice]
    totals = calculate_venda_totals(venda_id)
    plano_df = get_data_as_dataframe("SELECT * FROM plano_recebimentos WHERE venda_id = ? ORDER BY data_vencimento ASC", (venda_id,))

    st.divider()
    cols = st.columns(3)
    cols[0].metric("Valor Total da Venda", format_brl(totals.get('venda', {}).get('valor_venda', 0)))
    cols[1].metric("Total Recebido", format_brl(totals.get('total_recebido', 0)))
    cols[2].metric("Saldo a Receber", format_brl(totals.get('saldo_a_receber', 0)))
    total_venda_valor = totals.get('venda', {}).get('valor_venda', 0)
    total_recebido_valor = totals.get('total_recebido', 0)
    percentual_recebido = (total_recebido_valor / total_venda_valor) if total_venda_valor > 0 else 0
    st.progress(percentual_recebido, text=f"{percentual_recebido:.0%} Recebido")
    st.divider()

    with st.expander("➕ Adicionar Marco de Pagamento ao Plano"):
        with st.form("form_add_parcela", clear_on_submit=True):
            cols = st.columns([2, 1, 1])
            desc = cols[0].text_input("Descrição*", help="Ex: Sinal de 30%, Pagamento Final")
            val_previsto = cols[1].number_input("Valor Previsto*", min_value=0.01, format="%.2f")
            data_venc = cols[2].date_input("Data de Vencimento")
            if st.form_submit_button("Adicionar ao Plano"):
                if desc and val_previsto:
                    add_parcela_plano({'venda_id': venda_id, 'descricao': desc, 'valor_previsto': val_previsto, 'data_vencimento': str(data_venc)})
                    st.success("Marco de pagamento adicionado ao plano!"); st.rerun()
                else: st.error("Descrição e Valor Previsto são obrigatórios.")

    st.subheader("Plano de Pagamento Detalhado")

    if plano_df.empty:
        st.info("Nenhum marco de pagamento foi definido para esta venda ainda.")
    else:
        contas = get_contas_bancarias()
        for _, row in plano_df.iterrows():
            parcela_id = row['id']
            
            if st.session_state.edit_parcela_id == parcela_id:
                with st.form(f"form_edit_{parcela_id}"):
                    st.markdown(f"**Editando Parcela: {row['descricao']}**")
                    cols_edit = st.columns([2, 1, 1]); new_desc = cols_edit[0].text_input("Descrição", value=row['descricao'])
                    new_valor = cols_edit[1].number_input("Valor Previsto", value=float(row['valor_previsto']), format="%.2f")
                    data_venc_obj = None
                    if row['data_vencimento']:
                        try: data_venc_obj = datetime.strptime(row['data_vencimento'], '%Y-%m-%d').date()
                        except (ValueError, TypeError): pass
                    new_data = cols_edit[2].date_input("Data Vencimento", value=data_venc_obj)
                    submit_cols = st.columns(2)
                    if submit_cols[0].form_submit_button("Salvar Alterações"):
                        update_parcela_plano(parcela_id, {'descricao': new_desc, 'valor_previsto': new_valor, 'data_vencimento': str(new_data)})
                        st.session_state.edit_parcela_id = None; st.success("Parcela atualizada!"); st.rerun()
                    if submit_cols[1].form_submit_button("Cancelar"):
                        st.session_state.edit_parcela_id = None; st.rerun()
            else:
                with st.container(border=True):
                    cols = st.columns([0.4, 0.2, 0.2, 0.2])
                    cols[0].markdown(f"**{row['descricao']}**"); cols[1].markdown(f"Vencimento: {pd.to_datetime(row['data_vencimento']).strftime('%d/%m/%Y') if row['data_vencimento'] else 'N/A'}")
                    cols[2].markdown(f"Valor Previsto: **{format_brl(row['valor_previsto'])}**")

                    if row['status'] == 'Pendente':
                        # --- A MUDANÇA ESTÁ AQUI ---
                        status_col = cols[3].columns([1, 1, 1]) # Criamos 3 mini-colunas para os botões
                        status_col[0].warning("PENDENTE")
                        if status_col[1].button("✏️", key=f"edit_{parcela_id}", help="Editar Parcela"):
                            st.session_state.edit_parcela_id = parcela_id
                            st.rerun()
                        # Adicionamos o botão de exclusão
                        if status_col[2].button("🗑️", key=f"del_parcela_{parcela_id}", help="Excluir Parcela do Plano"):
                            delete_parcela_plano(parcela_id)
                            st.success("Parcela excluída do plano.")
                            st.rerun()
                            
                        with st.expander("Registrar Pagamento para este Marco"):
                            if contas.empty:
                                st.warning("Nenhuma conta bancária cadastrada.")
                            else:
                                with st.form(f"form_pay_{row['id']}", clear_on_submit=True):
                                    c = st.columns(4); val_pago = c[0].number_input("Valor Pago", value=row['valor_previsto'], format="%.2f", key=f"val_{row['id']}")
                                    data_pag = c[1].date_input("Data do Pagamento", value=date.today(), key=f"data_{row['id']}")
                                    forma_pag = c[2].selectbox("Forma", ["PIX", "Cartão", "Boleto", "Dinheiro", "Transferência"], key=f"forma_{row['id']}")
                                    conta_id = c[3].selectbox("Conta de Destino*", options=contas['id'], format_func=lambda x: contas[contas['id'] == x]['nome_banco'].iloc[0], key=f"conta_{row['id']}")
                                    if st.form_submit_button("Confirmar Pagamento"):
                                        if conta_id is None: st.error("ERRO: Nenhuma conta de destino foi selecionada.")
                                        else:
                                            registrar_pagamento_parcela(row['id'], {'valor_pago': val_pago, 'data_pagamento': str(data_pag), 'forma_pagamento': forma_pag, 'conta_id': int(conta_id)})
                                            st.success("Pagamento registrado!"); st.rerun()
                    else:
                        cols[3].success("PAGO")
                        info_cols = st.columns(3); info_cols[0].info(f"Valor Pago: {format_brl(row['valor_pago'])}")
                        info_cols[1].info(f"Data: {pd.to_datetime(row['data_pagamento']).strftime('%d/%m/%Y')}")
                        info_cols[2].info(f"Forma: {row['forma_pagamento']}")