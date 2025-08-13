# ui_contas_bancarias.py (Versão completa com botão de exclusão)
import streamlit as st
import pandas as pd
from datetime import date
from database import add_conta_bancaria, get_saldo_contas, add_transacao_bancaria, get_data_as_dataframe, delete_transacao_bancaria

def format_brl(value):
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ 0,00"

def render_contas_bancarias():
    st.header("🏦 Controle de Contas Bancárias")

    with st.expander("➕ Adicionar Nova Conta Bancária"):
        with st.form("form_add_conta", clear_on_submit=True):
            cols = st.columns(4)
            nome_banco = cols[0].text_input("Nome do Banco*")
            agencia = cols[1].text_input("Agência")
            conta = cols[2].text_input("Conta")
            saldo_inicial = cols[3].number_input("Saldo Inicial", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("Adicionar Conta"):
                if nome_banco:
                    add_conta_bancaria({
                        'nome_bancario': nome_banco, 'agencia': agencia, 
                        'conta': conta, 'saldo_inicial': saldo_inicial
                    })
                    st.success(f"Conta '{nome_banco}' adicionada com sucesso!")
                    st.rerun()
                else:
                    st.error("O nome do banco é obrigatório.")

    st.divider()
    st.subheader("Saldos Atuais")
    
    saldos_df = get_saldo_contas()
    if saldos_df.empty:
        st.info("Nenhuma conta bancária cadastrada. Adicione uma acima.")
    else:
        num_contas = len(saldos_df)
        cols = st.columns(num_contas if num_contas > 0 else 1)
        for i, row in saldos_df.iterrows():
            col_index = i % (num_contas if num_contas > 0 else 1)
            with cols[col_index]:
                st.metric(
                    label=f"{row['nome_banco']} (Ag: {row['agencia']} / C: {row['conta']})",
                    value=format_brl(row['saldo_atual'])
                )

    st.divider()
    st.subheader("Extrato e Lançamentos Manuais")

    if not saldos_df.empty:
        conta_selecionada_id = st.selectbox(
            "Selecione uma conta para ver o extrato ou fazer um lançamento",
            options=saldos_df['id'],
            format_func=lambda x: saldos_df[saldos_df['id'] == x]['nome_banco'].iloc[0]
        )

        with st.expander("💸 Adicionar Lançamento Manual (Entrada/Saída)"):
            with st.form("form_add_transacao", clear_on_submit=True):
                cols = st.columns(4)
                tipo = cols[0].selectbox("Tipo de Lançamento*", ["Entrada", "Saída"])
                desc = cols[1].text_input("Descrição*", help="Ex: Pagamento de conta de luz, Aporte de sócio")
                valor = cols[2].number_input("Valor*", min_value=0.01, format="%.2f")
                data_transacao = cols[3].date_input("Data*", value=date.today())
                
                if st.form_submit_button("Registrar Lançamento"):
                    add_transacao_bancaria({
                        'conta_id': conta_selecionada_id, 'data': str(data_transacao),
                        'tipo': tipo, 'descricao': desc, 'valor': valor
                    })
                    st.success("Transação registrada!")
                    st.rerun()
        
        # --- SEÇÃO DE EXTRATO ATUALIZADA ---
        st.subheader("Extrato da Conta")
        extrato_df = get_data_as_dataframe(
            "SELECT id, data, tipo, descricao, valor FROM transacoes_bancarias WHERE conta_id = ? ORDER BY data DESC, id DESC",
            (int(conta_selecionada_id),)
        )
        
        if extrato_df.empty:
            st.info("Nenhuma transação nesta conta ainda.")
        else:
            header_cols = st.columns([0.15, 0.15, 0.4, 0.2, 0.1])
            header_cols[0].markdown("**Data**"); header_cols[1].markdown("**Tipo**"); header_cols[2].markdown("**Descrição**"); header_cols[3].markdown("**Valor**"); header_cols[4].markdown("**Ações**")
            st.divider()

            for _, row in extrato_df.iterrows():
                cols = st.columns([0.15, 0.15, 0.4, 0.2, 0.1])
                cols[0].write(pd.to_datetime(row['data']).strftime('%d/%m/%Y'))
                cols[1].write(row['tipo'])
                cols[2].write(row['descricao'])
                valor_str = format_brl(row['valor'])
                
                if row['tipo'] == 'Entrada':
                    cols[3].success(valor_str)
                else:
                    cols[3].error(f"-{valor_str}")
                
                # Não permite excluir o "Saldo Inicial" para manter a integridade
                if 'Saldo Inicial' not in row['descricao']:
                    if cols[4].button("🗑️", key=f"del_trans_{row['id']}", help="Excluir esta transação"):
                        delete_transacao_bancaria(row['id'])
                        st.success("Transação excluída.")
                        st.rerun()