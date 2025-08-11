# ui_configuracoes.py
import streamlit as st
import os
from database import get_config, save_config

def render_configuracoes():
    st.header("⚙️ Configurações Gerais")

    st.subheader("Percentuais de Despesas")
    
    current_config = get_config()
    
    with st.form("form_config"):
        new_config = {}
        cols = st.columns(3)
        col_idx = 0
        for key, value in current_config.items():
            label = f"{key.capitalize()} (Atual: {value*100:.2f}%)"
            new_config[key] = cols[col_idx].number_input(label, value=float(value), format="%.4f", step=0.001)
            col_idx = (col_idx + 1) % 3

        submitted = st.form_submit_button("Salvar Configurações")
        if submitted:
            save_config(new_config)
            st.success("Configurações salvas com sucesso!")
            st.rerun()
            
    st.divider()
    
    st.subheader("💾 Backup e Restauração")
    st.info("""
    **Backup:** Para fazer o backup dos seus dados, simplesmente copie o arquivo `financeiro.db` que está na mesma pasta desta aplicação.
    
    **Restauração:** Para restaurar um backup, feche a aplicação, substitua o arquivo `financeiro.db` atual pelo seu arquivo de backup e inicie a aplicação novamente.
    """)

    with open("financeiro.db", "rb") as fp:
        st.download_button(
            label="📥 Baixar Arquivo de Backup (financeiro.db)",
            data=fp,
            file_name="backup_financeiro.db",
            mime="application/octet-stream"
        )
        
    st.divider()
    
    st.subheader("🗑️ Limpeza de Dados")
    st.warning("CUIDADO: A ação a seguir é irreversível e apagará todos os dados do sistema.")
    if st.button("🔴 Limpar Todos os Dados"):
        if 'confirm_delete' not in st.session_state:
            st.session_state.confirm_delete = True
            st.rerun()
        
    if 'confirm_delete' in st.session_state and st.session_state.confirm_delete:
        st.error("Você tem certeza ABSOLUTA que deseja apagar todos os dados?")
        if st.button("Sim, tenho certeza. Apagar tudo."):
            try:
                os.remove("financeiro.db")
                del st.session_state.confirm_delete
                st.success("Todos os dados foram apagados. A aplicação será reiniciada.")
                st.rerun()
            except Exception as e:
                st.error(f"Não foi possível apagar o arquivo: {e}")
        if st.button("Não, cancelar."):
            del st.session_state.confirm_delete
            st.rerun()