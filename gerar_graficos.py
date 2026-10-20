"""Script exclusivo para geração de todos os gráficos do dashboard."""
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import base64

CORES = {
    "primaria": "#f26522", "secundaria": "#d31a21", "destaque": "#fdb913",
    "bg_escuro": "#1a1a1a", "bg_grafico": "#2a2a2a", "texto_claro": "#e0e0e0"
}

def fmt_brl_curto(val):
    if val >= 1000000: return f"{val/1000000:.1f}M".replace(".", ",")
    if val >= 1000: return f"{val/1000:.0f}K"
    return f"{val:.0f}"

def fig_to_base64(fig):
    try:
        img_bytes = fig.to_image(format="png", width=1100, height=600, scale=2)
        return base64.b64encode(img_bytes).decode('utf-8')
    except Exception as e:
        print(f"Erro ao gerar imagem: {e}")
        return ""

def graf_cobranca_diaria(df, ano_mes):
    # Inverter a ordem para que o dia 01 fique no topo
    df = df.iloc[::-1]
    
    fig = go.Figure()
    
    text_rec = [f"{fmt_brl_curto(v)} | {q}T | {p:.0f}%" if v > 0 else "" for v, q, p in zip(df["valor_pgto"], df["qtd_pgto"], df["pct_pgto"])]
    text_inad = [f"{fmt_brl_curto(v)} | {q}T | {p:.0f}%" if v > 0 else "" for v, q, p in zip(df["valor_cr"], df["qtd_inad"], df["pct_cr"])]
    
    fig.add_trace(go.Bar(
        y=df["data"], x=df["valor_pgto"], name='Recuperação', orientation='h',
        marker_color='#70ad47', text=text_rec,
        textposition='outside', textfont=dict(size=12, color='#70ad47'),
        constraintext='none'
    ))
    fig.add_trace(go.Bar(
        y=df["data"], x=df["valor_cr"], name='Aumento Inadimplência', orientation='h',
        marker_color='#c00000', text=text_inad,
        textposition='outside', textfont=dict(size=12, color='#c00000'),
        constraintext='none'
    ))
    
    fig.update_layout(
        template='plotly_dark', paper_bgcolor=CORES["bg_escuro"], plot_bgcolor=CORES["bg_grafico"],
        font=dict(family="Outfit, sans-serif", color=CORES["texto_claro"]),
        margin=dict(t=30, l=120, r=20, b=30),
        title=None, barmode='group', height=650,
        yaxis=dict(type='category', title=None, tickfont=dict(size=11)),
        xaxis=dict(title="Valor (R$)", title_font=dict(size=12), automargin=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=13))
    )
    return fig

def graf_cobranca_mensal(df, ano):
    df = df.iloc[::-1]
    
    fig = go.Figure()
    
    text_rec = [f"{fmt_brl_curto(v)} | {q}T | {p:.0f}%" if v > 0 else "" for v, q, p in zip(df["valor_pgto"], df["qtd_pgto"], df["pct_pgto"])]
    text_inad = [f"{fmt_brl_curto(v)} | {q}T | {p:.0f}%" if v > 0 else "" for v, q, p in zip(df["valor_cr"], df["qtd_inad"], df["pct_cr"])]
    
    fig.add_trace(go.Bar(
        y=df["mes"], x=df["valor_pgto"], name='Recuperação', orientation='h',
        marker_color='#70ad47', text=text_rec,
        textposition='outside', textfont=dict(size=12, color='#70ad47'),
        constraintext='none'
    ))
    fig.add_trace(go.Bar(
        y=df["mes"], x=df["valor_cr"], name='Aumento Inadimplência', orientation='h',
        marker_color='#c00000', text=text_inad,
        textposition='outside', textfont=dict(size=12, color='#c00000'),
        constraintext='none'
    ))
    
    fig.update_layout(
        template='plotly_dark', paper_bgcolor=CORES["bg_escuro"], plot_bgcolor=CORES["bg_grafico"],
        font=dict(family="Outfit, sans-serif", color=CORES["texto_claro"]),
        margin=dict(t=30, l=80, r=20, b=30),
        title=None, barmode='group', height=500,
        yaxis=dict(type='category', title=None, tickfont=dict(size=11)),
        xaxis=dict(title="Valor (R$)", title_font=dict(size=12), automargin=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=13))
    )
    return fig

