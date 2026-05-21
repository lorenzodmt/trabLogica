import streamlit as st
import pandas as pd

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="DataRecruit AI", page_icon="◈", layout="wide")

# ── Minimal CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0e0e0e;
    color: #e8e8e8;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem; max-width: 1100px; }

h1 { font-family: 'IBM Plex Mono', monospace; font-size: 1.1rem; font-weight: 600;
     letter-spacing: 0.15em; color: #c8f055; margin-bottom: 0; }

.subtitle { font-size: 0.78rem; color: #555; letter-spacing: 0.08em;
            font-family: 'IBM Plex Mono', monospace; margin-bottom: 2.5rem; }

.divider { border: none; border-top: 1px solid #1e1e1e; margin: 2rem 0; }

/* Desafio cards */
.challenge-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    color: #c8f055;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}
.challenge-title {
    font-size: 0.95rem;
    font-weight: 500;
    color: #e8e8e8;
    margin-bottom: 0.2rem;
}
.challenge-desc {
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 1rem;
}

/* Result badge */
.badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    background: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 3px;
    padding: 0.18rem 0.55rem;
    margin: 0.18rem 0.18rem 0.18rem 0;
    color: #b0b0b0;
}
.badge-senior {
    border-color: #c8f055;
    color: #c8f055;
}
.badge-junior {
    border-color: #3a3a3a;
    color: #777;
}

/* Dataframe override */
.stDataFrame { border: 1px solid #1e1e1e; border-radius: 4px; }

/* Expander */
.st-expander { border: 1px solid #1e1e1e !important; border-radius: 4px !important;
               background: #0e0e0e !important; }

/* Metrics */
.metric-box { background: #111; border: 1px solid #1e1e1e; border-radius: 4px;
              padding: 1rem 1.2rem; }
.metric-num { font-family: 'IBM Plex Mono', monospace; font-size: 1.6rem;
              color: #c8f055; font-weight: 600; }
.metric-lbl { font-size: 0.72rem; color: #555; letter-spacing: 0.06em; margin-top: 0.1rem; }

/* Tabs */
button[data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    color: #555 !important;
}
button[data-baseweb="tab"][aria-selected="true"] { color: #c8f055 !important; }
[data-baseweb="tab-highlight"] { background-color: #c8f055 !important; }
[data-baseweb="tab-border"] { background-color: #1e1e1e !important; }
</style>
""", unsafe_allow_html=True)

# ── Dataset ────────────────────────────────────────────────────────────────────
data = [
    (1,"Alice Santos",19,1,True,False),(2,"Bruno Alves",25,4,False,True),
    (3,"Carla Souza",17,0,True,False),(4,"Daniel Lima",30,7,True,True),
    (5,"Elena Silva",21,2,False,False),(6,"Fabio Rocha",40,15,True,False),
    (7,"Gisele Melo",23,3,True,True),(8,"Hugo Peron",18,0,False,False),
    (9,"Igor Gomes",28,5,False,True),(10,"Julia Costa",22,2,True,False),
    (11,"Kauê Ramos",20,1,False,False),(12,"Liz Duarte",35,10,True,True),
    (13,"Marcos Vaz",19,2,True,False),(14,"Nina Sales",24,4,False,True),
    (15,"Otto Cruz",29,6,True,False),(16,"Paula Dias",17,1,True,False),
    (17,"Quico Neto",21,0,False,False),(18,"Rosa Lima",45,20,False,True),
    (19,"Saul Reis",26,5,True,False),(20,"Tati Belo",22,3,False,True),
    (21,"Uriel Luz",18,0,True,False),(22,"Vitor Paz",31,8,False,True),
    (23,"Wendy Sol",20,1,True,False),(24,"Xandy Farias",27,4,False,False),
    (25,"Yuri Zago",23,2,True,True),(26,"Zeca Silva",19,1,False,False),
    (27,"Alan Terra",33,9,True,True),(28,"Bia Nunes",20,2,False,False),
    (29,"Caio Mello",17,0,False,False),(30,"Dora Lins",25,3,True,True),
    (31,"Enzo Ferraz",18,1,False,False),(32,"Fred Góes",42,18,True,False),
    (33,"Giba Orta",22,2,False,True),(34,"Helô Maia",21,1,True,False),
    (35,"Isis Vale",24,4,False,False),(36,"Juca Terto",30,6,True,True),
    (37,"Kelly Pires",19,0,False,False),(38,"Léo Fontes",28,5,True,False),
    (39,"Mara Jobim",20,2,False,True),(40,"Noel Rosa",50,25,False,False),
    (41,"Olga Telles",22,3,True,False),(42,"Pepe Lopez",18,1,False,False),
    (43,"Ruth Lemos",26,4,True,True),(44,"Sara Otoni",23,2,False,False),
    (45,"Tomé Silva",31,8,True,False),(46,"Una Costa",19,0,False,True),
    (47,"Valter Zen",28,5,True,True),(48,"Will Smith",24,3,False,False),
    (49,"Zara Lima",21,1,True,False),(50,"Ari Pires",18,0,False,False),
]

cols = ["ID", "Nome", "Idade", "Exp", "Técnico", "Inglês"]
df = pd.DataFrame(data, columns=cols)

# ── Lógica dos desafios ────────────────────────────────────────────────────────
d1 = df[(df["Idade"] >= 18) & (df["Técnico"] == True)]
d2 = df[(df["Exp"] >= 3) | (df["Inglês"] == True)]
d3 = df[(df["Idade"] < 25) & ((df["Técnico"] == True) | (df["Exp"] >= 1))]
df["Categoria"] = df["Exp"].apply(lambda x: "SÊNIOR" if x > 5 else "JÚNIOR")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<h1>◈ DATARECRUIT AI</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">ALGORITMO DE SELEÇÃO INTELIGENTE — LÓGICA PARA COMPUTAÇÃO</div>', unsafe_allow_html=True)

# ── Métricas ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    (len(df), "candidatos totais"),
    (len(d1), "desafio 1"),
    (len(d2), "desafio 2"),
    (len(d3), "desafio 3"),
    (len(df[df["Categoria"] == "SÊNIOR"]), "sênior"),
]
for col, (num, lbl) in zip([c1, c2, c3, c4, c5], metrics):
    with col:
        st.markdown(f'<div class="metric-box"><div class="metric-num">{num}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_dataset, tab1, tab2, tab3, tab4 = st.tabs([
    "DATASET", "DESAFIO 1", "DESAFIO 2", "DESAFIO 3", "DESAFIO 4"
])

# helper para exibir tabela limpa
def show_table(frame, extra_cols=None):
    display_cols = ["ID", "Nome", "Idade", "Exp", "Técnico", "Inglês"]
    if extra_cols:
        display_cols += extra_cols
    show = frame[display_cols].copy()
    show["Técnico"] = show["Técnico"].map({True: "✓", False: "—"})
    show["Inglês"]  = show["Inglês"].map({True: "✓", False: "—"})
    st.dataframe(show.reset_index(drop=True), use_container_width=True, hide_index=True)

# ── Dataset ────────────────────────────────────────────────────────────────────
with tab_dataset:
    st.markdown('<div class="challenge-label">base de dados</div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-title">50 Candidatos</div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-desc">Dados brutos utilizados em todos os desafios.</div>', unsafe_allow_html=True)
    show_table(df)

# ── Desafio 1 ──────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="challenge-label">desafio 1 — operador E (and)</div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-title">Triagem de Qualificação Técnica</div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-desc">Maioridade legal (idade ≥ 18) <b>E</b> curso técnico completo.</div>', unsafe_allow_html=True)

    with st.expander("ver código"):
        st.code(
            "aprovados_d1 = [\n"
            "    c for c in candidatos\n"
            "    if c['idade'] >= 18 and c['tecnico'] == True\n"
            "]", language="python"
        )

    st.markdown(f"**{len(d1)} aprovados**")
    show_table(d1)

# ── Desafio 2 ──────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="challenge-label">desafio 2 — operador OU (or)</div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-title">Expansão de Talentos Internacionais</div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-desc">Experiência ≥ 3 anos <b>OU</b> domínio da língua inglesa.</div>', unsafe_allow_html=True)

    with st.expander("ver código"):
        st.code(
            "aprovados_d2 = [\n"
            "    c for c in candidatos\n"
            "    if c['exp'] >= 3 or c['ingles'] == True\n"
            "]", language="python"
        )

    st.markdown(f"**{len(d2)} aprovados**")
    show_table(d2)

# ── Desafio 3 ──────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="challenge-label">desafio 3 — lógica combinada</div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-title">Filtro de Potencial Jovem</div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-desc">Idade &lt; 25 <b>E</b> (técnico completo <b>OU</b> experiência ≥ 1 ano).</div>', unsafe_allow_html=True)

    with st.expander("ver código"):
        st.code(
            "aprovados_d3 = [\n"
            "    c for c in candidatos\n"
            "    if c['idade'] < 25\n"
            "    and (c['tecnico'] == True or c['exp'] >= 1)\n"
            "]", language="python"
        )

    st.markdown(f"**{len(d3)} aprovados**")
    show_table(d3)

# ── Desafio 4 ──────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="challenge-label">desafio 4 — operação condicional</div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-title">Classificação Salarial</div>', unsafe_allow_html=True)
    st.markdown('<div class="challenge-desc">Experiência &gt; 5 anos → <b>SÊNIOR</b>, caso contrário → <b>JÚNIOR</b>.</div>', unsafe_allow_html=True)

    with st.expander("ver código"):
        st.code(
            'for c in candidatos:\n'
            '    categoria = "SÊNIOR" if c["exp"] > 5 else "JÚNIOR"\n'
            '    print(f"Nome: {c[\'nome\']} | Categoria: {categoria}")',
            language="python"
        )

    col_s, col_j = st.columns(2)

    senior = df[df["Categoria"] == "SÊNIOR"]
    junior = df[df["Categoria"] == "JÚNIOR"]

    with col_s:
        st.markdown(f'<div class="challenge-label">sênior — {len(senior)} candidatos</div>', unsafe_allow_html=True)
        for _, row in senior.iterrows():
            st.markdown(f'<span class="badge badge-senior">#{row["ID"]:02d} {row["Nome"]} · {row["Exp"]}a</span>', unsafe_allow_html=True)

    with col_j:
        st.markdown(f'<div class="challenge-label">júnior — {len(junior)} candidatos</div>', unsafe_allow_html=True)
        for _, row in junior.iterrows():
            st.markdown(f'<span class="badge badge-junior">#{row["ID"]:02d} {row["Nome"]} · {row["Exp"]}a</span>', unsafe_allow_html=True)
