import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def capturar_mapas_PE():
    print("-> A iniciar captura dos mapas PE (Fronteiras)...")
    pasta_raiz = os.getcwd()
    hoje = datetime.now()
    
    fmt_hoje = hoje.strftime("%Y-%m-%d")
    fmt_amanha = (hoje + timedelta(days=1)).strftime("%Y-%m-%d")
    fmt_depois = (hoje + timedelta(days=2)).strftime("%Y-%m-%d")
    
    url_base = "https://api.ipma.pt/public-data/mf2_preview/lsasaf_p2000_continent/lsasaf_p2000_continent_{}T00_00_00.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1200, 'height': 1200})
        page = context.new_page()
        
        page.goto("https://www.ipma.pt/pt/riscoincendio/fwi/")
        page.wait_for_selector(".leaflet-container", timeout=60000)
        page.wait_for_timeout(6000) 
        
        page.evaluate("""
            var els = document.querySelectorAll('header, footer, nav, [id*=cookie], .leaflet-control-container');
            els.forEach(el => { if(el) el.style.display = 'none'; });
        """)
        
        mapa = page.locator(".leaflet-container").first
        js_mudar_imagem = """(novaUrl) => {
            var imagens = document.querySelectorAll('img[src*="lsasaf_p2000"]');
            imagens.forEach(img => img.src = novaUrl);
        }"""
        
        # HOJE PE
        page.evaluate(js_mudar_imagem, url_base.format(fmt_hoje))
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_hoje_PE.png"))
        print(f"   Sucesso: portugal_hoje_PE.png")
        
        # AMANHA PE
        page.evaluate(js_mudar_imagem, url_base.format(fmt_amanha))
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_amanha_PE.png"))
        print(f"   Sucesso: portugal_amanha_PE.png")
        
        # DEPOIS PE
        page.evaluate(js_mudar_imagem, url_base.format(fmt_depois))
        page.wait_for_timeout(3000)
        mapa.screenshot(path=os.path.join(pasta_raiz, "portugal_depois_PE.png"))
        print(f"   Sucesso: portugal_depois_PE.png")
        
        browser.close()

def capturar_mapas_PIR():
    print("\n-> A transferir mapas PIR (Download Direto do Servidor IPMA)...")
    hoje = datetime.now()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for d in range(3):
            data_alvo = (hoje + timedelta(days=d)).strftime("%Y-%m-%d")
            nome_ficheiro = "portugal_hoje.png" if d == 0 else "portugal_amanha.png" if d == 1 else "portugal_depois.png"
            
            # O link mágico! Substituí o "time=" pela data certa e o "bbox=" pelas coordenadas de Portugal inteiro
            url_wms = (
                "https://cs2.ipma.pt/azstats/wms?"
                "map=rcm_2026-forecast_9p1d-continental-prevstat-idw&"
                "service=WMS&request=GetMap&"
                "layers=PT%3AIPMA%3ACDG%3ALAYER%3Arcm_2026-forecast_9p1d-continental-prevstat-idw%3APIR%3ACONCELHOS&"
                "styles=&format=image%2Fpng&transparent=true&version=1.1.1&"
                f"time={data_alvo}T00%3A00%3A00Z&"
                "width=800&height=1200&srs=EPSG%3A3857&"
                "bbox=-1252344.27,4383204.95,-626172.14,5322463.15"
            )
            
            print(f"   A transferir {nome_ficheiro} ({data_alvo})...")
            
            # Navega direto para a imagem
            response = page.goto(url_wms, timeout=120000, wait_until="commit")
            
            # Guarda o corpo do link (a imagem crua) num ficheiro
            if response and response.status == 200:
                with open(nome_ficheiro, "wb") as f:
                    f.write(response.body())
                print(f"   Sucesso: {nome_ficheiro} guardado!")
            else:
                print(f"   Falha ao obter {nome_ficheiro}. O IPMA pode não ter este dia disponível.")
                
        browser.close()

if __name__ == "__main__":
    capturar_mapas_PE()
    capturar_mapas_PIR()
