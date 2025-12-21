#!/usr/bin/env python3
"""
Script de teste para a API FastAPI do Stock Predictor
Execute este script para testar a API sem interface web
"""

import requests
import json
import time
from datetime import datetime, timedelta

# URL da API
API_URL = "http://localhost:8000"

# Colors para output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.ENDC}")

def print_result(text):
    print(f"{Colors.BLUE}{text}{Colors.ENDC}")

def test_health():
    """Teste o endpoint /health"""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success("Health check OK")
            print_result(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Conexão recusada: {e}")
        return False

def test_info():
    """Teste o endpoint /info"""
    print_header("TEST 2: Model Info")
    
    try:
        response = requests.get(f"{API_URL}/api/info")
        if response.status_code == 200:
            data = response.json()
            print_success("Model info obtido")
            print_result(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

def test_prediction(ticker="ABEV3"):
    """Teste o endpoint /api/predict"""
    print_header(f"TEST 3: Prediction ({ticker})")
    
    # Calcular datas
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    payload = {
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date
    }
    
    print_info(f"Ticker: {ticker}")
    print_info(f"Período: {start_date} a {end_date}")
    print()
    
    try:
        print("⏳ Aguardando resposta...")
        start_time = time.time()
        response = requests.post(f"{API_URL}/api/predict", json=payload)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Previsão obtida em {elapsed:.2f}s")
            print()
            
            # Mostrar resultados principais
            print_result(f"{'='*60}")
            print_result(f"📊 RESULTADOS DA PREVISÃO")
            print_result(f"{'='*60}")
            print_result(f"Ação: {Colors.BOLD}{data['ticker']}{Colors.ENDC}")
            print_result(f"Preço Atual: {Colors.BOLD}R$ {data['last_close']:.2f}{Colors.ENDC}")
            print_result(f"Próximo Preço: {Colors.BOLD}R$ {data['next_price']:.2f}{Colors.ENDC}")
            
            change = data['price_change']
            change_pct = data['price_change_pct']
            change_color = Colors.GREEN if change >= 0 else Colors.RED
            direction = "📈" if change >= 0 else "📉"
            print_result(f"Variação: {change_color}{direction} R$ {change:.2f} ({change_pct:.2f}%){Colors.ENDC}")
            print()
            
            print_result(f"{'='*60}")
            print_result(f"📈 MÉTRICAS DE QUALIDADE")
            print_result(f"{'='*60}")
            metrics = data['metrics']
            print_result(f"R² Score: {Colors.BOLD}{metrics['R2']:.4f}{Colors.ENDC}")
            print_result(f"MAE (Erro Médio): R$ {Colors.BOLD}{metrics['MAE']:.4f}{Colors.ENDC}")
            print_result(f"RMSE: {Colors.BOLD}{metrics['RMSE']:.4f}{Colors.ENDC}")
            print_result(f"MAPE: {Colors.BOLD}{metrics['MAPE']:.2f}%{Colors.ENDC}")
            print_result(f"MSE: {Colors.BOLD}{metrics['MSE']:.6f}{Colors.ENDC}")
            print()
            
            print_result(f"{'='*60}")
            print_result(f"📊 DADOS")
            print_result(f"{'='*60}")
            print_result(f"Pontos de dados: {Colors.BOLD}{data['data_points']}{Colors.ENDC}")
            print_result(f"Gráfico: {Colors.BOLD}{len(data['plot'])} caracteres (base64){Colors.ENDC}")
            
            return True
        else:
            print_error(f"Status code: {response.status_code}")
            try:
                error_data = response.json()
                print_error(f"Mensagem: {error_data.get('detail', 'Erro desconhecido')}")
            except:
                print_error(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

def test_multiple_tickers():
    """Teste com múltiplos tickers"""
    print_header("TEST 4: Multiple Tickers")
    
    tickers = ["ABEV3", "VALE3", "PETR4"]
    results = {}
    
    for ticker in tickers:
        print_info(f"Testando {ticker}...")
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        
        payload = {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date
        }
        
        try:
            response = requests.post(f"{API_URL}/api/predict", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                results[ticker] = {
                    "status": "✅",
                    "next_price": data['next_price'],
                    "r2": data['metrics']['R2']
                }
                print_success(f"{ticker} - Preço: R$ {data['next_price']:.2f}, R²: {data['metrics']['R2']:.4f}")
            else:
                results[ticker] = {"status": "❌", "error": f"Status {response.status_code}"}
                print_error(f"{ticker} - Erro {response.status_code}")
        except Exception as e:
            results[ticker] = {"status": "❌", "error": str(e)}
            print_error(f"{ticker} - Exceção: {e}")
        
        time.sleep(1)  # Aguardar entre requisições
    
    print()
    print_result(json.dumps(results, indent=2, ensure_ascii=False))

def main():
    """Execute todos os testes"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         Stock Price Predictor - API Test Suite            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    print_info(f"URL da API: {API_URL}")
    print_info("Aguardando API disponível...")
    print()
    
    # Aguardar API ficar online
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/health")
            if response.status_code == 200:
                print_success("API está online!")
                break
        except:
            if i < max_retries - 1:
                print_info(f"Tentativa {i+1}/{max_retries}... aguardando 2s")
                time.sleep(2)
            else:
                print_error("API não está respondendo. Certifique-se que está rodando.")
                print_info("Execute: cd api && uvicorn app:app --reload")
                return
    
    # Executar testes
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Model Info", test_info()))
    results.append(("Prediction", test_prediction("ABEV3")))
    results.append(("Multiple Tickers", test_multiple_tickers()))
    
    # Resumo
    print_header("RESUMO DOS TESTES")
    
    for test_name, passed in results:
        status = Colors.GREEN + "PASSOU" + Colors.ENDC if passed else Colors.RED + "FALHOU" + Colors.ENDC
        print_result(f"{test_name}: {status}")
    
    print()
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    if passed == total:
        print_success(f"Todos os {total} testes passaram! 🎉")
    else:
        print_error(f"{passed}/{total} testes passaram")
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Testes cancelados pelo usuário{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Erro fatal: {e}{Colors.ENDC}\n")
