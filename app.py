import streamlit as st
import pandas as pd
import itertools
import re

class MotorLogico:
    def __init__(self):
        # Mapeamento de conectivos para operadores válidos do Python
        self.REPLACEMENTS = [
            ('<->', '=='),
            ('->', ' <= '),  # P -> Q é equivalente a P <= Q em lógica booleana no Python
            ('~', ' not '),
            ('&', ' and '),
            ('|', ' or '),
            ('+', ' or ')   
        ]

    def normalizar_expressao(self, expressao: str) -> str:
        """Converte todas as variáveis proposicionais para maiúsculas, padroniza o '+' para '|' e remove espaços."""
        expr = re.sub(r'\b[a-z]\b', lambda m: m.group(0).upper(), expressao)
        expr = expr.replace('+', '|')
        return "".join(expr.split())

    def extrair_variaveis(self, expressoes: list) -> list:
        """Extrai todas as variáveis proposicionais (letras isoladas, maiúsculas ou minúsculas)."""
        variaveis = set()
        for expr in expressoes:
            encontradas = re.findall(r'\b[a-zA-Z]\b', expr)
            variaveis.update([v.upper() for v in encontradas])
        return sorted(list(variaveis))

    def preparar_expressao(self, expressao: str) -> str:
        """Traduz a expressão normalizada para a sintaxe do Python."""
        expr_traduzida = self.normalizar_expressao(expressao)
        for logico, python in self.REPLACEMENTS:
            expr_traduzida = expr_traduzida.replace(logico, python)
        return expr_traduzida

    def avaliar_linha(self, expressao_preparada: str, contexto: dict) -> bool:
        """Avalia o valor-verdade de uma expressão usando o eval nativo."""
        try:
            return bool(eval(expressao_preparada, {}, contexto))
        except Exception as e:
            raise SyntaxError(f"Erro de sintaxe na expressão. Verifique os parênteses e conectivos.")

    def gerar_combinacoes(self, variaveis: list) -> list:
        """Gera a árvore de possibilidades binárias (True/False)."""
        return list(itertools.product([True, False], repeat=len(variaveis)))

    def formatar_booleano(self, valor: bool) -> str:
        """Mapeia True/False para V/F para exibição acadêmica."""
        return 'V' if valor else 'F'

    def processar_equivalencia(self, expr1: str, expr2: str):
        variaveis = self.extrair_variaveis([expr1, expr2])
        expr1_prep = self.preparar_expressao(expr1)
        expr2_prep = self.preparar_expressao(expr2)
        combinacoes = self.gerar_combinacoes(variaveis)

        linhas_tabela = []
        equivalentes = True

        for combo in combinacoes:
            contexto = dict(zip(variaveis, combo))
            res1 = self.avaliar_linha(expr1_prep, contexto)
            res2 = self.avaliar_linha(expr2_prep, contexto)

            if res1 != res2:
                equivalentes = False

            linha = {v: self.formatar_booleano(contexto[v]) for v in variaveis}
            linha[self.normalizar_expressao(expr1)] = self.formatar_booleano(res1)
            linha[self.normalizar_expressao(expr2)] = self.formatar_booleano(res2)
            linhas_tabela.append(linha)

        df = pd.DataFrame(linhas_tabela)
        return df, equivalentes

    # --- MAPEAMENTO DAS REGRAS SOLICITADAS ---
    def explicar_argumento(self, premissas: list, conclusao: str, eh_valido: bool) -> str:
        """Analisa a estrutura das premissas e conclusão para identificar e explicar a regra aplicada."""
        p_norm = [self.normalizar_expressao(p) for p in premissas]
        c_norm = self.normalizar_expressao(conclusao)
        p_set = set(p_norm)

        if eh_valido:
            # 1. MODUS PONENS (MP) -> A->B, A => B
            for p in p_norm:
                if "->" in p and "<->" not in p:
                    antecedente, consequente = p.split("->", 1)
                    if antecedente in p_set and c_norm == consequente:
                        return f"**Regra Identificada:** Modus Ponens (MP)\n\n" \
                               f"**Explicação:** A partir de uma condicional `{antecedente}->{consequente}` e da afirmação do seu antecedente `{antecedente}`, " \
                               f"infere-se legitimamente o consequente `{consequente}`."

            # 2. MODUS TOLLENS (MT) -> A->B, ~B => ~A
            for p in p_norm:
                if "->" in p and "<->" not in p:
                    antecedente, consequente = p.split("->", 1)
                    neg_consequente = f"~{consequente}" if not consequente.startswith("~") else consequente[1:]
                    neg_antecedente = f"~{antecedente}" if not antecedente.startswith("~") else antecedente[1:]
                    if neg_consequente in p_set and c_norm == neg_antecedente:
                        return f"**Regra Identificada:** Modus Tollens (MT)\n\n" \
                               f"**Explicação:** A partir de uma condicional `{antecedente}->{consequente}` e da negação do seu consequente `{neg_consequente}`, " \
                               f"infere-se a negação do seu antecedente `{neg_antecedente}`."

            # 3. SILOGISMO HIPOTÉTICO (SH) -> A->B, B->C => A->C
            for p1 in p_norm:
                if "->" in p1 and "<->" not in p1:
                    a, b = p1.split("->", 1)
                    for p2 in p_norm:
                        if "->" in p2 and "<->" not in p2 and p1 != p2:
                            b2, c = p2.split("->", 1)
                            if b == b2 and c_norm == f"{a}->{c}":
                                return f"**Regra Identificada:** Silogismo Hipotético (SH)\n\n" \
                                       f"**Explicação:** Se uma proposição `{a}` implica em `{b}`, e `{b}` implica em `{c}`, " \
                                       f"estabelece-se uma relação transitiva direta onde `{a}` implica em `{c}`."

            # 4. SILOGISMO DISJUNTIVO (SD) -> A|B, ~A => B
            for p in p_norm:
                if "|" in p:
                    partes = p.split("|")
                    if len(partes) == 2:
                        a, b = partes[0], partes[1]
                        neg_a = f"~{a}" if not a.startswith("~") else a[1:]
                        neg_b = f"~{b}" if not b.startswith("~") else b[1:]
                        if (neg_a in p_set and c_norm == b) or (neg_b in p_set and c_norm == a):
                            return f"**Regra Identificada:** Silogismo Disjuntivo (SD)\n\n" \
                                   f"**Explicação:** Havendo uma disjunção `{a}|{b}` (onde pelo menos uma alternativa é verdadeira) e sabendo " \
                                   f"que uma delas foi negada, conclui-se necessariamente a outra."

            # 5. ADIÇÃO (A) -> A => A|B
            if "|" in c_norm:
                partes_c = c_norm.split("|")
                if any(p in partes_c for p in p_norm):
                    return f"**Regra Identificada:** Adição (A)\n\n" \
                           f"**Explicação:** Como uma das proposições já é verdadeira pelas premissas, a introdução de uma disjunção " \
                           f"('OU') com qualquer outra variável mantém o argumento inteiramente válido."

            # 6. REGRAS DO BICONDICIONAL (BIC) -> A<->B => A->B (ou vice-versa)
            for p in p_norm:
                if "<->" in p:
                    a, b = p.split("<->", 1)
                    if c_norm in (f"{a}->{b}", f"{b}->{a}"):
                        return f"**Regra Identificada:** Regras do Bicondicional (BIC)\n\n" \
                               f"**Explicação:** A dupla implicação `{a}<->{b}` significa que tanto `{a}->{b}` quanto `{b}->{a}` são simultaneamente verdadeiros, " \
                               f"permitindo extrair qualquer uma das condicionais de forma isolada."
            if "->" in c_norm and len(p_norm) >= 2:
                # Caso inverso: p->q e q->p gerando p<->q
                for p1 in p_norm:
                    if "->" in p1 and "<->" not in p1:
                        a, b = p1.split("->", 1)
                        if f"{b}->{a}" in p_set and c_norm == f"{a}<->{b}":
                            return f"**Regra Identificada:** Regras do Bicondicional (BIC)\n\n" \
                                   f"**Explicação:** Havendo a implicação mútua nas premissas (se `{a}` então `{b}`, e se `{b}` então `{a}`), " \
                                   f"conclui-se a equivalência lógica exata `{a}<->{b}`."

            # 7. SIMPLIFICAÇÃO (S) -> A&B => A
            for p in p_norm:
                if "&" in p:
                    partes_p = p.split("&")
                    if c_norm in partes_p:
                        return f"**Regra Identificada:** Simplificação (S)\n\n" \
                               f"**Explicação:** Uma conjunção (`{p}`) exige que ambas as partes sejam simultaneamente verdadeiras, " \
                               f"sendo legítimo extrair qualquer uma das componentes separadamente."

            # 8. SIMPLIFICAÇÃO DISJUNTIVA (S+) -> A|A => A ou (A->B)&(C->B), A|C => B
            for p in p_norm:
                if "|" in p and p.split("|")[0] == p.split("|")[1] and c_norm == p.split("|")[0]:
                    return f"**Regra Identificada:** Simplificação Disjuntiva (S+) [Idempotência]\n\n" \
                           f"**Explicação:** A disjunção de uma proposição com ela mesma `{p}` reduz-se logicamente à própria proposição única."
            # Caso clássico de eliminação por casos (Dilema Construtivo Especializado)
            if len(p_norm) >= 2:
                for p1 in p_norm:
                    if "&" in p1:  # Estrutura (A->B)&(C->B)
                        partes = p1.split("&")
                        if "->" in partes[0] and "->" in partes[1]:
                            a, b1 = partes[0].split("->", 1)
                            c, b2 = partes[1].split("->", 1)
                            if b1 == b2 and b1 == c_norm and (f"{a}|{c}" in p_set or f"{c}|{a}" in p_set):
                                return f"**Regra Identificada:** Simplificação Disjuntiva (S+) [Eliminação por Casos]\n\n" \
                                       f"**Explicação:** Se ambos os caminhos alternativos (`{a}` ou `{c}`) levam inevitavelmente ao mesmo resultado `{c_norm}`, " \
                                       f"então o resultado ocorrerá de qualquer forma."

            # 9. CONJUNÇÃO (C) -> A, B => A&B
            if "&" in c_norm:
                partes_c = c_norm.split("&")
                if len(partes_c) == 2:
                    c1, c2 = partes_c[0], partes_c[1]
                    if (c1 in p_set or any(c1 in p and "&" in p for p in p_norm)) and \
                       (c2 in p_set or any(c2 in p and "&" in p for p in p_norm)):
                        return f"**Regra Identificada:** Conjunção (C)\n\n" \
                               f"**Explicação:** Se duas premissas são verdadeiras isoladamente no sistema, elas podem ser unidas através do conectivo 'E' (`&`)."

            return "**Regra Identificada:** Dedução Válida Geral.\n\n" \
                   "**Explicação:** O argumento foi validado com sucesso através da matriz da tabela-verdade, embora represente uma composição complexa de passos dedutivos."
        else:
            # Tratamento para Falácias
            for p in p_norm:
                if "->" in p and "<->" not in p:
                    antecedente, consequente = p.split("->", 1)
                    if consequente in p_set and c_norm == antecedente:
                        return f"**Falácia Identificada:** Afirmação do Consequente.\n\n" \
                               f"**Por que é inválido?** Mesmo que `{antecedente} -> {consequente}` seja verdade, saber que o efeito `{consequente}` ocorreu não garante que ele foi desencadeado especificamente por `{antecedente}`."
                    neg_antecedente = f"~{antecedente}" if not antecedente.startswith("~") else antecedente[1:]
                    neg_consequente = f"~{consequente}" if not consequente.startswith("~") else consequente[1:]
                    if neg_antecedente in p_set and c_norm == neg_consequente:
                        return f"**Falácia Identificada:** Negação do Antecedente.\n\n" \
                               f"**Por que é inválido?** A ausência da causa primitiva `{neg_antecedente}` não impede que o efeito ocorra por outras vias não mapeadas."

            return "**Falácia Identificada:** Falácia Lógica Geral.\n\n" \
                   "**Por que é inválido?** A tabela-verdade provou computacionalmente a existência de linhas inconsistentes onde as premissas são Verdadeiras e a conclusão é Falsa."

    def processar_argumento(self, premissas: list, conclusao: str):
        todas_expressoes = premissas + [conclusao]
        variaveis = self.extrair_variaveis(todas_expressoes)
        premissas_prep = [self.preparar_expressao(p) for p in premissas]
        conclusao_prep = self.preparar_expressao(conclusao)
        combinacoes = self.gerar_combinacoes(variaveis)

        linhas_tabela = []
        argumento_valido = True

        for combo in combinacoes:
            contexto = dict(zip(variaveis, combo))
            valores_premissas = [self.avaliar_linha(p, contexto) for p in premissas_prep]
            valor_conclusao = self.avaliar_linha(conclusao_prep, contexto)

            eh_falacia_na_linha = all(valores_premissas) and not valor_conclusao
            if eh_falacia_na_linha:
                argumento_valido = False

            linha = {v: self.formatar_booleano(contexto[v]) for v in variaveis}
            for i, p_val in enumerate(valores_premissas):
                p_nome_norm = self.normalizar_expressao(premissas[i])
                linha[f"Premissa {i+1} ({p_nome_norm})"] = self.formatar_booleano(p_val)
            
            c_nome_norm = self.normalizar_expressao(conclusao)
            linha[f"Conclusão ({c_nome_norm})"] = self.formatar_booleano(valor_conclusao)
            linha["Validação"] = "❌ FALÁCIA" if eh_falacia_na_linha else "✅ OK"
            linhas_tabela.append(linha)

        df = pd.DataFrame(linhas_tabela)
        explicao_didatica = self.explicar_argumento(premissas, conclusao, argumento_valido)
        
        return df, argumento_valido, explicao_didatica


