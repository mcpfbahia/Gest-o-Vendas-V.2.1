# pdf_generator.py (Versão otimizada para uma página)
from fpdf import FPDF
from datetime import datetime

def format_brl(value):
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ 0,00"

class PDF(FPDF):
    def header(self):
        # --- Configurações de Altura (sem alteração) ---
        TEXT_BLOCK_HEIGHT = 22; LOGO_HEIGHT = 25
        initial_y = self.get_y()
        try:
            self.image('logo.png', x=160, y=initial_y, h=LOGO_HEIGHT)
        except FileNotFoundError:
            self.set_xy(160, initial_y); self.set_font('Arial', 'I', 8)
            self.multi_cell(40, 5, "Arquivo 'logo.png' nao encontrado.", 0, 'R')
        text_y_offset = (LOGO_HEIGHT - TEXT_BLOCK_HEIGHT) / 2
        self.set_y(initial_y + text_y_offset)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 7, 'WOODBAHIA CASAS PREFABRICADAS', 0, 1, 'L')
        self.set_font('Arial', '', 9)
        self.cell(0, 5, 'CNPJ: 57.721.838.0001/91', 0, 1, 'L')
        self.cell(0, 5, 'Rodovia Ba 099 Eco Posto Shell Est. do Coco, Abrantes', 0, 1, 'L')
        self.cell(0, 5, 'Camacari Bahia - Cel 71 99293-6290', 0, 1, 'L')
        self.set_y(initial_y + LOGO_HEIGHT + 5) # AJUSTE: Margem inferior reduzida
        self.set_font('Arial', 'B', 16) # AJUSTE: Fonte do título principal reduzida
        self.cell(0, 10, 'RECIBO DE VENDA E STATUS FINANCEIRO', 0, 1, 'C')
        self.ln(3) # AJUSTE: Espaçamento reduzido

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cell(0, 10, f'Documento emitido em {data_emissao}', 0, 0, 'L')
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def gerar_recibo_venda(dados_venda):
    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    # --- Introdução ---
    pdf.set_font('Arial', '', 10) # AJUSTE: Fonte reduzida
    pdf.multi_cell(0, 5, # AJUSTE: Altura da linha reduzida
        f"Este documento certifica e detalha a transação comercial e o status financeiro atual referente à aquisição do produto/serviço descrito abaixo, celebrado entre a WOODBAHIA CASAS PREFABRICADAS e o(a) cliente.",
        0, 'J'
    )
    pdf.ln(5) # AJUSTE: Espaçamento reduzido
    
    # --- Dados do Cliente ---
    pdf.set_font('Arial', 'B', 12) # AJUSTE: Fonte do título da seção reduzida
    pdf.cell(0, 8, '1. Identificacao do Cliente', 0, 1, 'L') # AJUSTE: Altura da célula reduzida
    pdf.set_font('Arial', '', 10) # AJUSTE: Fonte do corpo reduzida
    pdf.cell(20, 6, 'Nome:') # AJUSTE: Altura da célula reduzida
    pdf.cell(0, 6, f"{dados_venda['cliente']}", 0, 1)
    pdf.cell(20, 6, 'Telefone:')
    pdf.cell(0, 6, f"{dados_venda.get('telefone', 'N/A')}", 0, 1)
    pdf.cell(20, 6, 'Email:')
    pdf.cell(0, 6, f"{dados_venda.get('email', 'N/A')}", 0, 1)
    pdf.ln(5)

    # --- Detalhes da Venda ---
    pdf.set_font('Arial', 'B', 12) # AJUSTE: Fonte do título da seção reduzida
    pdf.cell(0, 8, '2. Detalhes do Contrato', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(40, 6, 'Nº do Contrato/Venda:')
    pdf.cell(0, 6, f"#{dados_venda['id']}", 0, 1)
    pdf.cell(40, 6, 'Data da Contratacao:')
    pdf.cell(0, 6, f"{dados_venda['data_venda']}", 0, 1)
    pdf.cell(40, 6, 'Objeto do Contrato:')
    pdf.cell(0, 6, f"{dados_venda['nome_kit']}", 0, 1)
    pdf.ln(5)

    # --- Status Financeiro Detalhado ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '3. Status Financeiro do Contrato', 0, 1, 'L')
    
    valor_total = dados_venda['valor_venda'] + dados_venda['valor_frete']
    total_pago = sum(pag.get('valor_pago', 0) for pag in dados_venda.get('pagamentos', []) if pag['status'] == 'Pago')
    saldo_devedor = valor_total - total_pago
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(60, 6, 'Valor Total do Contrato (Kit + Frete):')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, format_brl(valor_total), 0, 1, 'R')
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(60, 6, 'Total de Pagamentos Confirmados:')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, format_brl(total_pago), 0, 1, 'R')
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(220, 53, 69)
    pdf.cell(60, 8, 'SALDO DEVEDOR:')
    pdf.cell(0, 8, format_brl(saldo_devedor), 0, 1, 'R')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    percentual_quitado = (total_pago / valor_total) * 100 if valor_total > 0 else 0
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 5, f'Progresso de Quitacao: {percentual_quitado:.2f}%', 0, 1)
    pdf.set_fill_color(224, 224, 224)
    pdf.cell(190, 5, '', 'B', 1, 'L', 1)
    pdf.set_y(pdf.get_y() - 5)
    pdf.set_fill_color(76, 175, 80)
    pdf.cell(190 * (percentual_quitado / 100.0), 5, '', 'B', 1, 'L', 1)
    pdf.ln(5)

    # --- Histórico de Pagamentos ---
    if dados_venda.get('pagamentos'):
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, '4. Historico de Pagamentos', 0, 1, 'L')
        pdf.set_font('Arial', 'B', 10)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(40, 6, 'Data', 1, 0, 'C', 1)
        pdf.cell(60, 6, 'Forma de Pagamento', 1, 0, 'C', 1)
        pdf.cell(40, 6, 'Valor Pago', 1, 1, 'C', 1)
        
        pdf.set_font('Arial', '', 9)
        for pag in dados_venda.get('pagamentos', []):
            if pag['status'] == 'Pago':
                pdf.cell(40, 6, pag.get('data_pagamento', 'N/A'), 1, 0, 'C')
                pdf.cell(60, 6, pag.get('forma_pagamento', 'N/A'), 1, 0, 'C')
                pdf.cell(40, 6, format_brl(pag.get('valor_pago', 0)), 1, 1, 'R')

    pdf.ln(10)
    pdf.cell(0, 8, '________________________________________', 0, 1, 'C')
    pdf.cell(0, 6, f"Assinatura do(a) Cliente: {dados_venda['cliente']}", 0, 1, 'C')

    return bytes(pdf.output())