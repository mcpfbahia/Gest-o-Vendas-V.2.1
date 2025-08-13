# calculations.py (Versão com a importação corrigida)
import pandas as pd
# A CORREÇÃO ESTÁ AQUI: Adicionamos a função que faltava na linha de importação
from database import get_data_as_dataframe, get_config, get_total_saldo_bancario

def calculate_venda_totals(venda_id):
    """Calcula todos os totais para uma única venda."""
    venda = get_data_as_dataframe("SELECT * FROM vendas WHERE id = ?", (venda_id,)).iloc[0]
    custo = get_data_as_dataframe("SELECT * FROM custos WHERE venda_id = ?", (venda_id,)).iloc[0]
    plano_recebimentos = get_data_as_dataframe("SELECT * FROM plano_recebimentos WHERE venda_id = ?", (venda_id,))
    pagamentos_custos = get_data_as_dataframe("SELECT * FROM pagamentos_custos WHERE venda_id = ?", (venda_id,))
    despesas_pagas = get_data_as_dataframe("SELECT * FROM despesas_pagas WHERE venda_id = ?", (venda_id,))
    config = get_config()

    custo_total = custo['custo_mcpf'] + custo['custo_madeireira']
    pagamentos_mcpf = pagamentos_custos[pagamentos_custos['tipo_fornecedor'] == 'MCPF']['valor'].sum()
    pagamentos_madeireira = pagamentos_custos[pagamentos_custos['tipo_fornecedor'] == 'Madeireira']['valor'].sum()
    custo_pago = pagamentos_mcpf + pagamentos_madeireira
    custo_pendente = custo_total - custo_pago

    despesas_detalhadas = {
        'royalties': venda['valor_venda'] * config.get('royalties', 0),
        'propaganda': venda['valor_venda'] * config.get('propaganda', 0),
        'simples': venda['valor_venda'] * config.get('simples', 0),
        'corretagem': venda['valor_venda'] * config.get('corretagem', 0),
        'admin': venda['valor_venda'] * config.get('admin', 0),
        'icms': custo_total * config.get('icms', 0)
    }
    despesas_total_calculado = sum(despesas_detalhadas.values())
    
    total_recebido = plano_recebimentos['valor_pago'].sum()
    saldo_a_receber = venda['valor_venda'] - total_recebido

    pagamentos_despesa_por_tipo = despesas_pagas.groupby('tipo_despesa')['valor'].sum().to_dict()
    total_despesas_pagas = despesas_pagas['valor'].sum()
    saldo_despesas_a_pagar = despesas_total_calculado - total_despesas_pagas

    lucro_bruto = venda['valor_venda'] - custo_total
    lucro_liquido = lucro_bruto - despesas_total_calculado
    
    return {
        'venda': venda, 'custo_total': custo_total, 'custo_pago': custo_pago, 'custo_pendente': custo_pendente,
        'custo_mcpf': custo['custo_mcpf'], 'pagamentos_mcpf': pagamentos_mcpf,
        'custo_madeireira': custo['custo_madeireira'], 'pagamentos_madeireira': pagamentos_madeireira,
        'despesas_detalhadas': despesas_detalhadas, 'despesas_total_calculado': despesas_total_calculado,
        'pagamentos_despesa_por_tipo': pagamentos_despesa_por_tipo,
        'total_recebido': total_recebido, 'saldo_a_receber': saldo_a_receber,
        'total_despesas_pagas': total_despesas_pagas, 'saldo_despesas_a_pagar': saldo_despesas_a_pagar,
        'lucro_bruto': lucro_bruto, 'lucro_liquido': lucro_liquido
    }

# calculations.py (substitua a função calculate_global_totals)

