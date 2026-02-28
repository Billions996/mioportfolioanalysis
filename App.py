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
# Dizionario Nome → Ticker Yahoo Finance (Italiano / Inglese)
# ==========================
nome_to_ticker = {
    # Indici
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

    # ETF obbligazionari
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

    # ETF azionari
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
# Funzione fuzzy match
# ==========================
def trova_ticker(input_nome, dizionario):
    if not isinstance(dizionario, dict):
        st.error("Errore: dizionario nome_to_ticker non definito correttamente!")
        return None, None
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
    "Nomi strumenti (italiano o inglese, separati da virgola)", "S&P 500, FTSE MIB, Oro"
).title().split(",")

lista_tickers = []
nomi_usati = []

for nome in lista_nomi_input:
    nome = nome.strip()
    if nome:
        ticker, nome_trovato = trova_ticker(nome, nome_to_ticker)
        if ticker:
            lista_tickers.append(ticker)
            nomi_usati.append(nome_trovato)
        else:
            st.sidebar.warning(f"Nome '{nome}' non trovato nel dizionario.")

if not lista_tickers:
    st.stop()

# ==========================
# Pesi personalizzati
# ==========================
st.sidebar.subheader("Pesi (%) per strumento")
pesi = []
for n in nomi_usati:
    peso = st.sidebar.number_input(f"{n}", min_value=0.0, max_value=100.0, value=100.0/len(nomi_usati))
    pesi.append(peso/100)

pesi_arr = np.array(pesi)
if np.sum(pesi_arr) != 1:
    pesi_arr /= np.sum(pesi_arr)

periodo = st.sidebar.selectbox("Periodo storico", ["1y","3y","5y","10y","max"])

# ==========================
# Analisi portafoglio
# ==========================
if st.sidebar.button("Analizza Portafoglio"):

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

    nome_to_ticker_usati = dict(zip(nomi_usati, lista_tickers))

    # Prezzi normalizzati
    df_norm = df / df.iloc[0] * 100
    st.subheader("Prezzi Normalizzati")
    fig, ax = plt.subplots(figsize=(12,6))
    for nome in nomi_usati:
        ticker = nome_to_ticker_usati[nome]
        ax.plot(df_norm.index, df_norm[ticker], label=nome, linewidth=2)
    ax.set_xlabel("Data", fontsize=12)
    ax.set_ylabel("Prezzo Normalizzato", fontsize=12)
    ax.set_title("Evoluzione Prezzi Normalizzati", fontsize=16)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=12)
    st.pyplot(fig)

    # Statistiche
    rendimenti_giornalieri = df.pct_change().dropna()
    rendimenti_annuali = rendimenti_giornalieri.mean() * 252
    vol_annuale = rendimenti_giornalieri.std() * np.sqrt(252)
    rendimento_cumulato = (df.iloc[-1] / df.iloc[0]) - 1

    df_statistiche = pd.DataFrame({
        "Rendimento Cumulato": rendimento_cumulato.values,
        "Rendimento Annualizzato": rendimenti_annuali.values,
        "Volatilità Annualizzata": vol_annuale.values
    }, index=nomi_usati).sort_values("Rendimento Annualizzato", ascending=False)

    # Colonne layout
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statistiche Finanziarie")
        st.dataframe(df_statistiche.style.format({
            "Rendimento Cumulato": "{:.2%}",
            "Rendimento Annualizzato": "{:.2%}",
            "Volatilità Annualizzata": "{:.2%}"
        }))
    with col2:
        st.subheader("Matrice di Correlazione")
        correlazioni = rendimenti_giornalieri.corr()
        st.dataframe(correlazioni.style.background_gradient(cmap="coolwarm"))

    # Portafoglio selezionato
    mu = rendimenti_annuali
    sigma = rendimenti_giornalieri.cov() * 252
    rend_port = np.dot(mu, pesi_arr)
    vol_port = np.sqrt(np.dot(pesi_arr.T, np.dot(sigma, pesi_arr)))

    st.subheader("Portafoglio Selezionato")
    for i, nome in enumerate(nomi_usati):
        st.write(f"{nome}: {pesi_arr[i]*100:.2f}%")
    st.write(f"Rendimento atteso: **{rend_port:.2%}**")
    st.write(f"Volatilità: **{vol_port:.2%}**")

    # Frontiera efficiente
    num_portfolios = 50
    results = []
    for i in range(num_portfolios):
        w = np.random.random(len(lista_tickers))
        w /= np.sum(w)
        port_rend = np.dot(mu, w)
        port_vol = np.sqrt(np.dot(w.T, np.dot(sigma, w)))
        sharpe = port_rend / port_vol
        results.append([port_vol, port_rend, sharpe, w])
    results = np.array(results)
    max_idx = np.argmax(results[:,2])

    fig, ax = plt.subplots(figsize=(12,6))
    sc = ax.scatter(results[:,0], results[:,1], c=results[:,2], cmap="viridis", s=60, alpha=0.7)
    ax.scatter(vol_port, rend_port, color="red", marker="X", s=200, label="Portafoglio Selezionato")
    ax.scatter(results[max_idx,0], results[max_idx,1], color="gold", marker="*", s=300, label="Massimo Sharpe")
    ax.set_xlabel("Volatilità", fontsize=12)
    ax.set_ylabel("Rendimento", fontsize=12)
    ax.set_title("Frontiera Efficiente - 50 Portafogli", fontsize=16)
    ax.legend()
    fig.colorbar(sc, label="Sharpe Ratio")
    st.pyplot(fig)

    # Storico P/E
    st.subheader("Storico P/E Ratio")
    df_pe = pd.DataFrame()
    for nome in nomi_usati:
        ticker = nome_to_ticker_usati[nome]
        try:
            ticker_obj = yf.Ticker(ticker)
            earnings = ticker_obj.quarterly_earnings
            if not earnings.empty:
                earnings = earnings.reindex(df.index, method='ffill')
                pe_series = df[ticker] / earnings['Earnings']
                df_pe[nome] = pe_series
        except:
            st.warning(f"P/E storico non disponibile per {nome}")

    if not df_pe.empty:
        st.line_chart(df_pe)
    else:
        st.write("Nessun P/E storico disponibile per gli strumenti selezionati.")
