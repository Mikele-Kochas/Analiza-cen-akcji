import altair as alt
import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# Funkcja do pobierania danych z Yahoo Finance
def fetch_stock_data(ticker, start_date, end_date):
    try:
        # Pobieranie danych o akcjach dla podanego tickera w wybranym zakresie dat
        data = yf.download(ticker, start=start_date, end=end_date)
        
        # Upewnij się, że indeks danych jest typu DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        
        # Resetowanie indeksu, aby 'Date' stała się kolumną
        data.reset_index(inplace=True)
        data['Date'] = pd.to_datetime(data['Date'])
        
        return data
    except Exception as e:
        st.error(f"Nie udało się pobrać danych dla {ticker}: {e}")
        return pd.DataFrame()

# Ustawienia aplikacji
st.title("Analiza cen akcji")
today = datetime.now()
start_date_default = today - timedelta(days=30)
end_date_default = today

# Wybór zakresu dat z predefiniowanych opcji
st.subheader("Predefiniowane zakresy dat")
range_selection = st.selectbox(
    "Wybierz zakres",
    ["Ostatni tydzień", "Ostatni miesiąc", "Ostatnie 3 miesiące", "Ostatnie 6 miesięcy", "Ostatni rok", "Ostatnie 2 lata"]
)

# Ustawienie dat na podstawie wybranego zakresu
if range_selection == "Ostatni tydzień":
    start_date = today - timedelta(days=7)
    end_date = today
elif range_selection == "Ostatni miesiąc":
    start_date = today - timedelta(days=30)
    end_date = today
elif range_selection == "Ostatnie 3 miesiące":
    start_date = today - timedelta(days=90)
    end_date = today
elif range_selection == "Ostatnie 6 miesięcy":
    start_date = today - timedelta(days=180)
    end_date = today
elif range_selection == "Ostatni rok":
    start_date = today - timedelta(days=365)
    end_date = today
elif range_selection == "Ostatnie 2 lata":
    start_date = today - timedelta(days=730)
    end_date = today

# Wybór widoku wykresów
view_option = st.radio(
    "Wybierz widok",
    ["Widok szczegółowy", "Widok porównawczy"]
)

# Mapowanie tickerów na pełne nazwy firm
tickers_full_names = {
    "GOOGL": "Alphabet Inc. (Google)",
    "AMZN": "Amazon.com Inc.",
    "META": "Meta Platforms Inc. (Facebook)",
    "AAPL": "Apple Inc.",
    "NVDA": "NVIDIA Corporation",
    "MSFT": "Microsoft Corporation"
}

# Mapowanie tickerów na kolory dla wykresów
color_map = {
    "GOOGL": "#DB4437",   # Czerwony
    "AMZN": "#FF9900",    # Pomarańczowy
    "META": "#1E90FF",    # Jasny, jaskrawy niebieski
    "AAPL": "#A2AAAD",    # Szary
    "NVDA": "#76B900",    # Zielony NVIDIA
    "MSFT": "#4CAF50"     # Zielony Microsoft
}

# Lista tickerów
tickers = list(tickers_full_names.keys())

# Wybór firm do analizy
selected_tickers = st.multiselect(
    "Wybierz firmy do analizy",
    tickers,
    default=tickers,
    format_func=lambda x: tickers_full_names[x]  # Formatowanie wyboru na pełne nazwy firm
)

# Funkcja do tworzenia wykresu Altair dla widoku szczegółowego
def create_altair_plot(data, title, color):
    chart = alt.Chart(data).mark_line(size=4, color=color).encode(
        x=alt.X('Date:T', title='Data', axis=alt.Axis(format='%d-%m-%Y')),
        y=alt.Y('Close:Q', title='Cena zamknięcia'),
        tooltip=[alt.Tooltip('Date:T', title='Data', format='%d-%m-%Y'), alt.Tooltip('Close:Q', title='Cena zamknięcia')]
    ).properties(
        title=title
    )
    return chart

# Generowanie wykresów
if view_option == "Widok porównawczy":
    if selected_tickers:
        st.subheader("Porównanie cen akcji")
        all_data = pd.DataFrame()
        
        # Pobieranie danych dla wszystkich wybranych tickerów
        for ticker in selected_tickers:
            data = fetch_stock_data(ticker, start_date, end_date)
            data['Ticker'] = ticker
            all_data = pd.concat([all_data, data], axis=0)

        # Tworzenie wykresu porównawczego
        chart = alt.Chart(all_data).mark_line(size=3).encode(
            x=alt.X('Date:T', title='Data', axis=alt.Axis(format='%d-%m-%Y')),
            y=alt.Y('Close:Q', title='Cena zamknięcia'),
            color=alt.Color('Ticker:N', scale=alt.Scale(domain=selected_tickers, range=[color_map[ticker] for ticker in selected_tickers]), title='Firma'),
            tooltip=[alt.Tooltip('Date:T', title='Data', format='%d-%m-%Y'), alt.Tooltip('Close:Q', title='Cena zamknięcia'), alt.Tooltip('Ticker:N', title='Firma')]
        ).properties(
            title='Porównanie cen zamknięcia akcji'
        )
        st.altair_chart(chart, use_container_width=True)

else:
    if selected_tickers:
        for ticker in selected_tickers:
            st.subheader(f"Ceny akcji dla {tickers_full_names[ticker]}")
            data = fetch_stock_data(ticker, start_date, end_date)
            color = color_map[ticker]
            
            # Tworzenie wykresu szczegółowego dla każdej firmy
            chart = create_altair_plot(data, f'Zamknięcie akcji {tickers_full_names[ticker]}', color)
            st.altair_chart(chart, use_container_width=True)