def calculate_global_totals():
    vendas_df = get_data_as_dataframe("SELECT * FROM vendas")
    total_saldo_bancario = get_total_saldo_bancario()

    if vendas_df.empty:
        base_dict = {key: 0 for key in [
            'total_vendas', 'total_recebido', 'total_a_receber', 'total_custos', 
            'total_despesas', 'lucro_bruto', 'lucro_liquido', 'percentual_lucro',
            'creditos_realizado', 'creditos_pendente', 'debitos_pago_custos', 
            'debitos_pago_despesas', 'total_pago_geral', 'debitos_pendente_custos', 
            'debitos_pendente_despesas', 'total_a_pagar_geral', 'saldo_realizado', 'balanco_futuro'
        ]}
        base_dict['total_saldo_bancario'] = total_saldo_bancario
        return base_dict
        
    all_totals = [calculate_venda_totals(venda_id) for venda_id in vendas_df['id']]

    total_vendas = vendas_df['valor_venda'].sum()
    total_custos = sum(t['custo_total'] for t in all_totals)
    total_despesas = sum(t['despesas_total_calculado'] for t in all_totals)
    lucro_bruto = total_vendas - total_custos
    lucro_liquido = lucro_bruto - total_despesas
    percentual_lucro = (lucro_liquido / total_vendas) * 100 if total_vendas > 0 else 0

    creditos_realizado = sum(t['total_recebido'] for t in all_totals)
    creditos_pendente = total_vendas - creditos_realizado

    debitos_pago_custos = sum(t['custo_pago'] for t in all_totals)
    debitos_pago_despesas = sum(t['total_despesas_pagas'] for t in all_totals)
    total_pago_geral = debitos_pago_custos + debitos_pago_despesas
    
    debitos_pendente_custos = total_custos - debitos_pago_custos
    debitos_pendente_despesas = total_despesas - debitos_pago_despesas
    total_a_pagar_geral = debitos_pendente_custos + debitos_pendente_despesas

    # --- NOVOS CÁLCULOS AGREGADOS ---
    total_disponivel = total_saldo_bancario + creditos_pendente
    provisao_saldo_final = total_disponivel - total_a_pagar_geral

    return {
        'total_vendas': total_vendas, 'total_recebido': creditos_realizado, 'total_a_receber': creditos_pendente,
        'total_custos': total_custos, 'total_despesas': total_despesas, 'lucro_bruto': lucro_bruto,
        'lucro_liquido': lucro_liquido, 'percentual_lucro': percentual_lucro,
        'total_saldo_bancario': total_saldo_bancario,
        'creditos_realizado': creditos_realizado, 'creditos_pendente': creditos_pendente,
        'debitos_pago_custos': debitos_pago_custos, 'debitos_pago_despesas': debitos_pago_despesas,
        'total_pago_geral': total_pago_geral,
        'debitos_pendente_custos': debitos_pendente_custos,
        'debitos_pendente_despesas': debitos_pendente_despesas,
        'total_a_pagar_geral': total_a_pagar_geral,
        'saldo_realizado': creditos_realizado - total_pago_geral,
        'balanco_futuro': creditos_pendente - total_a_pagar_geral,
        
        # Novas chaves para o dashboard estratégico
        'total_disponivel': total_disponivel,
        'provisao_saldo_final': provisao_saldo_final
    }
        
    all_totals = [calculate_venda_totals(venda_id) for venda_id in vendas_df['id']]

    total_vendas = vendas_df['valor_venda'].sum()
    total_custos = sum(t['custo_total'] for t in all_totals)
    total_despesas = sum(t['despesas_total_calculado'] for t in all_totals)
    
    lucro_bruto = total_vendas - total_custos
    lucro_liquido = lucro_bruto - total_despesas
    percentual_lucro = (lucro_liquido / total_vendas) * 100 if total_vendas > 0 else 0

    creditos_realizado = sum(t['total_recebido'] for t in all_totals)
    creditos_pendente = total_vendas - creditos_realizado

    debitos_pago_custos = sum(t['custo_pago'] for t in all_totals)
    debitos_pago_despesas = sum(t['total_despesas_pagas'] for t in all_totals)
    total_pago_geral = debitos_pago_custos + debitos_pago_despesas
    
    debitos_pendente_custos = total_custos - debitos_pago_custos
    debitos_pendente_despesas = total_despesas - debitos_pago_despesas
    total_a_pagar_geral = debitos_pendente_custos + debitos_pendente_despesas

    return {
        'total_vendas': total_vendas,
        'total_recebido': creditos_realizado,
        'total_a_receber': creditos_pendente,
        'total_custos': total_custos,
        'total_despesas': total_despesas,
        'lucro_bruto': lucro_bruto,
        'lucro_liquido': lucro_liquido,
        'percentual_lucro': percentual_lucro,
        'total_saldo_bancario': total_saldo_bancario,
        
        'creditos_realizado': creditos_realizado,
        'creditos_pendente': creditos_pendente,
        
        'debitos_pago_custos': debitos_pago_custos,
        'debitos_pago_despesas': debitos_pago_despesas,
        'total_pago_geral': total_pago_geral,

        'debitos_pendente_custos': debitos_pendente_custos,
        'debitos_pendente_despesas': debitos_pendente_despesas,
        'total_a_pagar_geral': total_a_pagar_geral,

        'saldo_realizado': creditos_realizado - total_pago_geral,
        'balanco_futuro': creditos_pendente - total_a_pagar_geral
    }