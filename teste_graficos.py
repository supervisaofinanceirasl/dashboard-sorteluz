import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import plotly.io as pio

# Regras exatas solicitadas
def gerar_dados(baixa, aberto):
    # 1. Recuperação: Dias > 0 (Pagos com atraso)
    b = baixa[baixa["dias"] > 0].copy()
    b["data"] = b["dt_pagamento"].dt.strftime("%Y-%m-%d")
    rec = b.groupby("data").agg(rec_valor=("valor_pgto", "sum"), rec_qtd=("nro_documento", "count")).reset_index()

    # 2. Aumento de Inadimplência: Vencidos e não pagos (dias_calc > 0)
    a = aberto[aberto["dias_calc"] > 0].copy()
    a["data"] = a["vencimento"].dt.strftime("%Y-%m-%d")
    inad = a.groupby("data").agg(inad_valor=("valor_cr", "sum"), inad_qtd=("nro_documento", "count")).reset_index()

    # Cruzamento
    df = pd.merge(rec, inad, on="data", how="outer").fillna(0)
    df["data_obj"] = pd.to_datetime(df["data"])
    df = df.sort_values("data_obj").drop(columns=["data_obj"])
    return df

# Lendo os arquivos
c_baixa = [f for f in Path("dados").glob("*.txt") if "baixa" in f.name.lower()][0]
c_aberto = [f for f in Path("dados").glob("*.txt") if "baixa" not in f.name.lower()][0]

# Simulação do ETL (para o teste rodar sozinho)
from src import etl
baixa = etl.carregar_baixa(str(c_baixa))
aberto = etl.carregar_aberto(str(c_aberto))

df_cruzado = gerar_dados(baixa, aberto)

# Filtrando para os últimos meses para não embolar o gráfico de teste
df_teste = df_cruzado.tail(30) 

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_teste["data"], y=df_teste["rec_valor"], mode='lines+markers', name='Recuperação (Pago c/ Atraso)', line=dict(color='#70ad47', width=3)))
fig.add_trace(go.Scatter(x=df_teste["data"], y=df_teste["inad_valor"], mode='lines+markers', name='Aumento de Inadimplência', line=dict(color='#c00000', width=3)))

fig.update_layout(title="Teste do Termômetro da Cobrança (Últimos 30 dias com movimentação)", template="plotly_dark", height=500)

html = pio.to_html(fig, full_html=True)
Path("output/teste_grafico.html").write_text(html, encoding="utf-8")
print("✅ Gráfico de teste gerado com sucesso em: output/teste_grafico.html")
