import requests
from bs4 import BeautifulSoup
import json
import os
import time


def fetch_text(url, timeout=15):
    """
    Baixa uma URL e extrai só o texto principal, sem HTML.
    Retorna string com o conteúdo, ou uma mensagem de erro se falhar.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove elementos que geralmente são ruído (menu, rodapé, scripts)
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe', 'noscript']):
            tag.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        lines = [line for line in text.split('\n') if line.strip()]
        result = '\n'.join(lines)
        
        return result
    except Exception as e:
        return f"[ERRO ao baixar: {type(e).__name__}: {e}]"


def main():
    with open('data/nvidia_config.json', encoding='utf-8') as f:
        produtos = json.load(f)
    
    os.makedirs('data/nvidia', exist_ok=True)
    
    for produto in produtos:
        nome = produto['produto']
        url = produto['url']
        print(f"→ {nome}: {url}")
        
        texto = fetch_text(url)
        tamanho = len(texto)
        
        if texto.startswith("[ERRO"):
            print(f"  ✗ Falhou: {texto[:80]}")
        else:
            print(f"  ✓ OK — {tamanho} caracteres")
        
        nome_arquivo = nome.lower().replace(' ', '_').replace('/', '_') + '.txt'
        caminho = os.path.join('data/nvidia', nome_arquivo)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(f"PRODUTO: {nome}\n")
            f.write(f"CATEGORIA: {produto['categoria']}\n")
            f.write(f"URL_FONTE: {url}\n")
            f.write("---\n")
            f.write(texto)
        
        time.sleep(2)
    
    print(f"\nConcluído: {len(produtos)} arquivos em data/nvidia/")


if __name__ == "__main__":
    main()