# database.py (Versão Definitiva com Transações Atômicas)
import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "financeiro.db"

def connect_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    # ... (as definições de tabela estão corretas, mantidas como estão)
    cursor.execute("""CREATE TABLE IF NOT EXISTS contas_bancarias (id INTEGER PRIMARY KEY AUTOINCREMENT, nome_banco TEXT NOT NULL, agencia TEXT, conta TEXT, saldo_inicial REAL DEFAULT 0, data_criacao TEXT NOT NULL);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS transacoes_bancarias (id INTEGER PRIMARY KEY AUTOINCREMENT, conta_id INTEGER NOT NULL, data TEXT NOT NULL, tipo TEXT NOT NULL, descricao TEXT NOT NULL, valor REAL NOT NULL, venda_id INTEGER, FOREIGN KEY (conta_id) REFERENCES contas_bancarias(id) ON DELETE CASCADE, FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE SET NULL);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT NOT NULL, telefone TEXT, email TEXT, data_venda TEXT NOT NULL, nome_kit TEXT NOT NULL, valor_venda REAL NOT NULL, valor_frete REAL DEFAULT 0);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS custos (venda_id INTEGER PRIMARY KEY, custo_mcpf REAL DEFAULT 0, custo_madeireira REAL DEFAULT 0, FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS plano_recebimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, venda_id INTEGER NOT NULL, descricao TEXT NOT NULL, valor_previsto REAL NOT NULL, data_vencimento TEXT, status TEXT DEFAULT 'Pendente', valor_pago REAL, data_pagamento TEXT, forma_pagamento TEXT, FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS pagamentos_custos (id INTEGER PRIMARY KEY AUTOINCREMENT, venda_id INTEGER NOT NULL, tipo_fornecedor TEXT NOT NULL, valor REAL NOT NULL, data_pagamento TEXT NOT NULL, FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS despesas_pagas (id INTEGER PRIMARY KEY AUTOINCREMENT, venda_id INTEGER NOT NULL, tipo_despesa TEXT NOT NULL, valor REAL NOT NULL, data_pagamento TEXT NOT NULL, FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS entregas (venda_id INTEGER PRIMARY KEY, status_entrega TEXT DEFAULT 'Aguardando', endereco_entrega TEXT, data_entrega TEXT, observacoes TEXT, FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS configuracoes (chave TEXT PRIMARY KEY, valor REAL NOT NULL);""")
    default_config = {'royalties': 0.075, 'propaganda': 0.015, 'icms': 0.10, 'simples': 0.045, 'corretagem': 0.03, 'admin': 0.05}
    for key, value in default_config.items(): 
        cursor.execute("INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_data_as_dataframe(query, params=()):
    conn = connect_db()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_query(query, params=()):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try:
        cursor.execute(query, params)
        last_id = cursor.lastrowid
        conn.commit()
    except Exception as e:
        print(f"ERRO AO EXECUTAR QUERY: {e}")
        raise e
    finally:
        conn.close()
    return last_id

# --- FUNÇÃO CENTRAL DA CORREÇÃO ---
def registrar_pagamento_parcela(plano_id, data):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    try:
        # Busca segura dos dados necessários
        cursor.execute("SELECT venda_id FROM plano_recebimentos WHERE id = ?", (plano_id,))
        plano_result = cursor.fetchone()
        if not plano_result:
            raise ValueError(f"Parcela com ID {plano_id} não encontrada.")
        venda_id = plano_result['venda_id']

        cursor.execute("SELECT cliente FROM vendas WHERE id = ?", (venda_id,))
        venda_result = cursor.fetchone()
        cliente = venda_result['cliente'] if venda_result else "Cliente Excluído"

        # --- Início da Transação ---
        cursor.execute("BEGIN TRANSACTION;")

        # Operação 1: Atualizar a parcela
        cursor.execute(
            "UPDATE plano_recebimentos SET status = 'Pago', valor_pago = ?, data_pagamento = ?, forma_pagamento = ? WHERE id = ?",
            (data['valor_pago'], data['data_pagamento'], data['forma_pagamento'], plano_id)
        )

        # Operação 2: Inserir a transação bancária, se houver conta
        if data.get('conta_id'):
            transacao_params = (
                data['conta_id'], data['data_pagamento'], 'Entrada',
                f"Recebimento Venda #{venda_id} - {cliente}",
                data['valor_pago'], venda_id
            )
            cursor.execute(
                "INSERT INTO transacoes_bancarias (conta_id, data, tipo, descricao, valor, venda_id) VALUES (?, ?, ?, ?, ?, ?)",
                transacao_params
            )
        
        # Se ambas as operações funcionaram, salva as mudanças
        conn.commit()
        # --- Fim da Transação ---

    except Exception as e:
        # Se qualquer operação falhou, desfaz tudo
        print(f"ERRO NA TRANSAÇÃO, revertendo... Erro: {e}")
        conn.rollback()
        raise e # Propaga o erro para a interface do usuário
    finally:
        conn.close()

# ... (Resto das funções, mantidas na versão limpa e descompactada)
def add_conta_bancaria(data):
    last_id = execute_query( "INSERT INTO contas_bancarias (nome_banco, agencia, conta, saldo_inicial, data_criacao) VALUES (?, ?, ?, ?, ?)", (data['nome_banco'], data['agencia'], data['conta'], data['saldo_inicial'], datetime.now().strftime("%Y-%m-%d")))
    if data['saldo_inicial'] > 0 and last_id: add_transacao_bancaria({ 'conta_id': last_id, 'data': datetime.now().strftime("%Y-%m-%d"), 'tipo': 'Entrada', 'descricao': 'Saldo Inicial', 'valor': data['saldo_inicial']})
def get_contas_bancarias():
    return get_data_as_dataframe("SELECT * FROM contas_bancarias")
def add_transacao_bancaria(data):
    if data.get('conta_id') is None and 'Saldo Inicial' not in data.get('descricao', ''):
        raise ValueError("ERRO CRÍTICO: Tentativa de inserir transação sem conta_id.")
    execute_query( "INSERT INTO transacoes_bancarias (conta_id, data, tipo, descricao, valor, venda_id) VALUES (?, ?, ?, ?, ?, ?)", (data['conta_id'], data['data'], data['tipo'], data['descricao'], data['valor'], data.get('venda_id')))
def get_saldo_contas():
    return get_data_as_dataframe("SELECT c.id, c.nome_banco, c.agencia, c.conta, (SELECT TOTAL(CASE WHEN tipo = 'Entrada' THEN valor ELSE -valor END) FROM transacoes_bancarias t WHERE t.conta_id = c.id) as saldo_atual FROM contas_bancarias c")
def update_parcela_plano(plano_id, data):
    execute_query( "UPDATE plano_recebimentos SET descricao = ?, valor_previsto = ?, data_vencimento = ? WHERE id = ? AND status = 'Pendente'", (data['descricao'], data['valor_previsto'], data['data_vencimento'], plano_id))
def get_all_vendas_options():
    return get_data_as_dataframe("SELECT id, cliente, nome_kit FROM vendas ORDER BY id DESC")
def add_venda(data):
    venda_id = execute_query("INSERT INTO vendas (cliente, telefone, email, data_venda, nome_kit, valor_venda, valor_frete) VALUES (?, ?, ?, ?, ?, ?, ?)", (data['cliente'], data['telefone'], data['email'], data['data_venda'], data['nome_kit'], data['valor_venda'], data['valor_frete']))
    if venda_id:
        execute_query("INSERT INTO custos (venda_id) VALUES (?)", (venda_id,))
        execute_query("INSERT INTO entregas (venda_id) VALUES (?)", (venda_id,))
    return venda_id
def delete_venda(venda_id):
    execute_query("DELETE FROM vendas WHERE id = ?", (venda_id,))
def update_custo(venda_id, custo_mcpf, custo_madeireira):
    execute_query("UPDATE custos SET custo_mcpf = ?, custo_madeireira = ? WHERE venda_id = ?", (custo_mcpf, custo_madeireira, venda_id))
def add_pagamento_custo(data):
    execute_query("INSERT INTO pagamentos_custos (venda_id, tipo_fornecedor, valor, data_pagamento) VALUES (?, ?, ?, ?)", (data['venda_id'], data['tipo_fornecedor'], data['valor'], data['data_pagamento']))
def add_despesa_paga(data):
    execute_query("INSERT INTO despesas_pagas (venda_id, tipo_despesa, valor, data_pagamento) VALUES (?, ?, ?, ?)", (data['venda_id'], data['tipo_despesa'], data['valor'], data['data_pagamento']))
def get_entrega_by_venda_id(venda_id):
    df = get_data_as_dataframe("SELECT * FROM entregas WHERE venda_id = ?", (venda_id,))
    return df.iloc[0] if not df.empty else None
def update_entrega(data):
    execute_query("UPDATE entregas SET status_entrega = ?, endereco_entrega = ?, data_entrega = ?, observacoes = ? WHERE venda_id = ?", (data['status_entrega'], data['endereco_entrega'], data['data_entrega'], data['observacoes'], data['venda_id']))
def get_config():
    df = get_data_as_dataframe("SELECT * FROM configuracoes")
    return pd.Series(df.valor.values, index=df.chave).to_dict()
def save_config(config_data):
    for key, value in config_data.items(): execute_query("UPDATE configuracoes SET valor = ? WHERE chave = ?", (value, key))
def add_parcela_plano(data):
    execute_query("INSERT INTO plano_recebimentos (venda_id, descricao, valor_previsto, data_vencimento) VALUES (?, ?, ?, ?)", (data['venda_id'], data['descricao'], data['valor_previsto'], data['data_vencimento']))
def delete_parcela_plano(plano_id):
    execute_query("DELETE FROM plano_recebimentos WHERE id = ?", (plano_id,))
def get_total_saldo_bancario():
    df = get_data_as_dataframe("SELECT TOTAL(CASE WHEN tipo = 'Entrada' THEN valor ELSE -valor END) as saldo_total FROM transacoes_bancarias")
    if not df.empty and df['saldo_total'].iloc[0] is not None: return df['saldo_total'].iloc[0]
    return 0