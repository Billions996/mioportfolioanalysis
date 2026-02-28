import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import difflib

st.title("Portfolio Completo Multilingua - Azioni, Obbligazioni, Materie Prime e Markowitz")

# ==========================
# Dizionario Nome → Ticker Yahoo Finance (Italiano / Inglese)
# ==========================
nome_to_ticker = {
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
    # ETF OBBLIGAZIONARI
    "Obbligazioni governative euro breve termine": "IBTS.DE",
    "Euro Gov Bond Short Term": "IBTS.DE",
    "Obbligazioni governative euro medio-lungo termine": "IBGL.DE",
    "Euro Gov Bond Medium-Long": "IBGL.DE",
    "Obbligazioni corporate euro breve termine": "IBCS.DE",
    "Euro Corporate Bond Short Term": "IBCS.DE",
    "Obbligazioni corporate euro medio-lungo termine": "IBCL.DE",
    "Euro Corporate Bond Medium-Long": "IBCL.DE",
    "Obbligazioni mercati emergenti": "EMB",
    "Emerging Market Bond": "EMB",
    "Obbligazioni governative giapponesi": "JPGB.L",
    "Japanese Gov Bond": "JPGB.L",
    "Obbligazioni governative inglesi": "IGLT.L",
    "UK Gov Bond": "IGLT.L",
    # ETF AZIONARI
    "Azioni Europa": "IEUR",
    "Equity Euro": "IEUR",
    "Azioni USA": "IVV",
    "Equity USA": "IVV",
    "Azioni mercati emergenti": "EEM",
    "Equity Emerging": "EEM",
    "Azioni Asia Pacifico sviluppati": "EPP",
    "Equity Asia Pacific Developed": "EPP",
    # Materie prime
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
    # Titoli USA
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Tesla": "TSLA",
    "Meta": "META",
    "NVIDIA": "NVDA",
    "Netflix": "NFLX",
    # Titoli Europa / Italia
    "Enel": "ENEL.MI",
    "Intesa Sanpaolo": "ISP.MI",
    "UniCredit": "UCG.MI",
    "Ferrari": "RACE.MI",
    "Stellantis": "STLA.MI",
    "Siemens": "SIE.DE",
    "SAP": "SAP.DE"
}

# ==========================
# Fuzzy matching
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

pesi_arr = np.array(pesi)
if np.sum(pesi_arr) != 1:
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

    if isinstance(df.columns, pd.MultiIndex):
        if 'Adj Close' in df.columns.levels[0]:
            df = df['Adj Close']
        else:
            df = df['Close']
    else:
        if 'Adj Close' in df.columns:
            df = df['Adj Close']
        else:
            df = df['Close']

    # ==========================
    # Mapping nome -> ticker per grafico e statistiche
    # ==========================
    nome_to_ticker_usati = dict(zip(nomi_usati, lista_tickers))

    # ==========================
    # Prezzi normalizzati
    # ==========================
    df_norm = df / df.iloc[0] * 100
    plt.figure(figsize=(10,6))
    for nome in nomi_usati:
        ticker = nome_to_ticker_usati[nome]
        plt.plot(df_norm.index, df_norm[ticker], label=nome)
    plt.xlabel("Data")
    plt.ylabel("Prezzo Normalizzato")
    plt.title("Evoluzione Prezzi Normalizzati")
    plt.legend()
    st.pyplot(plt)

    # ==========================
    # Statistiche finanziarie
    # ==========================
    rendimenti_giornalieri = df.pct_change().dropna()
    rendimenti_annuali = rendimenti_giornalieri.mean() * 252
    vol_annuale = rendimenti_giornalieri.std() * np.sqrt(252)
    rendimento_cumulato = (df.iloc[-1] / df.iloc[0]) - 1

    df_statistiche = pd.DataFrame({
        "Rendimento Cumulato": rendimento_cumulato,
        "Rendimento Annualizzato": rendimenti_annuali,
        "Volatilità Annualizzata": vol_annuale
    }, index=nomi_usati).sort_values("Rendimento Annualizzato", ascending=False)

    st.subheader("Statistiche Finanziarie")
    st.dataframe(df_statistiche.style.format({
        "Rendimento Cumulato": "{:.2%}",
        "Rendimento Annualizzato": "{:.2%}",
        "Volatilità Annualizzata": "{:.2%}"
    }))

    # ==========================
    # Matrice di correlazione
    # ==========================
    correlazioni = rendimenti_giornalieri.corr()
    st.subheader("Matrice di Correlazione")
    st.dataframe(correlazioni.style.background_gradient(cmap="coolwarm"))

    # ==========================
    # Portafoglio utente
    # ==========================
    mu = rendimenti_annuali
    sigma = rendimenti_giornalieri.cov() * 252

    rend_port = np.dot(mu, pesi_arr)
    vol_port = np.sqrt(np.dot(pesi_arr.T, np.dot(sigma, pesi_arr)))

    st.subheader("Portafoglio Selettivo")
    for i, nome in enumerate(nomi_usati):
        st.write(f"{nome}: {pesi_arr[i]*100:.2f}%")
    st.write(f"Rendimento atteso: **{rend_port:.2%}**")
    st.write(f"Volatilità: **{vol_port:.2%}**")

    # ==========================
    # Frontiera efficiente (50 portafogli)
    # ==========================
    num_portfolios = 50
    results = []
    weights_record = []

    for i in range(num_portfolios):
        w = np.random.random(len(lista_tickers))
        w /= np.sum(w)
        weights_record.append(w)
        port_rend = np.dot(mu, w)
        port_vol = np.sqrt(np.dot(w.T, np.dot(sigma, w)))
        sharpe = port_rend / port_vol
        results.append([port_rend, port_vol, sharpe])

    df_frontiera = pd.DataFrame(results, columns=["Rendimento", "Volatilità", "Sharpe"])
    df_frontiera["Peso"] = weights_record
    max_sharpe_idx = df_frontiera["Sharpe"].idxmax()
    df_frontiera["Massimo Sharpe"] = ""
    df_frontiera.loc[max_sharpe_idx, "Massimo Sharpe"] = "⭐"

    st.subheader("Frontiera Efficiente (50 Portafogli)")
    st.dataframe(df_frontiera.style.format({
        "Rendimento": "{:.2%}",
        "Volatilità": "{:.2%}",
        "Sharpe": "{:.2f}"
    }))
