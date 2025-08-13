# ui_vendas.py (Versão com Filtro de Busca)
import streamlit as st
import pandas as pd
from datetime import date
from database import add_venda, delete_venda, get_data_as_dataframe
from calculations import calculate_venda_totals
from pdf_generator import gerar_recibo_venda

def format_brl(value):
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ 0,00"

def render_vendas():
    st.header("📝 Vendas")

    with st.expander("➕ Registrar Nova Venda", expanded=False):
        # ... (O formulário de registro de nova venda não muda)
        with st.form("form_nova_venda", clear_on_submit=True):
            cols = st.columns((2, 1, 2)); cliente = cols[0].text_input("Cliente*", key="cliente"); telefone = cols[1].text_input("Telefone", key="telefone"); email = cols[2].text_input("Email", key="email")
            cols = st.columns(4); data_venda = cols[0].date_input("Data da Venda*", value=date.today(), key="data_venda", format="DD/MM/YYYY"); nome_kit = cols[1].text_input("Nome do Kit*", key="nome_kit")
            valor_venda = cols[2].number_input("Valor da Venda*", min_value=0.0, format="%.2f", key="valor_venda", help="Use PONTO (.) para casas decimais. Ex: 50000.00")
            valor_frete = cols[3].number_input("Valor do Frete", min_value=0.0, format="%.2f", key="valor_frete", help="Use PONTO (.) para casas decimais. Ex: 350.50")
            if st.form_submit_button("Registrar Venda"):
                if not cliente or not nome_kit or valor_venda <= 0: st.error("Por favor, preencha os campos obrigatórios: Cliente, Nome do Kit e Valor da Venda.")
                else:
                    venda_data = {'cliente': cliente, 'telefone': telefone, 'email': email, 'data_venda': str(data_venda), 'nome_kit': nome_kit, 'valor_venda': valor_venda, 'valor_frete': valor_frete}
                    add_venda(venda_data); st.success("Venda registrada com sucesso!"); st.rerun()

    st.subheader("📋 Vendas Registradas")
    
    # --- LÓGICA DO FILTRO DE BUSCA ---
    # 1. Busca todos os dados do banco de dados primeiro
    vendas_df_completo = get_data_as_dataframe("SELECT v.*, e.status_entrega FROM vendas v LEFT JOIN entregas e ON v.id = e.venda_id ORDER BY v.id DESC")
    
    # 2. Cria o campo de texto para a busca
    termo_busca = st.text_input("🔍 Buscar Vendas (por cliente ou nome do kit)", placeholder="Digite aqui para filtrar...")

    # 3. Filtra o dataframe se houver algo digitado na busca
    if termo_busca:
        vendas_df_filtrado = vendas_df_completo[
            vendas_df_completo['cliente'].str.contains(termo_busca, case=False, na=False) |
            vendas_df_completo['nome_kit'].str.contains(termo_busca, case=False, na=False)
        ]
    else:
        vendas_df_filtrado = vendas_df_completo

    if vendas_df_filtrado.empty:
        if termo_busca:
            st.warning(f"Nenhuma venda encontrada para o termo '{termo_busca}'.")
        else:
            st.info("Nenhuma venda registrada ainda.")
    else:
        header_cols = st.columns([0.05, 0.2, 0.1, 0.2, 0.15, 0.1, 0.2])
        fields = ["ID", "Cliente", "Data", "Kit", "Lucro Líquido", "Status Entrega", "Ações"]
        for col, field_name in zip(header_cols, fields):
            col.markdown(f"**{field_name}**")
        st.divider()

        # 4. O loop agora usa o dataframe JÁ FILTRADO
        for _, row in vendas_df_filtrado.iterrows():
            venda_id = row['id']
            totals = calculate_venda_totals(venda_id)
            
            row_cols = st.columns([0.05, 0.2, 0.1, 0.2, 0.15, 0.1, 0.2])
            
            row_cols[0].write(str(venda_id))
            row_cols[1].write(row['cliente'])
            row_cols[2].write(pd.to_datetime(row['data_venda']).strftime('%d/%m/%Y'))
            row_cols[3].write(row['nome_kit'])
            row_cols[4].write(format_brl(totals['lucro_liquido']))
            row_cols[5].write(row['status_entrega'] or 'Aguardando')
            
            with row_cols[6]:
                action_cols = st.columns([1, 1])
                
                if action_cols[0].button("🗑️", key=f"delete_venda_{venda_id}", help="Excluir venda"):
                    delete_venda(venda_id); st.success(f"Venda #{venda_id} excluída."); st.rerun()
                
                pagamentos_df = get_data_as_dataframe("SELECT * FROM plano_recebimentos WHERE venda_id = ?", (venda_id,))
                dados_para_pdf = row.to_dict()
                dados_para_pdf['data_venda'] = pd.to_datetime(dados_para_pdf['data_venda']).strftime('%d/%m/%Y')
                pagamentos_list = []
                for _, pag_row in pagamentos_df.iterrows():
                    pag_dict = pag_row.to_dict()
                    if pag_dict.get('data_pagamento'):
                        pag_dict['data_pagamento'] = pd.to_datetime(pag_dict['data_pagamento']).strftime('%d/%m/%Y')
                    pagamentos_list.append(pag_dict)
                dados_para_pdf['pagamentos'] = pagamentos_list

                pdf_bytes = gerar_recibo_venda(dados_para_pdf)
                
                action_cols[1].download_button(
                    label="📄", data=pdf_bytes,
                    file_name=f"Recibo_Venda_{venda_id}_{row['cliente']}.pdf",
                    mime='application/pdf', help="Gerar Recibo de Venda em PDF"
                )