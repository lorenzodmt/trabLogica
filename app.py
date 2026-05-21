import streamlit as st
import pandas as pd

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="DataRecruit AI", page_icon="◈", layout="wide")

# ── Minimal CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem; max-width: 1100px; }
.divider { border: none; border-top: 1px solid #e0e0e0; margin: 1.5rem 0; }

.metric-box { background: linear-gradient(135deg, #e8f0fe 0%, #ede7f6 100%); border: 1px solid #d0d8f0; border-radius: 6px;
              padding: 1rem 1.2rem; }
.metric-num { font-size: 1.6rem; font-weight: 600; margin-bottom: 0.1rem; color: #111; }
.metric-lbl { font-size: 0.75rem; color: #888; margin-top: 0.1rem; }

.badge {
    display: inline-block;
    font-size: 0.78rem;
    background: #f4f4f4;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 0.2rem 0.6rem;
    margin: 0.2rem 0.2rem 0.2rem 0;
    color: #444;
}
.badge-senior { border-color: #1a7f4b; color: #1a7f4b; background: #f0faf4; }
.badge-junior { border-color: #ccc; color: #666; }
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
st.title("DataRecruit AI")
st.caption("Algoritmo de Seleção Inteligente — Lógica para Computação")

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
        st.markdown(
            f'<div class="metric-box">'
            f'<div class="metric-num">{num}</div>'
            f'<div class="metric-lbl">{lbl}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_dataset, tab1, tab2, tab3, tab4 = st.tabs([
    "Dataset", "Desafio 1", "Desafio 2", "Desafio 3", "Desafio 4"
])

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
    st.subheader("50 Candidatos")
    st.caption("Dados brutos utilizados em todos os desafios.")
    show_table(df)

# ── Desafio 1 ──────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Triagem de Qualificação Técnica")
    st.caption("Operador **E** — Maioridade legal (idade ≥ 18) **e** curso técnico completo.")

    with st.expander("Ver código", expanded=True):
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
    st.subheader("Expansão de Talentos Internacionais")
    st.caption("Operador **OU** — Experiência ≥ 3 anos **ou** domínio da língua inglesa.")

    with st.expander("Ver código", expanded=True):
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
    st.subheader("Filtro de Potencial Jovem")
    st.caption("Lógica combinada — Idade < 25 **e** (técnico completo **ou** experiência ≥ 1 ano).")

    with st.expander("Ver código", expanded=True):
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
    st.subheader("Classificação Salarial")
    st.caption("Operação condicional — Experiência > 5 anos → **SÊNIOR**, caso contrário → **JÚNIOR**.")

    with st.expander("Ver código", expanded=True):
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
        st.markdown(f"**Sênior — {len(senior)} candidatos**")
        for _, row in senior.iterrows():
            st.markdown(
                f'<span class="badge badge-senior">#{row["ID"]:02d} {row["Nome"]} · {row["Exp"]}a</span>',
                unsafe_allow_html=True
            )

    with col_j:
        st.markdown(f"**Júnior — {len(junior)} candidatos**")
        for _, row in junior.iterrows():
            st.markdown(
                f'<span class="badge badge-junior">#{row["ID"]:02d} {row["Nome"]} · {row["Exp"]}a</span>',
                unsafe_allow_html=True
            )
