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
            ('|', ' or ')
        ]

    def normalizar_expressao(self, expressao: str) -> str:
        """Converte todas as variáveis proposicionais para maiúsculas e remove espaços extras."""
        # Encontra letras isoladas e as transforma em maiúsculas
        expr = re.sub(r'\b[a-z]\b', lambda m: m.group(0).upper(), expressao)
        # Remove espaços desnecessários para facilitar o casamento de padrões
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

    # --- PROCESSAMENTO PARA O MÓDULO B ---
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

    # --- MOTOR DE RECONHECIMENTO DE PADRÕES (EXPLICAÇÃO) ---
    def explicar_argumento(self, premissas: list, conclusao: str, eh_valido: bool) -> str:
        """Analisa a estrutura das premissas e conclusão para identificar e explicar a regra aplicada."""
        p_norm = [self.normalizar_expressao(p) for p in premissas]
        c_norm = self.normalizar_expressao(conclusao)
        
        # Cria um conjunto das premissas para facilitar buscas de ordem independente
        p_set = set(p_norm)

        if eh_valido:
            # 1. Tenta identificar MODUS PONENS
            # Padrão: Se tivermos uma condicional (A->B) e a afirmação do antecedente (A), a conclusão deve ser B.
            for p in p_norm:
                if "->" in p and "<->" not in p:
                    antecedente, consequente = p.split("->", 1)
                    if antecedente in p_set and c_norm == consequente:
                        return f"**Regra identificada:** Modus Ponens (Afirmação do Antecedente).\n\n" \
                               f"**Por que é válido?** A estrutura lógica diz que sempre que a regra `{antecedente} -> {consequente}` for verdadeira, " \
                               f"e o fato `{antecedente}` ocorrer isoladamente, o resultado `{consequente}` obrigatoriamente acontecerá."

            # 2. Tenta identificar MODUS TOLLENS
            # Padrão: Se tivermos uma condicional (A->B) e a negação do consequente (~B), a conclusão deve ser ~A.
            for p in p_norm:
                if "->" in p and "<->" not in p:
                    antecedente, consequente = p.split("->", 1)
                    neg_consequente = f"~{consequente}" if not consequente.startswith("~") else consequente[1:]
                    neg_antecedente = f"~{antecedente}" if not antecedente.startswith("~") else antecedente[1:]
                    
                    if neg_consequente in p_set and c_norm == neg_antecedente:
                        return f"**Regra identificada:** Modus Tollens (Negação do Consequente).\n\n" \
                               f"**Por que é válido?** A regra diz que `{antecedente}` implica em `{consequente}`. Como a premissa informa " \
                               f"que `{consequente}` não aconteceu (`{neg_consequente}`), conclui-se de forma legítima que o seu causador também não ocorreu (`{neg_antecedente}`)."

            # 3. Tenta identificar SILOGISMO HIPOTÉTICO
            # Padrão: Se A->B e B->C, então A->C.
            for p1 in p_norm:
                if "->" in p1 and "<->" not in p1:
                    a, b = p1.split("->", 1)
                    for p2 in p_norm:
                        if "->" in p2 and "<->" not in p2 and p1 != p2:
                            b2, c = p2.split("->", 1)
                            if b == b2 and c_norm == f"{a}->{c}":
                                return f"**Regra identificada:** Silogismo Hipotético (Regra da Cadeia).\n\n" \
                                       f"**Por que é válido?** Há um encadeamento lógico de causa e efeito. Se `{a}` leva a `{b}` e `{b}` leva a `{c}`, " \
                                       f"estabelece-se uma relação direta de que `{a}` causará `{c}`."

            # 4. Tenta identificar SILOGISMO DISJUNTIVO
            # Padrão: Se A|B e tivermos ~A, a conclusão é B (ou vice-versa).
            for p in p_norm:
                if "|" in p:
                    partes = p.split("|")
                    if len(partes) == 2:
                        a, b = partes[0], partes[1]
                        neg_a = f"~{a}" if not a.startswith("~") else a[1:]
                        neg_b = f"~{b}" if not b.startswith("~") else b[1:]
                        
                        if (neg_a in p_set and c_norm == b) or (neg_b in p_set and c_norm == a):
                            return f"**Regra identificada:** Silogismo Disjuntivo (Eliminação por Alternativa).\n\n" \
                                   f"**Por que é válido?** A premissa inicial garante que pelo menos uma das opções é verdadeira (`{a}` ou `{b}`). " \
                                   f"Ao eliminar uma das alternativas através da outra premissa, resta obrigatoriamente aceitar a outra como verdade."

            return "**Regra identificada:** Dedução Válida Geral.\n\n" \
                   "**Por que é válido?** Embora este argumento não se encaixe perfeitamente em um único nome de silogismo simples clássico, " \
                   "a análise matemática da tabela-verdade provou que em todas as situações onde todas as suas premissas são Verdadeiras, " \
                   "a sua conclusão também se manteve Verdadeira."
        else:
            # Tratamento didático para Falácias (Argumentos Inválidos)
            for p in p_norm:
                if "->" in p and "<->" not in p:
                    antecedente, consequente = p.split("->", 1)
                    
                    # Falácia da Afirmação do Consequente (Ex: P->Q, Q. Conclusão: P)
                    if consequente in p_set and c_norm == antecedente:
                        return f"**Falácia Identificada:** Afirmação do Consequente.\n\n" \
                               f"**Por que é inválido?** É um erro comum deduzir que o efeito só possui uma causa única. Mesmo que `{antecedente} -> {consequente}` seja verdade, " \
                               f"saber que `{consequente}` aconteceu não prova que ele foi causado especificamente por `{antecedente}` (outros fatores não mapeados poderiam gerar `{consequente}`)."
                    
                    # Falácia da Negação do Antecedente (Ex: P->Q, ~P. Conclusão: ~Q)
                    neg_antecedente = f"~{antecedente}" if not antecedente.startswith("~") else antecedente[1:]
                    neg_consequente = f"~{consequente}" if not consequente.startswith("~") else consequente[1:]
                    if neg_antecedente in p_set and c_norm == neg_consequente:
                        return f"**Falácia Identificada:** Negação do Antecedente.\n\n" \
                               f"**Por que é inválido?** Dizer que `{antecedente}` causa `{consequente}` não significa que `{antecedente}` seja a *única* forma de gerar `{consequente}`. " \
                               f"Portanto, o fato de `{antecedente}` não ter acontecido (`{neg_antecedente}`) não impede que `{consequente}` aconteça por outros caminhos."

            return "**Falácia Identificada:** Falácia Lógica Geral.\n\n" \
                   "**Por que é inválido?** A análise computacional detectou linhas críticas (sinalizadas abaixo) onde todas as premissas " \
                   "inseridas conseguem ser Verdadeiras (V) ao mesmo tempo em que a sua conclusão resulta em Falsa (F). Isso quebra a consistência do argumento."

    # --- PROCESSAMENTO PARA O MÓDULO C ---
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

            # Um argumento é inválido se as premissas forem V e a conclusão for F
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
* **Disjunção (OU):** `p | q`
* **Condicional:** `p -> q`
* **Bicondicional:** `p <-> q`
* *Você pode utilizar tanto letras **minúsculas** quanto **maiúsculas** para as variáveis!*
""")

motor = MotorLogico()

# Criação das abas para organização do Trabalho Prático
tab_equiv, tab_inferencia = st.tabs([
    "Módulo B: Provador de Equivalência",
    "Módulo C: Motor de Inferência (Validador)"
])

# --- ABA: PROVADOR DE EQUIVALÊNCIA ---
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

# --- ABA: MOTOR DE INFERÊNCIA ---
with tab_inferencia:
    st.header("Validador de Argumentos Lógicos com Explicação Didática")
    st.write("Defina um conjunto de premissas e veja se a conclusão decorre logicamente delas, acompanhado do diagnóstico conceitual.")

    # Controle dinâmico do número de premissas usando a sessão do Streamlit
    if 'num_premissas' not in st.session_state:
        st.session_state.num_premissas = 2

    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
    with col_btn1:
        if st.button("➕ Adicionar Premissa"):
            st.session_state.num_premissas += 1
    with col_btn2:
        if st.button("➖ Remover Premissa") and st.session_state.num_premissas > 1:
            st.session_state.num_premissas -= 1

    # Inputs das premissas dinâmicas
    premissas_inputs = []
    st.write("#### Premissas:")
    
    defaults_premissas = ["p -> q", "p"]
    
    for i in range(st.session_state.num_premissas):
        val_default = defaults_premissas[i] if i < len(defaults_premissas) else ""
        p_in = st.text_input(f"Premissa {i+1}:", value=val_default, key=f"premissa_{i}")
        if p_in:
            premissas_inputs.append(p_in)

    st.write("#### Conclusão:")
    conclusao_input = st.text_input("Conclusão do Argumento:", value="q", key="conclusao")

    if st.button("Avaliar Validade do Argumento", key="btn_infer"):
        if premissas_inputs and conclusao_input:
            try:
                df_argumento, eh_valido, explicacao = motor.processar_argumento(premissas_inputs, conclusao_input)
                
                if eh_valido:
                    st.success("### 🟩 Veredito: O argumento é VÁLIDO (Dedução Legítima)")
                else:
                    st.error("### 🟥 Veredito: O argumento é INVÁLIDO (Falácia Lógica)")
                
                # Renderiza a caixa com a explicação teórica do Silogismo/Argumento
                st.info(explicacao)

                st.write("#### Análise da Tabela-Verdade do Argumento:")
                st.dataframe(df_argumento, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao processar o argumento: {e}")
        else:
            st.warning("Certifique-se de preencher as premissas e a conclusão.")
