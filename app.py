import streamlit as st
import pandas as pd
import itertools
import re

class MotorLogico:
    def __init__(self):
        # Mapeamento de conectivos para operadores válidos do Python
        self.REPLACEMENTS = [
            ('<->', '=='),
            ('->', ' <= '),  # P -> Q é equivalente a P <= Q em lógica booleana no Python [cite: 27, 28]
            ('~', ' not '),
            ('&', ' and '),
            ('|', ' or ')
        ]

    def normalizar_expressao(self, expressao: str) -> str:
        """Converte todas as variáveis proposicionais para maiúsculas para evitar duplicidade."""
        # Encontra letras isoladas e as transforma em maiúsculas
        return re.sub(r'\b[a-z]\b', lambda m: m.group(0).upper(), expressao)

    def extrair_variaveis(self, expressoes: list) -> list:
        """Extrai todas as variáveis proposicionais (letras isoladas, maiúsculas ou minúsculas)."""
        variaveis = set()
        for expr in expressoes:
            # Modificado para aceitar letras de 'a' a 'z' (minúsculas) e 'A' a 'Z' (maiúsculas)
            encontradas = re.findall(r'\b[a-zA-Z]\b', expr)
            # Padroniza tudo em maiúsculo no conjunto para evitar 'p' e 'P' duplicados
            variaveis.update([v.upper() for v in encontradas])
        return sorted(list(variaveis))

    def preparar_expressao(self, expressao: str) -> str:
        """Traduz a expressão normalizada para a sintaxe do Python."""
        expr_traduzida = self.normalizar_expressao(expressao)
        for logico, python in self.REPLACEMENTS:
            expr_traduzida = expr_traduzida.replace(logico, python)
        return expr_traduzida

    def avaliar_linha(self, expressao_preparada: str, contexto: dict) -> bool:
        """Avalia o valor-verdade de uma expressão usando o eval nativo[cite: 41, 43]."""
        try:
            return bool(eval(expressao_preparada, {}, contexto))
        except Exception as e:
            raise SyntaxError(f"Erro de sintaxe na expressão. Verifique os parênteses e conectivos.")

    def gerar_combinacoes(self, variaveis: list) -> list:
        """Gera a árvore de possibilidades binárias (True/False)[cite: 31, 42]."""
        return list(itertools.product([True, False], repeat=len(variaveis)))

    def formatar_booleano(self, valor: bool) -> str:
        """Mapeia True/False para V/F para exibição acadêmica[cite: 32]."""
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

            # Exibe os cabeçalhos das expressões de forma normalizada (maiúsculas)
            linha = {v: self.formatar_booleano(contexto[v]) for v in variaveis}
            linha[self.normalizar_expressao(expr1)] = self.formatar_booleano(res1)
            linha[self.normalizar_expressao(expr2)] = self.formatar_booleano(res2)
            linhas_tabela.append(linha)

        df = pd.DataFrame(linhas_tabela)
        return df, equivalentes

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

            # Um argumento é inválido se as premissas forem V e a conclusão for F [cite: 39]
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
        return df, argumento_valido


# =====================================================================
#                         INTERFACE STREAMLIT
# =====================================================================

st.set_page_config(page_title="Motor Lógico - UFN", page_icon="🧠", layout="wide") [cite: 1, 2]

st.title("🧠 Protótipo de Motor Lógico em Python") [cite: 9, 14]
st.markdown("""
Mapeamento de Tabelas-Verdade, Equivalências e Motores de Inferência Aplicados à IA.  
*Desenvolvido para a disciplina de Lógica para Computação (Prof. Leandro Ribeiro Fontoura).* [cite: 5, 6, 10]
""")

