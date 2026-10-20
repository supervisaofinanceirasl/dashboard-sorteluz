import base64
from pathlib import Path
from src import etl, analise, dashboard, relatorio

def fmt_brl(val): return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def img_b64(fig):
    try: return base64.b64encode(fig.to_image(format="png", width=800, height=400, scale=1)).decode('utf-8')
    except Exception as e: 
        print(f"    [AVISO] Falha ao gerar imagem do gráfico: {e}")
        return ""

def executar():
    print("  Gerando PDF Executivo...")
    c_baixa = [f for f in Path("dados").glob("*.txt") if "baixa" in f.name.lower()][0]
    c_aberto = [f for f in Path("dados").glob("*.txt") if "baixa" not in f.name.lower()][0]
    baixa = etl.carregar_baixa(str(c_baixa))
    aberto = etl.carregar_aberto(str(c_aberto))

    kpis = analise.kpis_gerais(baixa, aberto)
    df_aging = analise.aging(aberto)
    df_top = analise.top_devedores(aberto)
    df_evolucao = analise.evolucao_cobranca(baixa, aberto)
    
    fig_cobranca = dashboard.graf_evolucao_cobranca(df_evolucao)
    fig_aging = dashboard.graf_aging(df_aging)

    ctx_pdf = {
        "data_base": etl.DATA_BASE.strftime("%d/%m/%Y"),
        "kpis": kpis,
        "img_cobranca": img_b64(fig_cobranca),
        "img_aging": img_b64(fig_aging),
        "tbl_top": df_top.head(10).style.format({'saldo': fmt_brl, 'encargos': fmt_brl}).hide(axis='index').to_html(classes="data"),
        "tbl_aging": df_aging.style.format({'saldo': fmt_brl, 'encargos': fmt_brl}).hide(axis='index').to_html(classes="data")
    }
    relatorio.gerar_pdf(ctx_pdf, "output/relatorio_executivo.pdf")
    print("  [OK] output/relatorio_executivo.pdf")
