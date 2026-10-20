from pathlib import Path
from src import etl, analise, relatorio

def fmt_brl(val): return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

TELEFONES_WPP = {
    "PAN XINGRONG": "558599873387",
    "FRANCISCO DE ASSIS MEDEIROS SILVA": "5584999509245",
    "ELIDIO CAVALCANTE LEITE FILHO": "5585999871571",
    "EDSON MORAIS DE ALBUQUERQUE": "5584999919599",
    "FRANCISCO CARLOS NOGUEIRA DE MELO": "5585997783311",
    "RUBENS FILHO": "5585988630570",
    "SIDNEY BARROS": "5585992314626",
    "KLEBER CARVALHO PACHECO": "5586999464999",
    "JUVENAL CHAVES DE OLIVEIRA": "558699750562",
    "IRANIL OLIVEIRA VIEIRA": "5583991315552",
    "RIVALDECY NASCIMENTO": "5583988046509",
    "JOSE OLIVEIRA DA SILVA": "5588999559233",
    "SAMIR DANIEL ALMEIDA TAVARES": "5582991517559",
    "JEFFERSON SOARES": "5584999045520",
    "MARCONI GOUVEIA RAMOS": "558199965427",
    "EDU REPRESENTACOES DE MATERIAIS DE CONSTRUCAO LTDA": "5581988657060",
    "GRUPO SORTE LUZ": "",
    "JOSE DANIEL FREITAS DA SILVA": "5585985174773",
    "F L L ANDRADE & CIA LTDA": "5588996366878",
    "NATAN RODRIGUES DOS SANTOS": "5585998262171",
    "O VIAJANTE ASSESSORIA E REPRESENTACOES LTDA": "5581998041818",
    "HELCIA REPRESENTACOES LTDA": "5588999486848",
    "SANDRO TAGLIONE DOS SANTOS": "5511965956884",
    "AJ REPRESENTACOES LTDA": "5521977245665",
    "S DAVI SENA REPRESENTACOES": "5594992864791",
    "GIUBERTI & MENDES REPRESENTACAO LTDA": "5598982042897",
    "56.423.653 MARIA LIDIANA LEITE DOS SANTOS": "5585997108662",
    "MC COMERCIO E REPRESENTAÇÃO LTDA": "5531986121313",
    "ALTA RELEVANCIA REPRESENTACOES COMERCIAIS LTDA": "5562982820582",
    "SRK REPRESENTACOES LTDA": "5584994190001",
    "ANTONIO EUGENIO DA PAIXAO NETO": "5584999550861",
    "MARIA DO PERPETUO DO SOCORRO DA SILVA RIPARDO LTDA": "5586999540718",
    "MAX VANDER FREIRE REPRESENTANTES COMERCIAIS E AGENTES DO COM": "5591984567285",
    "META REPRESENTACOES LTDA": "5579998276782",
    "AURI SILVA DO NASCIMENTO REPRESENTACAO COMERCIAL": "5581998590263",
    "ADRIANO COSTA SILVA REPRESENTACOES LTDA": "5575991399667",
    "J.S.L. REPRESENTACOES LTDA": "5571992043626",
    "F. PAZ REPRESENTACOES LTDA": "5585987102985",
    "ROCHA GUIMARAES REPRESENTACOES LTDA": "556299686801",
    "R8 REPRESENTACOES LTDA": "556181140600",
    "RP REPRESENTACAO LTDA": "559591650579",
    "DG REPRESENTACAO LTDA": "5592993218927",
    "ANTONIO DE SOUZA SALES": "5592991018220",
    "LORENA DELTA REPRESENTACOES LTDA": "5585988744000",
    "ARLESSON O. CALDEIRA": "5593991713647",
    "NASCIMENTO E CORTEZ LTDA": "5595991197436",
    "G. P. MARQUES & CIA LTDA": "5596984236335",
    "R N SOUZA NETO": "5596984128009",
    "RATHES COMERCIO, ENGENHARIA E REPRESENTACOES LTDA": "5594991599820",
    "PAULO J C LISBOA REPRESENTACOES": "5591982268832",
    "66.551.213 MATHEUS HENRIQUE DA SILVA": "5562983217581",
    "FOCUS REPRESENTACOES LTDA": "5596999114647",
    "F A M REPRESENTACOES LTDA": "5562996228046",
    "FRANCISCO DIAS REPRESENTACOES COMERCIAIS DE MATERIAL DE CONS": "5587988267304",
    "L C DA S ROCHA": "5569999639427",
    "L. MIQUILES DOS SANTOS NASCIMENTO": "5592993397973",
    "PEREIRA E MARINHO REPRESENTANTE COMERCIAL LTDA": "551935569600",
    "T C SOARES REPRESENTACOES": "5591985153633",
    "GABRIEL SOUSA VITORINO REPRESENTACOES LTDA": "5591982350261",
    "FILADELPHIA REPRESENTACOES COMERCIAIS DE TEXTEIS, VESTUARIO,": "5592981185171",
    "JMK REPRESENTACOES LTDA": "5594984083821",
    "FABIO FERREIRA DE OLIVEIRA - REPRESENTANTE COMERCIAL": "5599985395451"
}

