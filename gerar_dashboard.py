import base64
from pathlib import Path
import pandas as pd
import plotly.io as pio
from src import etl, analise, relatorio
import gerar_graficos

def executar():
    print("  Gerando Dashboard HTML Unificado...")
    c_baixa = [f for f in Path("dados").glob("*.txt") if "baixa" in f.name.lower()][0]
    c_aberto = [f for f in Path("dados").glob("*.txt") if "baixa" not in f.name.lower()][0]
    baixa_total = etl.carregar_baixa(str(c_baixa))
    aberto_total = etl.carregar_aberto(str(c_aberto))

    logo_base64 = base64.b64encode(open("logo.jpg", "rb").read()).decode('utf-8') if Path("logo.jpg").exists() else ""
    
    empresas = {
        "Visão Geral": (baixa_total, aberto_total),
        "EC Comércio": (baixa_total[baixa_total["empresa"] == "EC COMERCIO"], aberto_total[aberto_total["empresa"] == "EC COMERCIO"]),
        "MP Matriz": (baixa_total[baixa_total["empresa"] == "MP MATRIZ"], aberto_total[aberto_total["empresa"] == "MP MATRIZ"]),
        "MP Filial": (baixa_total[baixa_total["empresa"] == "MP FILIAL"], aberto_total[aberto_total["empresa"] == "MP FILIAL"]),
    }

    contexts = {}
    
    for empresa_nome, (baixa, aberto) in empresas.items():
        if aberto.empty:
            continue
            
        kpis = analise.kpis_gerais(baixa, aberto)
        kpis_formas = analise.kpis_formas(aberto)
        
        ultima_data, ultimo_mes, ultimo_ano = analise.obter_ultimo_periodo(baixa, aberto)
        
        df_diario = analise.evolucao_cobranca_diaria(baixa, aberto, ultimo_mes, ultima_data)
        df_mensal = analise.evolucao_cobranca_mensal(baixa, aberto, ultimo_ano)
        
        fig_diario = gerar_graficos.graf_cobranca_diaria(df_diario, ultimo_mes)
        fig_mensal = gerar_graficos.graf_cobranca_mensal(df_mensal, ultimo_ano)

        # O PRIMEIRO GRÁFICO DO PRIMEIRO CONTEXTO EMBUTE O PLOTLY (include_plotlyjs=True)
        # Os demais usam False para não duplicar a biblioteca.
        include_js_diario = True if empresa_nome == "Visão Geral" else False
        
        # Para o gráfico mensal, nunca precisamos incluir o JS novamente
        include_js_mensal = False

        def calc_resumo(df):
            rec = df["valor_pgto"].sum()
            inad = df["valor_cr"].sum()
            qtd_rec = df["qtd_pgto"].sum()
            qtd_inad = df["qtd_inad"].sum()
            pct_rec = (rec / kpis["total_aberto"] * 100) if kpis["total_aberto"] > 0 else 0
            pct_inad = (inad / kpis["total_aberto"] * 100) if kpis["total_aberto"] > 0 else 0
            saldo = inad - rec
            pct_saldo = (saldo / kpis["total_aberto"] * 100) if kpis["total_aberto"] > 0 else 0
            qtd_saldo = int(qtd_inad - qtd_rec) if qtd_inad > qtd_rec else 0
            return {"rec": rec, "qtd_rec": int(qtd_rec), "pct_rec": pct_rec, "inad": inad, "qtd_inad": int(qtd_inad), "pct_inad": pct_inad, "saldo": saldo, "qtd_saldo": qtd_saldo, "pct_saldo": pct_saldo}

        resumo_mes = calc_resumo(df_diario)
        resumo_ano = calc_resumo(df_mensal)

        df_aging = analise.aging(aberto)
        df_top = analise.top_devedores(aberto)
        df_vend = analise.por_vendedor(aberto)
        df_prioritarios = analise.clientes_prioritarios(baixa, aberto)
        df_aging_det = analise.aging_detalhado(aberto)
        
        fig_aging = gerar_graficos.graf_aging(df_aging)
        fig_top = gerar_graficos.graf_top_devedores(df_top)
        fig_vend = gerar_graficos.graf_vendedores(df_vend)
        fig_evo_emi = gerar_graficos.graf_evo_emissao(aberto)
        fig_evo_ven = gerar_graficos.graf_evo_vencimento(aberto)

        def fmt_brl(val): return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        def fmt_pct(val): return f"{val:,.2f}%".replace(".", ",")

        tbl_prio = df_prioritarios.style.format({'total_pago': fmt_brl, 'saldo_devedor': fmt_brl, 'atraso_medio': '{:,.0f} dias'}).hide(axis='index').to_html(classes="tbl") if not df_prioritarios.empty else "<p>Nenhum cliente.</p>"
        tbl_vend = df_vend.style.format({'saldo': fmt_brl, 'atraso_medio': '{:,.0f}', 'pct_total': fmt_pct}).hide(axis='index').to_html(classes="tbl")
        tbl_forma = pd.DataFrame(kpis_formas).style.format({'saldo': fmt_brl, 'pct': fmt_pct}).hide(axis='index').to_html(classes="tbl")

        detalhes_aging = {}
        for faixa in df_aging_det["faixa"].unique():
            sub = df_aging_det[df_aging_det["faixa"] == faixa][["vencimento", "pessoa", "vendedor", "nro_documento", "forma_pgto", "saldo_cr", "dias_calc"]]
            detalhes_aging[str(faixa)] = sub.style.format({"vencimento": lambda x: x.strftime('%d/%m/%Y'), "saldo_cr": fmt_brl}).hide(axis='index').to_html(classes="tbl")

        contexts[empresa_nome] = {
            "kpis": kpis, "formas": kpis_formas, "mes_ref": ultimo_mes, "ano_ref": ultimo_ano,
            "resumo_mes": resumo_mes, "resumo_ano": resumo_ano, 
            "graf_diario": pio.to_html(fig_diario, full_html=False, include_plotlyjs=include_js_diario),
            "graf_mensal": pio.to_html(fig_mensal, full_html=False, include_plotlyjs=include_js_mensal),
            "graf_aging": pio.to_html(fig_aging, full_html=False, include_plotlyjs=False),
            "graf_top": pio.to_html(fig_top, full_html=False, include_plotlyjs=False),
            "graf_vend": pio.to_html(fig_vend, full_html=False, include_plotlyjs=False),
            "graf_evo_emissao": pio.to_html(fig_evo_emi, full_html=False, include_plotlyjs=False),
            "graf_evo_vencimento": pio.to_html(fig_evo_ven, full_html=False, include_plotlyjs=False),
            "tbl_prioritarios": tbl_prio, "tbl_vend": tbl_vend, "tbl_forma": tbl_forma,
            "tbl_aging": df_aging.style.format({'saldo': fmt_brl}).hide(axis='index').to_html(classes="tbl"),
            "tbl_top": df_top.style.format({'saldo': fmt_brl, 'atraso_medio': '{:,.0f}'}).hide(axis='index').to_html(classes="tbl"),
            "detalhes_aging": detalhes_aging
        }

    relatorio.gerar_main_html(contexts, etl.DATA_BASE.strftime("%d/%m/%Y"), logo_base64, "output/relatorio.html")
    print(f"  [OK] output/relatorio.html (Arquivo Único gerado com Sucesso!)")
