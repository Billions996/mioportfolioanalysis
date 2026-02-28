import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Analisi Portafoglio PRO", layout="wide")

st.title("📈 Analizzatore di Portafoglio Avanzato")

# Sidebar per input
with st.sidebar:
    st.header("Configurazione")
    tickers = st.text_input("Inserisci Ticker (es: AAPL, TSLA, BTC-USD, gold)", "AAPL, MSFT, GOOGL, AMZN")
    periodo = st.selectbox("Periodo Storico", ["1y", "2y", "5y", "10y"], index=2)

if tickers:
    # Download dati
    lista_tickers = [t.strip() for t in tickers.split(",")]
    df = yf.download(lista_tickers, period=periodo)['Adj Close']
    
    if not df.empty:
        # Calcoli base
        returns = df.pct_change().dropna()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()
        
        # Simulazione Portafogli Casuali
        num_portfolios = 1000
        results = np.zeros((3, num_portfolios))
        for i in range(num_portfolios):
            weights = np.random.random(len(lista_tickers))
            weights /= np.sum(weights)
            
            p_return = np.sum(mean_returns * weights) * 252
            p_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
            
            results[0,i] = p_std
            results[1,i] = p_return
            results[2,i] = p_return / p_std # Sharpe Ratio base

        # Visualizzazione
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Performance Cumulata")
            st.line_chart(df / df.iloc[0])

        with col2:
            st.subheader("Frontiera Efficiente (Simulata)")
            fig = px.scatter(x=results[0, :], y=results[1, :], color=results[2, :],
                             labels={'x': 'Rischio (Volatilità)', 'y': 'Rendimento Atteso', 'color': 'Sharpe Ratio'})
            st.plotly_chart(fig)

        st.subheader("Matrice di Correlazione")
        st.dataframe(returns.corr().style.background_gradient(cmap='coolwarm'))