def executar():
    print("  Gerando Carteiras Individuais...")
    c_aberto = [f for f in Path("dados").glob("*.txt") if "baixa" not in f.name.lower()][0]
    aberto = etl.carregar_aberto(str(c_aberto))
    df_vend = analise.por_vendedor(aberto)
    
    Path("output/carteiras").mkdir(exist_ok=True, parents=True)
    total_geral_inad = df_vend["saldo"].sum()
    links_carteira = []
    
    for _, row in df_vend.iterrows():
        vendedor = row["vendedor"]
        df_v = aberto[aberto["vendedor"] == vendedor].copy().sort_values("vencimento", ascending=False)
        df_v_tab = df_v[["vencimento", "pessoa", "nro_documento", "numero_nf", "forma_pgto", "saldo_cr", "dias_calc"]]
        df_v_tab["vencimento"] = df_v_tab["vencimento"].dt.strftime('%d/%m/%Y')
        
        tab_html = df_v_tab.style.format({"saldo_cr": fmt_brl}).hide(axis='index').to_html(classes="tbl")
        safe_name = "".join([c if c.isalnum() else "_" for c in vendedor])[:30]
        
        telefone = TELEFONES_WPP.get(vendedor, "")
        formas_vend = analise.formas_por_vendedor(aberto, vendedor)
        
        relatorio.gerar_carteira_html({
            "vendedor": vendedor, "data_base": etl.DATA_BASE.strftime("%d/%m/%Y"),
            "total": row["saldo"], "qtd": len(df_v), "pct": (row["saldo"]/total_geral_inad)*100,
            "ticket": row["saldo"]/len(df_v) if len(df_v)>0 else 0, "clientes": df_v["pessoa"].nunique(),
            "tabela": tab_html, "formas_vendedor": formas_vend, "telefone_wpp": telefone
        }, f"output/carteiras/carteira_{safe_name}.html")
        links_carteira.append(f'<li><a href="carteira_{safe_name}.html">{vendedor}</a> - {fmt_brl(row["saldo"])}</li>')

    html_index = f"""
    <html><head><meta charset="UTF-8"><title>Índice de Carteiras</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap" rel="stylesheet">
    <style>body{{font-family:'Outfit',sans-serif;padding:40px;background:#f4f7f6;}} h1{{color:#d31a21;}} a{{color:#f26522;text-decoration:none;font-weight:bold;}} li{{margin-bottom:10px;}}</style>
    </head><body>
    <h1>Índice de Carteiras por Vendedor</h1>
    <ul>{''.join(links_carteira)}</ul>
    <br><a href='../relatorio.html'>Voltar ao Dashboard Geral</a>
    </body></html>
    """
    Path("output/carteiras/index.html").write_text(html_index, encoding="utf-8")
    print(f"  [OK] {len(df_vend)} carteiras geradas em output/carteiras/")
