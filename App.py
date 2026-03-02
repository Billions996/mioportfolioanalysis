import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import difflib

# ==========================
# Configurazione pagina
# ==========================
st.set_page_config(
    page_title="Analisi Portafoglio",
    page_icon="📈",
    layout="wide"
)

st.title("Portfolio Completo Multilingua - Azioni, Obbligazioni, Materie Prime e Markowitz")

# ==========================
# Dizionario Nome → Ticker
# ==========================
nome_to_ticker = {
    "S&P 500": "^GSPC",
    "NASDAQ 100": "^NDX",
    "Dow Jones": "^DJI",
    "FTSE MIB": "FTSEMIB.MI",
    "Oro": "GLD",
    "Gold": "GLD",
    "Azioni USA": "IVV",
    "Azioni Europa": "IEUR",
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
}

# ==========================
# Funzione fuzzy match
# ==========================
def trova_ticker(input_nome, dizionario):
    nomi = list(dizionario.keys())
    match = difflib.get_close_matches(input_nome, nomi, n=1, cutoff=0.5)
    if match:
        return dizionario[match[0]], match[0]
    return None, None

# ==========================
# Sidebar input
# ==========================
st.sidebar.header("Configurazione Portafoglio")
lista_nomi_input = st.sidebar.text_input(
    "Nomi strumenti (separati da virgola)", "S&P 500, Oro, Apple"
).title().split(",")

lista_tickers = []
nomi_usati = []

for nome in lista_nomi_input:
    nome = nome.strip()
    ticker, nome_trovato = trova_ticker(nome, nome_to_ticker)
    if ticker:
        lista_tickers.append(ticker)
        nomi_usati.append(nome_trovato)
    else:
        st.sidebar.warning(f"{nome} non trovato")

if not lista_tickers:
    st.stop()

# ==========================
# Pesi
# ==========================
st.sidebar.subheader("Pesi (%)")
pesi = []
for n in nomi_usati:
    p = st.sidebar.number_input(n, 0.0, 100.0, 100.0/len(nomi_usati))
    pesi.append(p / 100)

pesi_arr = np.array(pesi)
pesi_arr /= pesi_arr.sum()

periodo = st.sidebar.selectbox("Periodo", ["1y", "3y", "5y", "10y", "max"])

# ==========================
# Analisi
# ==========================
if st.sidebar.button("Analizza Portafoglio"):

    df = yf.download(lista_tickers, period=periodo)

    if isinstance(df.columns, pd.MultiIndex):
        df = df["Adj Close"] if "Adj Close" in df.columns.levels[0] else df["Close"]
    else:
        df = df["Adj Close"] if "Adj Close" in df.columns else df["Close"]

    df = df.dropna()

    nome_to_ticker_usati = dict(zip(nomi_usati, lista_tickers))

    # ==========================
    # Prezzi normalizzati
    # ==========================
    df_norm = df / df.iloc[0] * 100
    fig, ax = plt.subplots(figsize=(12,6))
    for nome in nomi_usati:
        ax.plot(df_norm.index, df_norm[nome_to_ticker_usati[nome]], label=nome)
    ax.legend()
    ax.set_title("Prezzi Normalizzati")
    st.pyplot(fig)

    # ==========================
    # Statistiche
    # ==========================
    rendimenti = df.pct_change().dropna()
    mu = rendimenti.mean() * 252
    sigma = rendimenti.cov() * 252

    rend_port = np.dot(mu, pesi_arr)
    vol_port = np.sqrt(np.dot(pesi_arr.T, np.dot(sigma, pesi_arr)))

    st.subheader("Portafoglio Selezionato")
    for i, nome in enumerate(nomi_usati):
        st.write(f"{nome}: {pesi_arr[i]*100:.2f}%")

    st.write(f"Rendimento atteso: **{rend_port:.2%}**")
    st.write(f"Volatilità: **{vol_port:.2%}**")

    # ==========================
    # Frontiera efficiente (FIX)
    # ==========================
    num_portfolios = 100

    vols = []
    rends = []
    sharpes = []
    weights = []

    for _ in range(num_portfolios):
        w = np.random.random(len(lista_tickers))
        w /= np.sum(w)

        port_r = np.dot(mu, w)
        port_v = np.sqrt(np.dot(w.T, np.dot(sigma, w)))
        sharpe = port_r / port_v

        vols.append(port_v)
        rends.append(port_r)
        sharpes.append(sharpe)
        weights.append(w)

    vols = np.array(vols)
    rends = np.array(rends)
    sharpes = np.array(sharpes)
    weights = np.array(weights)

    max_idx = np.argmax(sharpes)

    fig, ax = plt.subplots(figsize=(12,6))
    sc = ax.scatter(vols, rends, c=sharpes, cmap="viridis", s=60)
    ax.scatter(vol_port, rend_port, color="red", marker="X", s=200, label="Portafoglio Selezionato")
    ax.scatter(vols[max_idx], rends[max_idx], color="gold", marker="*", s=300, label="Max Sharpe")
    ax.set_xlabel("Volatilità")
    ax.set_ylabel("Rendimento")
    ax.set_title("Frontiera Efficiente")
    ax.legend()
    fig.colorbar(sc, label="Sharpe Ratio")
    st.pyplot(fig)