# =====================================================================
#                         INTERFACE STREAMLIT
# =====================================================================

st.set_page_config(page_title="Motor Lógico - UFN", page_icon="🧠", layout="wide")

st.title("🧠 Protótipo de Motor Lógico em Python")
st.markdown("""
Mapeamento de Tabelas-Verdade, Equivalências e Motores de Inferência Aplicados à IA.  
*Desenvolvido para a disciplina de Lógica para Computação (Prof. Leandro Ribeiro Fontoura).*
""")

st.sidebar.header("Guia de Conectivos")
st.sidebar.markdown("""
Use a seguinte sintaxe para as expressões:
* **Negação:** `~p`
* **Conjunção (E):** `p & q`
* **Disjunção (OU):** `p | q` ou `p + q`
* **Condicional:** `p -> q`
* **Bicondicional:** `p <-> q`
* *Você pode separar premissas por **vírgulas** em um mesmo campo (ex: `p + q, ~p`).*
""")

motor = MotorLogico()

tab_equiv, tab_inferencia = st.tabs([
    "Módulo B: Provador de Equivalência",
    "Módulo C: Motor de Inferência (Validador)"
])

# --- MÓDULO B ---
with tab_equiv:
    st.header("Verificador de Equivalência Lógica")
    st.write("Insira duas expressões para verificar se elas possuem tabelas-verdade idênticas (Ex: Leis de De Morgan).")
    
    col1, col2 = st.columns(2)
    with col1:
        e1 = st.text_input("Primeira Expressão (Entrada 1):", value="~(p & q)")
    with col2:
        e2 = st.text_input("Segunda Expressão (Entrada 2):", value="~p | ~q")

    if st.button("Calcular Equivalência", key="btn_equiv"):
        if e1 and e2:
            try:
                df_resultado, sao_equivalentes = motor.processar_equivalencia(e1, e2)
                if sao_equivalentes:
                    st.success("### 🟩 Resposta: Expressões LOGICAMENTE EQUIVALENTES")
                else:
                    st.error("### 🟥 Resposta: Expressões NÃO SÃO EQUIVALENTES")
                st.write("#### Tabela-Verdade Gerada:")
                st.dataframe(df_resultado, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
        else:
            st.warning("Por favor, preencha ambas as expressões.")

# --- MÓDULO C ---
with tab_inferencia:
    st.header("Validador de Argumentos Lógicos com Explicação Didática")
    st.write("Defina um conjunto de premissas e veja se a conclusão decorre logicamente delas, acompanhado do diagnóstico conceitual com siglas acadêmicas.")
    st.caption("💡 **Exemplo de uso:** Você pode digitar `p + q, ~p` diretamente na caixa abaixo.")

    if 'num_premissas' not in st.session_state:
        st.session_state.num_premissas = 1

    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
    with col_btn1:
        if st.button("➕ Adicionar Linha de Entrada"):
            st.session_state.num_premissas += 1
    with col_btn2:
        if st.button("➖ Remover Linha de Entrada") and st.session_state.num_premissas > 1:
            st.session_state.num_premissas -= 1

    premissas_brutas = []
    st.write("#### Premissas:")
    
    defaults_premissas = ["p + q, ~p"]
    
    for i in range(st.session_state.num_premissas):
        val_default = defaults_premissas[i] if i < len(defaults_premissas) else ""
        p_in = st.text_input(f"Entrada {i+1}:", value=val_default, key=f"premissa_{i}")
        if p_in.strip():
            premissas_brutas.append(p_in)

    st.write("#### Conclusão:")
    conclusao_input = st.text_input("Conclusão do Argumento:", value="q", key="conclusao")

    if st.button("Avaliar Validade do Argumento", key="btn_infer"):
        if premissas_brutas and conclusao_input:
            try:
                premissas_finais = []
                for item in premissas_brutas:
                    if "," in item:
                        sub_premissas = [sub.strip() for sub in item.split(",") if sub.strip()]
                        premissas_finais.extend(sub_premissas)
                    else:
                        premissas_finais.append(item.strip())

                df_argumento, eh_valido, explicacao = motor.processar_argumento(premissas_finais, conclusao_input)
                
                if eh_valido:
                    st.success("### 🟩 Veredito: O argumento é VÁLIDO (Dedução Legítima)")
                else:
                    st.error("### 🟥 Veredito: O argumento é INVÁLIDO (Falácia Lógica)")
                
                st.info(explicacao)

                st.write("#### Análise da Tabela-Verdade do Argumento:")
                st.dataframe(df_argumento, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao processar o argumento: {e}")
        else:
            st.warning("Certifique-se de preencher as premissas e a conclusão.")
