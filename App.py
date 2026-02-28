import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title("Portfolio Analysis con Rendimenti e Volatilità")

# Input dell'utente
lista_tickers = st.text_input(
    "Inserisci i ticker separati da una virgola (es: AAPL,MSFT,GOOGL)"
).upper().replace(" ", "").split(",")
lista_tickers = [t for t in lista_tickers if t]  # rimuove stringhe vuote

periodo = st.selectbox(
    "Seleziona il periodo",
    ["1mo", "3mo", "6mo", "1y", "5y", "10y", "max"]
)

# Pesatura portafoglio
st.write("Inserisci la percentuale di ciascun titolo (totale deve fare 100%)")
pesi = []
if lista_tickers:
    for t in lista_tickers:
        peso = st.number_input(f"% di {t}", min_value=0.0, max_value=100.0, value=100.0/len(lista_tickers))
        pesi.append(peso/100)  # converti in frazione

if st.button("Analizza Portafoglio"):
    if not lista_tickers:
        st.error("Inserisci almeno un ticker valido.")
    else:
        try:
            # Scarica dati da Yahoo Finance
            df = yf.download(lista_tickers, period=periodo)

            if df.empty:
                st.error("Nessun dato scaricato. Controlla i ticker o il periodo.")
            else:
                # Gestione MultiIndex o singolo livello
                if isinstance(df.columns, pd.MultiIndex):
                    if 'Adj Close' in df.columns.levels[0]:
                        df = df.xs('Adj Close', axis=1, level=0)
                    elif 'Close' in df.columns.levels[0]:
                        df = df.xs('Close', axis=1, level=0)
                        st.warning("Colonna 'Adj Close' non trovata. Uso 'Close' al suo posto.")
                    else:
                        st.error("Nessuna colonna di prezzi disponibile")
                        st.stop()
                else:
                    if 'Adj Close' in df.columns:
                        df = df['Adj Close']
                    elif 'Close' in df.columns:
                        df = df['Close']
                        st.warning("Colonna 'Adj Close' non trovata. Uso 'Close' al suo posto.")
                    else:
                        st.error("Nessuna colonna di prezzi disponibile")
                        st.stop()

                st.subheader("Serie Storiche")
                st.dataframe(df)
                st.line_chart(df)

                # Rendimenti giornalieri
                rendimenti_giornalieri = df.pct_change().dropna()

                # Rendimento medio annuo
                rendimenti_medio_annuo = rendimenti_giornalieri.mean() * 252  # 252 giorni di trading

                # Volatilità annua
                volatilita_annua = rendimenti_giornalieri.std() * np.sqrt(252)

                # Calcolo rendimento e volatilità portafoglio
                pesi_array = np.array(pesi)
                rend_portafoglio = np.dot(rendimenti_medio_annuo, pesi_array)
                cov_matrix = rendimenti_giornalieri.cov() * 252
                volatilita_portafoglio = np.sqrt(np.dot(pesi_array.T, np.dot(cov_matrix, pesi_array)))

                # Mostra risultati
                st.subheader("Rendimenti e Volatilità Titoli")
                tabella_titoli = pd.DataFrame({
                    "Rendimento Medio Annuo": rendimenti_medio_annuo,
                    "Volatilità Annua": volatilita_annua
                })
                st.dataframe(tabella_titoli.style.format("{:.2%}"))

                st.subheader("Rendimenti e Volatilità Portafoglio")
                st.write(f"Rendimento atteso portafoglio: **{rend_portafoglio:.2%}**")
                st.write(f"Volatilità portafoglio: **{volatilita_portafoglio:.2%}**")

        except Exception as e:
            st.error(f"Errore durante l'analisi: {e}")