st.sidebar.header("Guia de Conectivos") [cite: 23]
st.sidebar.markdown("""
Use a seguinte sintaxe para as expressões:
* **Negação:** `~p` [cite: 24]
* **Conjunção (E):** `p & q` [cite: 25]
* **Disjunção (OU):** `p | q` [cite: 26]
* **Condicional:** `p -> q` [cite: 27]
* **Bicondicional:** `p <-> q` [cite: 28]
* *Agora você pode utilizar tanto letras **minúsculas** quanto **maiúsculas** para as variáveis!*
""")

motor = MotorLogico()

# Criação das abas para organização do Trabalho Prático [cite: 17]
tab_equiv, tab_inferencia = st.tabs([
    "Módulo B: Provador de Equivalência", [cite: 29]
    "Módulo C: Motor de Inferência (Validador)" [cite: 37]
])

# --- ABA: PROVADOR DE EQUIVALÊNCIA ---
with tab_equiv:
    st.header("Verificador de Equivalência Lógica") [cite: 29]
    st.write("Insira duas expressões para verificar se elas possuem tabelas-verdade idênticas (Ex: Leis de De Morgan).") [cite: 30, 33]
    
    col1, col2 = st.columns(2)
    with col1:
        e1 = st.text_input("Primeira Expressão (Entrada 1):", value="~(p & q)") [cite: 34]
    with col2:
        e2 = st.text_input("Segunda Expressão (Entrada 2):", value="~p | ~q") [cite: 35]

    if st.button("Calcular Equivalência", key="btn_equiv"):
        if e1 and e2:
            try:
                df_resultado, sao_equivalentes = motor.processar_equivalencia(e1, e2)
                
                # Exibição do Veredito [cite: 32]
                if sao_equivalentes:
                    st.success("### 🟩 Resposta: Expressões LOGICAMENTE EQUIVALENTES") [cite: 36]
                else:
                    st.error("### 🟥 Resposta: Expressões NÃO SÃO EQUIVALENTES")
                
                # Renderização da Tabela Verdade Completa
                st.write("#### Tabela-Verdade Gerada:") [cite: 32]
                st.dataframe(df_resultado, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
        else:
            st.warning("Por favor, preencha ambas as expressões.")

# --- ABA: MOTOR DE INFERÊNCIA ---
with tab_inferencia:
    st.header("Validador de Argumentos Lógicos") [cite: 37]
    st.write("Defina um conjunto de premissas e veja se a conclusão decorre logicamente delas.") [cite: 38]

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
    st.write("#### Premissas:") [cite: 38]
    
    # Valores default demonstrativos em minúsculas (Modus Ponens) [cite: 47]
    defaults_premissas = ["p -> q", "p"]
    
    for i in range(st.session_state.num_premissas):
        val_default = defaults_premissas[i] if i < len(defaults_premissas) else ""
        p_in = st.text_input(f"Premissa {i+1}:", value=val_default, key=f"premissa_{i}")
        if p_in:
            premissas_inputs.append(p_in)

    st.write("#### Conclusão:") [cite: 38]
    conclusao_input = st.text_input("Conclusão do Argumento:", value="q", key="conclusao") [cite: 38]

    if st.button("Avaliar Validade do Argumento", key="btn_infer"):
        if premissas_inputs and conclusao_input:
            try:
                df_argumento, eh_valido = motor.processar_argumento(premissas_inputs, conclusao_input)
                
                if eh_valido:
                    st.success("### 🟩 Veredito: O argumento é VÁLIDO (Dedução Legítima)") [cite: 39]
                else:
                    st.error("### 🟥 Veredito: O argumento é INVÁLIDO (Falácia Lógica)") [cite: 39]
                    st.info("💡 Uma falácia ocorre quando todas as premissas são Verdadeiras (V), mas a conclusão é Falsa (F). Veja as linhas sinalizadas na tabela abaixo.") [cite: 39]

                st.write("#### Análise da Tabela-Verdade do Argumento:") [cite: 39]
                st.dataframe(df_argumento, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao processar o argumento: {e}")
        else:
            st.warning("Certifique-se de preencher as premissas e a conclusão.")
