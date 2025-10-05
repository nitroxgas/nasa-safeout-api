"""
Script de diagnóstico para verificar a autenticação e o acesso aos dados da NASA Earthdata.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def run_diagnostics():
    """Run the diagnostic tests."""
    print_section("Diagnóstico de Acesso ao NASA Earthdata")

    # 1. Verificar token no ambiente
    print("\n[PASSO 1/4] Verificando credenciais...")
    settings = get_settings()
    token = settings.earthdata_token

    if token:
        print("  ✅ Encontrado: EARTHDATA_TOKEN")
        print(f"     Token: {token[:50]}..." if len(token) > 50 else f"     Token: {token}")
    else:
        print("  ❌ ERRO: Token não encontrado no arquivo .env")
        print("     Configure EARTHDATA_TOKEN no arquivo .env")
        print("\n  Para obter um token:")
        print("     1. Acesse: https://urs.earthdata.nasa.gov/profile")
        print("     2. Clique em 'Generate Token'")
        print("     3. Copie o token para o arquivo .env")
        return

    # 2. Tentar autenticar
    print("\n[PASSO 2/4] Tentando autenticar...")
    try:
        import earthaccess
        os.environ["EARTHDATA_TOKEN"] = token

        auth = earthaccess.login(strategy="environment")
        if auth.authenticated:
            print("  ✅ SUCESSO: Autenticação bem-sucedida com token!")
        else:
            print("  ❌ FALHA: A autenticação falhou. Verifique seu token.")
            print("\n  Para gerar um novo token:")
            print("     1. Acesse: https://urs.earthdata.nasa.gov/profile")
            print("     2. Clique em 'Generate Token'")
            print("     3. Atualize o .env com o novo token")
            return
    except Exception as e:
        print(f"  ❌ ERRO: Ocorreu uma exceção durante a autenticação: {e}")
        print("\n  Verifique se o token está correto e não expirou.")
        return

    # 3. Tentar buscar dados
    print("\n[PASSO 3/4] Tentando buscar um granule de teste (GPM_3IMERGHHE)...")
    try:
        results = earthaccess.search_data(
            short_name="GPM_3IMERGHHE",
            count=1
        )
        if results:
            print("  ✅ SUCESSO: A busca de dados retornou resultados!")
            print(f"     Encontrado(s) {len(results)} granule(s).")
            print("     Isso significa que suas credenciais e autorizações estão funcionando.")
        else:
            print("  ⚠️ ATENÇÃO: A busca de dados não retornou resultados.")
            print("     Isso pode ser normal (sem dados para o período) ou pode indicar um problema.")

    except Exception as e:
        print(f"  ❌ ERRO: A busca de dados falhou com a seguinte exceção: {e}")
        print_section("AÇÃO NECESSÁRIA: Autorizar Aplicações")
        print("  Este erro geralmente significa que você precisa autorizar as aplicações no seu perfil Earthdata.")
        print("  Siga os passos abaixo:")
        print("  1. Acesse: https://urs.earthdata.nasa.gov/profile")
        print("  2. Vá para a aba 'Applications' -> 'Authorized Apps'")
        print("  3. Procure e aprove a seguinte aplicação:")
        print("     - NASA GESDISC DATA ARCHIVE (para GPM IMERG e MERRA-2)")
        print("  4. Após aprovar, execute este script novamente.")
        print("\n  NOTA: TROPOMI/Sentinel-5P não está disponível via NASA Earthdata.")
        print("        Esses dados são da ESA e requerem acesso separado via Copernicus.")
        print("        A API funcionará sem TROPOMI, usando apenas dados terrestres para qualidade do ar.")
        return

    # 4. Conclusão
    print_section("RESULTADO DO DIAGNÓSTICO")
    print("  ✅ Acesso ao Earthdata parece estar configurado corretamente.")
    print("  Se a API ainda falhar, o problema pode ser:")
    print("    - A API está rodando em um ambiente onde as variáveis de ambiente não estão sendo carregadas.")
    print("    - Problemas de rede no ambiente da API (firewall, proxy, etc.).")
    print("    - Dados específicos não disponíveis para a localização/data solicitada.")

if __name__ == "__main__":
    run_diagnostics()
