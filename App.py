import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import difflib

st.title("Portfolio Completo Multilingua - Azioni, Obbligazioni, Materie Prime e Markowitz")

# ==========================
# Dizionario Nome → Ticker Yahoo Finance
# Supporta italiano e inglese
# ==========================
nome_to_ticker = {
    # INDICI AZIONARI
    "S&P 500": "^GSPC",
    "NASDAQ 100": "^NDX",
    "Dow Jones": "^DJI",
    "FTSE 100": "^FTSE",
    "DAX 30": "^GDAXI",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "FTSE MIB": "FTSEMIB.MI",
    "CAC 40": "^FCHI",
    "IBEX 35": "^IBEX",
    "MSCI Mondo": "URTH",
    "MSCI World": "URTH",
    "MSCI Mercati Emergenti": "EEM",
    "MSCI Emerging Markets": "EEM",
    "Euro Stoxx 50": "FEZ",
    "Asia Pacifico sviluppati": "EPP",
    "Asia Pacific Developed": "EPP",

    # ETF OBBLIGAZIONARI - GOVERNATIVI EURO
    "Obbligazioni governative euro breve termine": "IBTS.DE",
    "Euro Gov Bond Short Term": "IBTS.DE",
    "Obbligazioni governative euro medio-lungo termine": "IBGL.DE",
    "Euro Gov Bond Medium-Long": "IBGL.DE",

    # ETF OBBLIGAZIONARI - CORPORATE EURO
    "Obbligazioni corporate euro breve termine": "IBCS.DE",
    "Euro Corporate Bond Short Term": "IBCS.DE",
    "Obbligazioni corporate euro medio-lungo termine": "IBCL.DE",
    "Euro Corporate Bond Medium-Long": "IBCL.DE",

    # ETF OBBLIGAZIONARI - EMERGING
    "Obbligazioni mercati emergenti": "EMB",
    "Emerging Market Bond": "EMB",

    # ETF OBBLIGAZIONARI - GIAPPONE/UK
    "Obbligazioni governative giapponesi": "JPGB.L",
    "Japanese Gov Bond": "JPGB.L",
    "Obbligazioni governative inglesi": "IGLT.L",
    "UK Gov Bond": "IGLT.L",

    # ETF AZIONARI - EURO/USA/EMERGING/ASIA PACIFICO
    "Azioni Europa": "IEUR",
    "Equity Euro": "IEUR",
    "Azioni USA": "IVV",
    "Equity USA": "IVV",
    "Azioni mercati emergenti": "EEM",
    "Equity Emerging": "EEM",
    "Azioni Asia Pacifico sviluppati": "EPP",
    "Equity Asia Pacific Developed": "EPP",

    # MATERIE PRIME
    "Oro": "GLD",
    "Gold": "GLD",
    "Argento": "SLV",
    "Silver": "SLV",
    "Petrolio WTI": "USO",
    "Oil WTI": "USO",
    "Rame": "CPER",
    "Copper": "CPER",
    "Agricoltura": "DBA",
    "Agriculture": "DBA",

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
    "Stellantis": "STLA.MI",
    "Siemens": "SIE.DE",
    "SAP": "SAP.DE"
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
# Input nomi strumenti
# ==========================
lista_nomi = st.text_input(
    "Inserisci nomi di indici, azioni, ETF o materie prime (italiano o inglese), separati da virgola"
).title().split(",")

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

# ==========================
# Input pesi personalizzati
# ==========================
st.write("Inserisci i pesi percentuali per ciascun strumento (totale 100%)")
pesi = []
for n in nomi_usati:
    peso = st.number_input(f"% di {n}", min_value=0.0, max_value=100.0, value=100.0/len(nomi_usati))
    pesi.append(peso/100)

# Normalizzazione automatica dei pesi
pesi_arr = np.array(pesi)
if np.sum(pesi_arr) != 1:
    st.warning("I pesi non sommano a 100%, normalizzo automaticamente.")
    pesi_arr /= np.sum(pesi_arr)

# ==========================
# Selezione periodo storico
# ==========================
periodo = st.selectbox("Seleziona il periodo storico", ["1y","3y","5y","10y","max"])

if st.button("Analizza Portafoglio"):

    # ==========================
    # Scarica dati
    # ==========================
    df = yf.download(lista_tickers, period=periodo)
    if df.empty:
        st.error("Nessun dato scaricato!")
        st.stop()

    # Gestione MultiIndex / singolo livello
    if isinstance(df.columns, pd.MultiIndex):
        if 'Adj Close' in df.columns.levels[0]:
            df = df.xs('Adj Close', axis=1, level=0)
        else:
            df = df.xs('Close', axis=1, level=0)
            st.warning("Uso 'Close' al posto di 'Adj Close'.")
    else:
        df = df['Adj Close'] if 'Adj Close' in df.columns else df['Close']

    st.subheader("Serie Storiche")
    st.line_chart(df)

    # ==========================
    # Rendimenti e covarianza
    # ==========================
    rendimenti = df.pct_change().dropna()
    mu = rendimenti.mean() * 252
    sigma = rendimenti.cov() * 252

    # Portafoglio con pesi utente
    rend_port = np.dot(mu, pesi_arr)
    vol_port = np.sqrt(np.dot(pesi_arr.T, np.dot(sigma, pesi_arr)))

    st.subheader("Portafoglio Selettivo")
    for i, nome in enumerate(nomi_usati):
        st.write(f"{nome}: {pesi_arr[i]*100:.2f}%")
    st.write(f"Rendimento atteso: **{rend_port:.2%}**")
    st.write(f"Volatilità: **{vol_port:.2%}**")

    # ==========================
    # Simulazione Markowitz
    # ==========================
    num_portfolios = 5000
    results = np.zeros((3, num_portfolios))
    weights_record = []

    for i in range(num_portfolios):
        w = np.random.random(len(lista_tickers))
        w /= np.sum(w)
        weights_record.append(w)
        results[0,i] = np.dot(mu, w)
        results[1,i] = np.sqrt(np.dot(w.T, np.dot(sigma, w)))
        results[2,i] = results[0,i]/results[1,i]

    max_sharpe_idx = np.argmax(results[2])
    w_star = weights_record[max_sharpe_idx]

    st.subheader("Markowitz - Portafoglio Ottimale (Max Sharpe)")
    for i, nome in enumerate(nomi_usati):
        st.write(f"{nome}: {w_star[i]*100:.2f}%")
    st.write(f"Rendimento Sharpe ottimale: **{results[0,max_sharpe_idx]:.2%}**")
    st.write(f"Volatilità Sharpe ottimale: **{results[1,max_sharpe_idx]:.2%}**")
    st.write(f"Sharpe Ratio: **{results[2,max_sharpe_idx]:.2f}**")

    # ==========================
    # Grafico frontiera efficiente
    # ==========================
    plt.figure(figsize=(10,6))
    plt.scatter(results[1,:], results[0,:], c=results[2,:], cmap='viridis', s=10, alpha=0.3)
    plt.colorbar(label='Sharpe Ratio')
    plt.scatter(results[1,max_sharpe_idx], results[0,max_sharpe_idx], marker='*', color='r', s=500, label='Massimo Sharpe')
    plt.xlabel('Volatilità')
    plt.ylabel('Rendimento')
    plt.title('Portafogli Simulati - Frontiera Efficiente')
    plt.legend()
    st.pyplot(plt)