def graf_aging(df_aging):
    fig = px.bar(df_aging, x="faixa", y="saldo", text_auto=".2s", title="Aging List", color="faixa", color_discrete_sequence=px.colors.sequential.Oranges_r, template='plotly_dark')
    fig.update_layout(template='plotly_dark', paper_bgcolor=CORES["bg_escuro"], plot_bgcolor=CORES["bg_grafico"], font=dict(family="Outfit, sans-serif", color=CORES["texto_claro"]), margin=dict(t=50, l=40, r=20, b=40), showlegend=False, height=400, xaxis_title="", yaxis_title="Saldo (R$)")
    fig.update_traces(marker_line_width=0, marker_line_color=None, textposition='outside', textfont=dict(color=CORES["texto_claro"]))
    return fig

def graf_top_devedores(df):
    fig = px.bar(df.sort_values("saldo"), x="saldo", y="pessoa", orientation="h", text_auto=".2s", title="Top 20 Devedores", color="saldo", color_continuous_scale="Reds", template='plotly_dark')
    fig.update_layout(template='plotly_dark', paper_bgcolor=CORES["bg_escuro"], plot_bgcolor=CORES["bg_grafico"], font=dict(family="Outfit, sans-serif", color=CORES["texto_claro"]), margin=dict(t=50, l=40, r=20, b=40), height=650, yaxis_title="", coloraxis_showscale=False)
    fig.update_traces(marker_line_width=0, marker_line_color=None)
    return fig

def graf_vendedores(df):
    fig = px.bar(df.head(20).sort_values("saldo"), x="saldo", y="vendedor", orientation="h", text_auto=".2s", title="Ranking por Vendedor - TOP 20", color="saldo", color_continuous_scale="Oranges", template='plotly_dark')
    fig.update_layout(template='plotly_dark', paper_bgcolor=CORES["bg_escuro"], plot_bgcolor=CORES["bg_grafico"], font=dict(family="Outfit, sans-serif", color=CORES["texto_claro"]), margin=dict(t=50, l=40, r=20, b=40), height=650, yaxis_title="", coloraxis_showscale=False)
    fig.update_traces(marker_line_width=0, marker_line_color=None)
    return fig

def graf_evo_emissao(aberto):
    df = (aberto.assign(mes=aberto["emissao"].dt.strftime("%Y-%m")).groupby("mes").agg(saldo=("saldo_cr", "sum")).reset_index()).sort_values("mes")
    fig = px.bar(df, x="mes", y="saldo", text_auto=".2s", title="Faturamento (Emissão)", color_discrete_sequence=[CORES["primaria"]], template='plotly_dark')
    fig.update_layout(template='plotly_dark', paper_bgcolor=CORES["bg_escuro"], plot_bgcolor=CORES["bg_grafico"], font=dict(family="Outfit, sans-serif", color=CORES["texto_claro"]), margin=dict(t=50, l=40, r=20, b=40), height=350, xaxis=dict(type='category'))
    fig.update_traces(marker_line_width=0, marker_line_color=None, textposition='outside', textfont=dict(color=CORES["texto_claro"]))
    return fig

def graf_evo_vencimento(aberto):
    df = (aberto.assign(mes=aberto["vencimento"].dt.strftime("%Y-%m")).groupby("mes").agg(saldo=("saldo_cr", "sum")).reset_index()).sort_values("mes")
    fig = px.bar(df, x="mes", y="saldo", text_auto=".2s", title="Inadimplência (Vencimento)", color_discrete_sequence=[CORES["secundaria"]], template='plotly_dark')
    fig.update_layout(template='plotly_dark', paper_bgcolor=CORES["bg_escuro"], plot_bgcolor=CORES["bg_grafico"], font=dict(family="Outfit, sans-serif", color=CORES["texto_claro"]), margin=dict(t=50, l=40, r=20, b=40), height=350, xaxis=dict(type='category'))
    fig.update_traces(marker_line_width=0, marker_line_color=None, textposition='outside', textfont=dict(color=CORES["texto_claro"]))
    return fig

