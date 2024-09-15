import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_option_menu import option_menu

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('livros.db')
cursor = conn.cursor()

# Criar tabela de livros se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    preco REAL NOT NULL,
    data_cadastro TEXT,
    exemplares INTEGER,
    data_venda TEXT,
    quantidade_vendida INTEGER,
    valor_recebido REAL,
    local_venda TEXT
)
''')
conn.commit()

# Função para adicionar um livro ao banco de dados
def adicionar_livro(titulo, autor, preco, data_cadastro, exemplares):
    cursor.execute('''
        INSERT INTO livros (titulo, autor, preco, data_cadastro, exemplares) 
        VALUES (?, ?, ?, ?, ?)
    ''', (titulo, autor, preco, data_cadastro, exemplares))
    conn.commit()

# Função para registrar uma venda
def registrar_venda(titulo, data_venda, quantidade_vendida, valor_recebido, local_venda):
    cursor.execute('''
        UPDATE livros SET data_venda = ?, quantidade_vendida = ?, valor_recebido = ?, local_venda = ? 
        WHERE titulo = ?
    ''', (data_venda, quantidade_vendida, valor_recebido, local_venda, titulo))
    conn.commit()

# Exibir os livros no banco de dados
def exibir_livros():
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    return livros

# Interface Streamlit
st.title('Dashboard de Vendas de Livros')

# Menu de navegação
menu_escolhido = option_menu(
    menu_title=None,
    options=["Adicionar Livro", "Registrar Venda", "Visualizar Vendas e Gráficos"],
    icons=["book", "cart", "bar-chart-line"],
    default_index=0,
    orientation="horizontal"
)

# Página: Adicionar Livro
if menu_escolhido == "Adicionar Livro":
    st.header('Adicionar Livro')
    
    with st.form(key='adicionar_livro'):
        titulo = st.text_input('Título do Livro')
        autor = st.text_input('Autor do Livro')
        preco = st.number_input('Preço', min_value=0.0, format="%.2f")
        data_cadastro = st.date_input('Data de Cadastro do Livro')
        exemplares = st.number_input('Número de Exemplares', min_value=1, step=1)
        
        submit_livro = st.form_submit_button('Adicionar Livro')

        if submit_livro:
            adicionar_livro(titulo, autor, preco, data_cadastro.strftime('%Y-%m-%d'), exemplares)
            st.success(f'Livro "{titulo}" adicionado com sucesso!')

# Página: Registrar Venda
elif menu_escolhido == "Registrar Venda":
    st.header('Registrar Venda')
    titulos_livros = [livro[1] for livro in exibir_livros()]  # Obter todos os títulos de livros
    with st.form(key='registrar_venda'):
        titulo_venda = st.selectbox('Escolha o título do livro', titulos_livros)
        data_venda = st.date_input('Data da Venda')
        quantidade_vendida = st.number_input('Quantidade Vendida', min_value=1, step=1)
        valor_recebido = st.number_input('Valor Recebido', min_value=0.0, format="%.2f")
        local_venda = st.text_input('Local da Venda')
        submit_venda = st.form_submit_button('Registrar Venda')

        if submit_venda:
            registrar_venda(titulo_venda, data_venda.strftime('%Y-%m-%d'), quantidade_vendida, valor_recebido, local_venda)
            st.success(f'Venda do livro "{titulo_venda}" registrada com sucesso no local "{local_venda}"!')

# Página: Visualizar Vendas e Gráficos
elif menu_escolhido == "Visualizar Vendas e Gráficos":
    st.header('Visualização de Vendas e Análise')

    # Exibir os dados em uma tabela
    livros_vendidos = pd.read_sql_query("SELECT * FROM livros", conn)
    st.dataframe(livros_vendidos)

    # Preparar dados para os gráficos
    if not livros_vendidos.empty:
        livros_vendidos['data_venda'] = pd.to_datetime(livros_vendidos['data_venda'], errors='coerce')
        livros_vendidos = livros_vendidos.dropna(subset=['data_venda'])
        livros_vendidos = livros_vendidos.sort_values(by='data_venda')

        # Gráfico de Linhas: Valor Recebido e Quantidade Vendida ao Longo do Tempo
        fig = px.line(livros_vendidos, x='data_venda', y=['valor_recebido', 'quantidade_vendida'],
                      labels={'data_venda': 'Data da Venda', 'value': 'Valor/Quantidade'},
                      title='Valor Recebido e Quantidade Vendida ao Longo do Tempo',
                      markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico de Barras: Quantidade Vendida ao Longo do Tempo (Horizontal)
        fig2 = px.bar(livros_vendidos, x='quantidade_vendida', y='data_venda',
                      orientation='h',
                      labels={'data_venda': 'Data da Venda', 'quantidade_vendida': 'Quantidade Vendida'},
                      title='Quantidade Vendida ao Longo do Tempo')
        st.plotly_chart(fig2, use_container_width=True)
        
    else:
        st.write("Não há dados suficientes para gerar gráficos.")
