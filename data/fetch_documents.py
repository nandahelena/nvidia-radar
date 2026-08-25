"""
Baixa os documentos de cada startup a partir do config JSON,
extrai o texto principal e salva um JSON por startup em data/startups/.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time


def fetch_text(url, timeout=15):
    """
    Baixa uma URL e extrai só o texto principal, sem ruído de HTML.
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


def process_startup(startup_config, output_dir):
    """Baixa os documentos de uma startup e salva o JSON final."""
    nome = startup_config['nome']
    print(f"\n=== {nome} ===")
    
    documentos = []
    for doc_config in startup_config['documentos_urls']:
        url = doc_config['url']
        print(f"  → {url}")
        
        texto = fetch_text(url)
        tamanho = len(texto)
        
        if texto.startswith("[ERRO"):
            print(f"    ✗ Falhou: {texto[:80]}")
        else:
            print(f"    ✓ OK — {tamanho} caracteres")
        
        documentos.append({
            "tipo": doc_config['tipo'],
            "titulo": doc_config['titulo'],
            "conteudo_texto": texto,
            "url_fonte": url,
            "data_publicacao": doc_config.get('data_publicacao')
        })
        
        time.sleep(2)  # gentileza com os servidores
    
    # Monta o JSON final (metadata da startup + documentos)
    resultado = {k: v for k, v in startup_config.items() if k != 'documentos_urls'}
    resultado['documentos'] = documentos
    
    # Salva
    nome_arquivo = nome.lower().replace(' ', '_') + '.json'
    caminho = os.path.join(output_dir, nome_arquivo)
    
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print(f"  → Salvo em {caminho}")


def main():
    config_path = 'data/startups_config.json'
    output_dir = 'data/startups'
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(config_path, encoding='utf-8') as f:
        startups = json.load(f)
    
    print(f"Processando {len(startups)} startups...")
    
    for startup in startups:
        process_startup(startup, output_dir)
    
    print(f"\n=== Concluído: {len(startups)} JSONs em {output_dir}/ ===")


if __name__ == "__main__":
    main()