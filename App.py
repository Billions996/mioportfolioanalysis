import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import difflib

st.title("Portfolio di Indici e Titoli - Markowitz con Ricerca Fuzzy")

# Dizionario: Nome → Ticker Yahoo Finance
nome_to_ticker = {
    # INDICI GLOBALI
    "S&P 500": "^GSPC",
    "NASDAQ 100": "^NDX",
    "Dow Jones": "^DJI",
    "FTSE 100": "^FTSE",
    "DAX 30": "^GDAXI",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "FTSE MIB": "^FTSEMIB",
    "CAC 40": "^FCHI",
    "IBEX 35": "^IBEX",
    "Shanghai Composite": "000001.SS",

    # TITOLI USA
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Tesla": "TSLA",
    "Meta": "META",
    "NVIDIA": "NVDA",
    "Netflix": "NFLX",

    # TITOLI EUROPA / ITALIA
    "Enel": "ENEL.MI",
    "Intesa Sanpaolo": "ISP.MI",
    "UniCredit": "UCG.MI",
    "Ferrari": "RACE.MI",
    "Fiat Chrysler": "STLA.MI",
    "Siemens": "SIE.DE",
    "SAP": "SAP.DE"
}

# Funzione fuzzy match
def trova_ticker(input_nome, dizionario):
    """
    Cerca il nome più vicino nel dizionario e restituisce il ticker.
    Se non trova niente di simile (>60% match), ritorna None.
    """
    nomi_dizionario = list(dizionario.keys())
    match = difflib.get_close_matches(input_nome, nomi_dizionario, n=1, cutoff=0.6)
    if match:
        return dizionario[match[0]], match[0]  # ticker e nome trovato
    return None, None

# Input utente
lista_nomi = st.text_input(
    "Inserisci nomi di indici o azioni separati da virgola"
).title().split(",")

# Converti nomi in ticker usando fuzzy match
lista_tickers = []
nomi_usati = []

for nome in lista_nomi:
    nome = nome.strip()
    if nome:
        ticker, nome_trovato = trova_ticker(nome, nome_to_ticker)
        if ticker:
            lista_tickers.append(ticker)
            nomi_usati.append(nome_trovato)
        else:
            st.warning(f"Nome '{nome}' non trovato nel dizionario.")

if not lista_tickers:
    st.stop()

st.write("Ticker utilizzati:", lista_tickers)
st.write("Nomi interpretati:", nomi_usati)

# Seleziona periodo storico
periodo = st.selectbox(
    "Seleziona il periodo",
    ["1y", "3y", "5y", "10y", "max"]
)

if st.button("Analizza Portafoglio"):

    # Scarica dati
    df = yf.download(lista_tickers, period=periodo)

    if df.empty:
        st.error("Nessun dato scaricato. Controlla i ticker o il periodo.")
        st.stop()

    # Gestione MultiIndex / singolo livello
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

    st.subheader("Serie Storiche")
    st.line_chart(df)

    # Rendimenti giornalieri
    rendimenti = df.pct_change().dropna()
    media_rendimenti = rendimenti.mean() * 252  # annualizzati
    cov_matrix = rendimenti.cov() * 252         # annualizzata

    # Simulazione portafogli
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

    # Portafoglio massimo Sharpe
    max_sharpe_idx = np.argmax(risultati[2])
    pesi_max_sharpe = weights_record[max_sharpe_idx]
    rendimento_max_sharpe = risultati[0,max_sharpe_idx]
    volatilita_max_sharpe = risultati[1,max_sharpe_idx]

    st.subheader("Portafoglio con massimo Sharpe Ratio")
    for i, t in enumerate(lista_tickers):
        st.write(f"{nomi_usati[i]} ({t}): {pesi_max_sharpe[i]*100:.2f}%")
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
