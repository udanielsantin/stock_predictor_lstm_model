from playwright.sync_api import sync_playwright
import pandas as pd
import yfinance as yf 
import time
from pathlib import Path
from playwright.async_api import async_playwright
import asyncio

async def scrape_ibov(csv_path: str = "/workspaces/stock_predictor_lstm_model/data/ibov_tickers.csv") -> pd.DataFrame:

    url = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = await browser.new_page()
        await page.goto(url)
        await page.select_option("#selectPage", "120")

        rows = []
        for _ in range(15):
            rows = await page.query_selector_all("table tbody tr")
            if len(rows) == 120:
                break
            await asyncio.sleep(1)

        data = []
        for row in rows:
            cols = await row.query_selector_all("td")
            if len(cols) == 5:
                codigo = (await cols[0].inner_text()).strip()
                data.append(codigo)

        await browser.close()
        df = pd.DataFrame(data, columns=["codigo"])

    # Normalize values to strings
    df["codigo"] = df["codigo"].astype(str)

    csv_file = Path(csv_path)
    if csv_file.exists():
        try:
            existing = pd.read_csv(csv_file, dtype=str)
            if "codigo" in existing.columns:
                existing_set = set(existing["codigo"].astype(str))
                new_set = set(df["codigo"])
                if existing_set == new_set and len(existing) == len(df):
                    print(f"No changes detected in {csv_path}. CSV not updated.")
                    return df
            # if column missing or sets differ, fall through to overwrite
        except Exception as e:
            print(f"Warning: could not read existing CSV ({e}). Will overwrite.")

    df.to_csv(csv_file, index=False)
    print(f"Saved {len(df)} tickers to {csv_path}.")

    return df


def obter_tickers_yfinance() -> list:
    csv_file = Path("/workspaces/stock_predictor_lstm_model/data/ibov_tickers.csv")

    # if not csv_file.exists():
    #     scrape_ibov()  # creates the CSV at the default path

    df = pd.read_csv(csv_file, dtype=str)

    if "codigo" not in df.columns or df.empty:
        return []

    tickers = df["codigo"].astype(str).str.strip().tolist()
    return [f"{t}.SA" for t in tickers if t]
''

# --- EXEMPLO DE USO ---
if __name__ == "__main__":
    
    lista_de_tickers = obter_tickers_yfinance()
    
    dados = yf.download(lista_de_tickers, period="10y")

    # print(dados.head())

    df_long = dados.stack(level=1)

    df_long = df_long.reset_index().rename(columns={'level_1': 'Ticker'}) 
    
    # print(len(df_long))
    
    # antiga eletrobras ELET3 mudou para AXIA3
    # print(df_long[df_long['Ticker'] == 'AXIA6.SA'].head())
    # print(df_long[df_long['Ticker'] == 'AXIA3.SA'].head())


    
