from playwright.sync_api import sync_playwright
import pandas as pd
import yfinance as yf  # Importando o yfinance
import time

# Esta função continua a mesma, ela é a base
def scrape_ibov() -> pd.DataFrame:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = browser.new_page()
        page.goto(
            "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"
        )
        page.select_option("#selectPage", "120")

        for _ in range(15):
            rows = page.query_selector_all("table tbody tr")
            if len(rows) == 120:
                break
            time.sleep(1)

        data = []

        for row in rows:
            cols = row.query_selector_all("td")
            if len(cols) == 5:
                codigo = cols[0].inner_text().strip()
                data.append(codigo)

        browser.close()
        df = pd.DataFrame(data, columns=["codigo"])

    return df


def obter_tickers_yfinance() -> list:
    df_tickers = scrape_ibov()
    
    # Verifica se a coluna 'codigo' existe e não está vazia
    if 'codigo' not in df_tickers.columns or df_tickers.empty:
        print("Não foi possível encontrar a coluna 'codigo' ou o DataFrame está vazio.")
        return []

    tickers_b3 = df_tickers['codigo'].tolist()
    
    tickers_yf = [f"{ticker}.SA" for ticker in tickers_b3]
    
    return tickers_yf


# --- EXEMPLO DE USO ---
if __name__ == "__main__":
    
    lista_de_tickers = obter_tickers_yfinance()
    
    dados = yf.download(lista_de_tickers, period="10y")

    # print(dados.head())

    df_long = dados.stack(level=1)

    df_long = df_long.reset_index().rename(columns={'level_1': 'Ticker'}) 
    
    print(len(df_long))
    
    # antiga eletrobras ELET3 mudou para AXIA3
    # print(df_long[df_long['Ticker'] == 'AXIA6.SA'].head())
    # print(df_long[df_long['Ticker'] == 'AXIA3.SA'].head())


    
