import streamlit as st
import numpy as np
import plotly.graph_objects as go
from itertools import combinations
import math
import base64
from pathlib import Path

st.set_page_config(
    page_title="MathErgy | Akıllı Enerji Paylaşımı",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_logo_b64():
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()
logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" style="height:72px; margin-bottom:8px;">'
    if logo_b64 else "⚡"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
:root {
    --gold:#F5A623; --green:#27AE60; --blue:#2980B9;
    --dark:#0D1117; --card:#161B22; --border:#30363D;
    --text:#E6EDF3; --muted:#8B949E;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:var(--dark);color:var(--text);}
h1,h2,h3{font-family:'Syne',sans-serif;}
.hero{background:linear-gradient(135deg,#0D1117 0%,#1a2332 60%,#0D1117 100%);border:1px solid var(--border);border-radius:16px;padding:40px 36px;margin-bottom:28px;position:relative;overflow:hidden;}
.hero-title{font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;line-height:1.1;background:linear-gradient(90deg,#27AE60,#F5A623,#2980B9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-sub{font-size:1.05rem;color:var(--muted);margin-top:10px;font-weight:300;}
.badge{display:inline-block;border-radius:20px;padding:3px 13px;font-size:.76rem;font-weight:600;margin:3px 4px 3px 0;}
.badge-gold{background:rgba(245,166,35,.15);border:1px solid rgba(245,166,35,.4);color:var(--gold);}
.badge-green{background:rgba(39,174,96,.13);border:1px solid rgba(39,174,96,.4);color:#4ecb7f;}
.badge-blue{background:rgba(41,128,185,.13);border:1px solid rgba(41,128,185,.4);color:#5dade2;}
.mcard{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:22px 18px;text-align:center;transition:border-color .2s;}
.mcard:hover{border-color:var(--gold);}
.mcard-val{font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:700;color:var(--gold);}
.mcard-lbl{font-size:.80rem;color:var(--muted);margin-top:3px;}
.sec{font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:700;padding-bottom:6px;border-bottom:2px solid var(--gold);display:inline-block;margin:24px 0 14px;}
.sh-row{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px 14px;margin-bottom:7px;display:flex;align-items:center;gap:12px;}
.sh-bar-bg{flex:1;height:8px;background:#30363D;border-radius:4px;}
.sh-val{font-family:'Syne',sans-serif;font-weight:700;min-width:52px;text-align:right;font-size:.95rem;}
.ibox{background:rgba(39,174,96,.07);border:1px solid rgba(39,174,96,.28);border-radius:10px;padding:14px 18px;color:#a8e6bf;font-size:.87rem;margin-bottom:12px;}
section[data-testid="stSidebar"]{background:#0D1117 !important;border-right:1px solid var(--border);}
.stButton>button{background:linear-gradient(135deg,#27AE60,#1e8449);color:#fff;font-weight:700;border:none;border-radius:8px;font-family:'Syne',sans-serif;width:100%;padding:10px 0;}
</style>
""", unsafe_allow_html=True)

RENKLER = ["#F5A623","#27AE60","#3498DB","#9B59B6","#E74C3C","#1ABC9C"]
HAVA_OPT = ["☀️ Güneşli","⛅ Parçalı Bulutlu","☁️ Bulutlu","🌧️ Yağmurlu"]
HAVA_K   = {"☀️ Güneşli":1.0,"⛅ Parçalı Bulutlu":0.65,"☁️ Bulutlu":0.35,"🌧️ Yağmurlu":0.15}

def shapley(uretim):
    n = len(uretim)
    phi = [0.0] * n
    for i in range(n):
        diger = [j for j in range(n) if j != i]
        for r in range(n):
            for coal in combinations(diger, r):
                coal = list(coal)
                v_with    = sum(uretim[j] for j in coal + [i])
                v_without = sum(uretim[j] for j in coal)
                w = math.factorial(r) * math.factorial(n-r-1) / math.factorial(n)
                phi[i] += w * (v_with - v_without)
    return phi

def sim(n_hane, panel_guc, hava):
    rng = np.random.default_rng()
    k   = HAVA_K[hava]
    uretim  = [round(g * k * rng.uniform(0.88,1.0), 2) for g in panel_guc]
    tuketim = [round(rng.uniform(1.5, 5.0), 2) for _ in range(n_hane)]
    net     = [round(u - t, 2) for u, t in zip(uretim, tuketim)]
    phi     = shapley(uretim)
    tot_u   = sum(uretim)
    tot_t   = sum(tuketim)
    return dict(
        uretim=uretim, tuketim=tuketim, net=net, shapley=phi,
        tot_u=tot_u, tot_t=tot_t,
        fazla=round(max(0, tot_u-tot_t), 2),
        bagimsi=round(min(100, tot_u/max(tot_t,.01)*100), 1),
        tasarruf=round(min(tot_u, tot_t)*0.85, 2),
    )

with st.sidebar:
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="width:100%;max-width:220px;margin-bottom:16px;">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Sistem Parametreleri")
    n_hane = st.slider("🏠 Hane Sayısı", 2, 6, 4)
    hava   = st.selectbox("🌤️ Hava Durumu", HAVA_OPT)
    st.markdown("**☀️ Panel Güçleri (kW)**")
    panel_guc = []
    for i in range(n_hane):
        g = st.slider(f"Hane {i+1}", 1.0, 10.0, 4.0+i*0.5, 0.5, key=f"p{i}")
        panel_guc.append(g)
    simule = st.button("🔄 Simülasyonu Çalıştır")
    st.divider()
    st.caption("TÜBİTAK 4006 · 2026")

if "s" not in st.session_state or simule:
    st.session_state.s = sim(n_hane, panel_guc, hava)
    st.session_state.n = n_hane

s = st.session_state.s
n = st.session_state.n
haneler = [f"Hane {i+1}" for i in range(n)]

st.markdown(f"""
<div class="hero">
    <div>{logo_html}</div>
    <div style="margin-bottom:10px;">
        <span class="badge badge-gold">TÜBİTAK 4006</span>
        <span class="badge badge-green">Matematik · Enerji</span>
        <span class="badge badge-blue">Tasarım Araştırma</span>
    </div>
    <p class="hero-title">MathErgy <sup style="font-size:1rem;">212510</sup></p>
    <p class="hero-sub">Mahalle Ölçeğinde Akıllı Enerji Paylaşımı ve Optimizasyon Simülatörü</p>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4,c5 = st.columns(5)
for col, val, lbl in [
    (c1, f"{s['tot_u']:.1f} kW",  "☀️ Toplam Üretim"),
    (c2, f"{s['tot_t']:.1f} kW",  "🏠 Toplam Tüketim"),
    (c3, f"{s['fazla']:.1f} kW",  "🔋 Fazla Enerji"),
    (c4, f"%{s['bagimsi']}",       "📈 Şebeke Bağımsızlığı"),
    (c5, f"{s['tasarruf']:.1f} ₺","💰 Tahmini Tasarruf"),
]:
    with col:
        st.markdown(f'<div class="mcard"><div class="mcard-val">{val}</div><div class="mcard-lbl">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

g1,g2 = st.columns([3,2])
with g1:
    st.markdown('<p class="sec">📊 Üretim & Tüketim</p>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_bar(name="Üretim (kW)", x=haneler, y=s["uretim"], marker_color=RENKLER[:n], opacity=.9)
    fig.add_bar(name="Tüketim (kW)", x=haneler, y=s["tuketim"], marker_color=["rgba(255,255,255,.18)"]*n, marker_line_color="white", marker_line_width=1.2)
    fig.update_layout(barmode="group",height=300,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#E6EDF3",margin=dict(l=0,r=0,t=6,b=0),legend=dict(bgcolor="rgba(0,0,0,0)",orientation="h",y=1.08),xaxis=dict(gridcolor="#30363D"),yaxis=dict(gridcolor="#30363D",title="kW"))
    st.plotly_chart(fig, use_container_width=True)

with g2:
    st.markdown('<p class="sec">🔋 Üretim Dağılımı</p>', unsafe_allow_html=True)
    fig_pie = go.Figure(go.Pie(labels=haneler,values=s["uretim"],marker_colors=RENKLER[:n],hole=.52,textinfo="percent+label",textfont_size=12))
    fig_pie.update_layout(height=300,showlegend=False,paper_bgcolor="rgba(0,0,0,0)",font_color="#E6EDF3",margin=dict(l=0,r=0,t=6,b=0),annotations=[dict(text="Üretim",x=.5,y=.5,font_size=14,font_color="#F5A623",showarrow=False)])
    st.plotly_chart(fig_pie, use_container_width=True)

g3,g4 = st.columns([3,2])
with g3:
    st.markdown('<p class="sec">⚡ Net Enerji Dengesi</p>', unsafe_allow_html=True)
    net_renk = [RENKLER[i] if v>=0 else "#E74C3C" for i,v in enumerate(s["net"])]
    fig2 = go.Figure(go.Bar(x=haneler,y=s["net"],marker_color=net_renk,text=[f"{v:+.2f} kW" for v in s["net"]],textposition="outside",textfont_color="#E6EDF3"))
    fig2.add_hline(y=0,line_color="#F5A623",line_dash="dot",line_width=1.5)
    fig2.update_layout(height=270,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#E6EDF3",margin=dict(l=0,r=0,t=6,b=0),yaxis=dict(gridcolor="#30363D",title="kW"),xaxis=dict(gridcolor="#30363D"))
    st.plotly_chart(fig2, use_container_width=True)

with g4:
    st.markdown('<p class="sec">🎮 Shapley Değerleri</p>', unsafe_allow_html=True)
    st.markdown('<div class="ibox">Her hanenin sisteme <strong>marjinal katkısı</strong> Shapley Değeri ile hesaplanır. Daha fazla üreten hane daha adil pay alır.</div>', unsafe_allow_html=True)
    max_sh = max(abs(v) for v in s["shapley"]) or 1
    for i in range(n):
        sh  = s["shapley"][i]
        pct = int(abs(sh)/max_sh*100)
        st.markdown(f'<div class="sh-row"><span style="font-size:.85rem;min-width:60px;"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{RENKLER[i]};margin-right:6px;"></span>Hane {i+1}</span><div class="sh-bar-bg"><div style="width:{pct}%;height:100%;background:{RENKLER[i]};border-radius:4px;"></div></div><span class="sh-val" style="color:{RENKLER[i]}">{sh:.3f}</span></div>', unsafe_allow_html=True)

st.markdown('<p class="sec">🕸️ Mikrogrid Enerji Ağı</p>', unsafe_allow_html=True)
angles = np.linspace(0, 2*np.pi, n, endpoint=False)
cx, cy = np.cos(angles)*1.3, np.sin(angles)*1.3
ex, ey = [], []
for i in range(n):
    for j in range(i+1, n):
        ex += [cx[i], cx[j], None]
        ey += [cy[i], cy[j], None]

fig_net = go.Figure()
fig_net.add_scatter(x=ex,y=ey,mode="lines",line=dict(color="rgba(245,166,35,.18)",width=1.8),hoverinfo="none",showlegend=False)
fig_net.add_scatter(x=cx,y=cy,mode="markers+text",marker=dict(size=[max(24,s["uretim"][i]*6) for i in range(n)],color=RENKLER[:n],line=dict(color="white",width=2)),text=[f"<b>H{i+1}</b><br>{s['uretim'][i]} kW" for i in range(n)],textposition="top center",textfont=dict(color="white",size=11),showlegend=False)
fig_net.add_scatter(x=[0],y=[0],mode="markers+text",marker=dict(size=52,color="#F5A623",symbol="star",line=dict(color="white",width=2)),text=["<b>Mikrogrid</b>"],textposition="bottom center",textfont=dict(color="#F5A623",size=12),hoverinfo="none",showlegend=False)
for i in range(n):
    fig_net.add_scatter(x=[0,cx[i]],y=[0,cy[i]],mode="lines",line=dict(color=RENKLER[i],width=2,dash="dot"),hoverinfo="none",showlegend=False)
fig_net.update_layout(height=420,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",showlegend=False,margin=dict(l=0,r=0,t=10,b=0),xaxis=dict(visible=False,range=[-2.0,2.0]),yaxis=dict(visible=False,range=[-2.0,2.0]))
st.plotly_chart(fig_net, use_container_width=True)

st.divider()
fa,fb,fc = st.columns(3)
with fa: st.caption("📌 **Proje:** MathErgy 212510\n\nTÜBİTAK 4006 · 2026 · Tasarım Araştırma")
with fb: st.caption("🔬 **Yöntemler**\n\nShapley Değeri · Nash Dengesi\nMini Mikrogrid Prototipi")
with fc: st.caption("🏫 **Okul**\n\nSıdıka Rodop Anadolu Lisesi\nMatematik · Enerji · Sürdürülebilirlik")
st.markdown("<p style='text-align:center;color:#30363D;font-size:.75rem;margin-top:12px;'>MathErgy © 2026 · TÜBİTAK 4006</p>", unsafe_allow_html=True)
