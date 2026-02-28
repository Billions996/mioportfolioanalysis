import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Portfolio Analysis")

# Input dell'utente
lista_tickers = st.text_input(
    "Inserisci i ticker separati da una virgola (es: AAPL,MSFT,GOOGL)"
).upper().replace(" ", "").split(",")

periodo = st.selectbox(
    "Seleziona il periodo",
    ["1mo", "3mo", "6mo", "1y", "5y", "10y", "max"]
)

if st.button("Scarica dati"):
    if not lista_tickers or lista_tickers == ['']:
        st.error("Inserisci almeno un ticker valido.")
    else:
        try:
            # Scarica dati da Yahoo Finance
            df = yf.download(lista_tickers, period=periodo)

            # Gestione MultiIndex per più ticker
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs('Adj Close', axis=1, level=0)
            else:
                # Controlla che 'Adj Close' esista
                if 'Adj Close' in df.columns:
                    df = df['Adj Close']
                else:
                    st.error("Colonna 'Adj Close' non trovata nei dati scaricati.")
                    st.stop()

            st.success("Dati scaricati correttamente!")
            st.dataframe(df)

            # Puoi aggiungere grafici
            st.line_chart(df)

        except Exception as e:
            st.error(f"Errore durante il download dei dati: {e}")
