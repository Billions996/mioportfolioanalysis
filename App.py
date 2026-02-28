import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Portafoglio di Markowitz (Frontiera Efficiente)")

# Input tickers
lista_tickers = st.text_input(
    "Inserisci i ticker separati da una virgola (es: AAPL,MSFT,GOOGL)"
).upper().replace(" ", "").split(",")
lista_tickers = [t for t in lista_tickers if t]

periodo = st.selectbox(
    "Seleziona il periodo",
    ["1y", "3y", "5y", "10y", "max"]
)

if st.button("Genera Portafoglio di Markowitz"):

    if not lista_tickers:
        st.error("Inserisci almeno un ticker valido.")
    else:
        # Scarica dati
        df = yf.download(lista_tickers, period=periodo)

        # Se MultiIndex, seleziona 'Adj Close' o 'Close'
        if isinstance(df.columns, pd.MultiIndex):
            if 'Adj Close' in df.columns.levels[0]:
                df = df.xs('Adj Close', axis=1, level=0)
            else:
                df = df.xs('Close', axis=1, level=0)
                st.warning("Usando 'Close' al posto di 'Adj Close'")
        else:
            if 'Adj Close' in df.columns:
                df = df['Adj Close']
            else:
                df = df['Close']
                st.warning("Usando 'Close' al posto di 'Adj Close'")

        if df.empty:
            st.error("Nessun dato scaricato.")
            st.stop()

        st.subheader("Serie Storiche")
        st.line_chart(df)

        # Rendimenti giornalieri
        rendimenti = df.pct_change().dropna()
        media_rendimenti = rendimenti.mean() * 252  # annualizzati
        cov_matrix = rendimenti.cov() * 252         # annualizzata

        # Simulazioni portafoglio
        num_portfolios = 5000
        risultati = np.zeros((3, num_portfolios))
        weights_record = []

        for i in range(num_portfolios):
            pesi = np.random.random(len(lista_tickers))
            pesi /= np.sum(pesi)
            weights_record.append(pesi)

            port_return = np.dot(pesi, media_rendimenti)
            port_vol = np.sqrt(np.dot(pesi.T, np.dot(cov_matrix, pesi)))
            sharpe = port_return / port_vol

            risultati[0,i] = port_return
            risultati[1,i] = port_vol
            risultati[2,i] = sharpe

        # Trova portafoglio con massimo Sharpe
        max_sharpe_idx = np.argmax(risultati[2])
        pesi_max_sharpe = weights_record[max_sharpe_idx]
        rendimento_max_sharpe = risultati[0,max_sharpe_idx]
        volatilita_max_sharpe = risultati[1,max_sharpe_idx]

        st.subheader("Portafoglio con massimo Sharpe Ratio")
        for i, t in enumerate(lista_tickers):
            st.write(f"{t}: {pesi_max_sharpe[i]*100:.2f}%")
        st.write(f"Rendimento atteso: {rendimento_max_sharpe:.2%}")
        st.write(f"Volatilità: {volatilita_max_sharpe:.2%}")
        st.write(f"Sharpe Ratio: {risultati[2,max_sharpe_idx]:.2f}")

        # Grafico frontiera efficiente
        plt.figure(figsize=(10,6))
        plt.scatter(risultati[1,:], risultati[0,:], c=risultati[2,:], cmap='viridis', marker='o', s=10, alpha=0.3)
        plt.colorbar(label='Sharpe Ratio')
        plt.scatter(volatilita_max_sharpe, rendimento_max_sharpe, marker='*', color='r', s=500, label='Massimo Sharpe')
        plt.title('Portafogli Simulati - Frontiera Efficiente')
        plt.xlabel('Volatilità Annua')
        plt.ylabel('Rendimento Atteso Annua')
        plt.legend()
        st.pyplot(plt)
