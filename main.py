"""Orquestrador principal."""
from pathlib import Path
from src.sqlite_loader import criar_banco
from src import etl
import gerar_dashboard, gerar_carteiras

def gerar_txt_inconsistencias():
    from src import analise
    c_baixa = [f for f in Path("dados").glob("*.txt") if "baixa" in f.name.lower()][0]
    c_aberto = [f for f in Path("dados").glob("*.txt") if "baixa" not in f.name.lower()][0]
    baixa = etl.carregar_baixa(str(c_baixa))
    aberto = etl.carregar_aberto(str(c_aberto))
    incons = analise.inconsistencias(baixa, aberto)
    
    data_str = etl.DATA_BASE.strftime("%Y%m%d")
    filename = f"output/INCONSISTENCIAS_DETECTADAS_{data_str}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"RELATÓRIO DE INCONSISTÊNCIAS - DATA-BASE: {etl.DATA_BASE.strftime('%d/%m/%Y')}\n" + "="*60 + "\n\n")
        f.write("EMISSÃO > VENCIMENTO\n*****************\n")
        for _, row in incons["emissao_maior_venc"].iterrows():
            f.write(f"Doc: {row['nro_documento']} | NF: {row['numero_nf']} | Cliente: {row['pessoa'][:30]}... | Emissão: {row['emissao'].strftime('%d/%m/%Y')} | Vencimento: {row['vencimento'].strftime('%d/%m/%Y')}\n")
        f.write("\n\nSALDOS NEGATIVOS (OVERPAYMENT)\n*********************\n")
        for _, row in incons["saldo_negativo"].iterrows():
            f.write(f"Doc: {row['nro_documento']} | NF: {row['numero_nf']} | Cliente: {row['pessoa'][:30]}... | Valor: R$ {row['valor_pgto']:.2f} | Saldo: R$ {row['saldo_cr']:.2f}\n")
    print(f"  [OK] {filename}")

def main():
    print("\n" + "="*60 + "\n  AUDITORIA FINANCEIRA - GRUPO SORTELUZ\n" + "="*60)
    
    print("\n[1/3] Criando Banco de Dados e TXT de Inconsistências...")
    c_baixa = [f for f in Path("dados").glob("*.txt") if "baixa" in f.name.lower()][0]
    c_aberto = [f for f in Path("dados").glob("*.txt") if "baixa" not in f.name.lower()][0]
    baixa = etl.carregar_baixa(str(c_baixa))
    aberto = etl.carregar_aberto(str(c_aberto))
    criar_banco(baixa, aberto)
    gerar_txt_inconsistencias()

    print("\n[2/3] Gerando Dashboard HTML Principal...")
    gerar_dashboard.executar()

    print("\n[3/3] Gerando Carteiras dos Vendedores...")
    gerar_carteiras.executar()

    print("\n" + "="*60)
    print("  CONCLUIDO! Verifique a pasta output/.")
    print("="*60)

if __name__ == "__main__":
    main()
