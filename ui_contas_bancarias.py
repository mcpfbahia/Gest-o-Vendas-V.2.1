# ui_contas_bancarias.py
import streamlit as st
import pandas as pd
from datetime import date
from database import add_conta_bancaria, get_saldo_contas, add_transacao_bancaria, get_data_as_dataframe

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
                        'nome_banco': nome_banco, 'agencia': agencia, 
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
        # Garante que não tenhamos mais colunas que contas
        num_contas = len(saldos_df)
        cols = st.columns(num_contas if num_contas > 0 else 1)
        
        for i, row in saldos_df.iterrows():
            # Evita erro se houver mais de 'n' colunas
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

        # Lançamentos Manuais
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

        # Extrato da conta selecionada
        extrato_df = get_data_as_dataframe(
            "SELECT data, tipo, descricao, valor FROM transacoes_bancarias WHERE conta_id = ? ORDER BY data DESC, id DESC",
            (int(conta_selecionada_id),)
        )
        st.dataframe(extrato_df, use_container_width=True)