"""
Teste rápido para verificar se o .env está correto após remover username/password.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("Verificação do arquivo .env")
print("=" * 60)

# Check what's in the environment
token = os.getenv("EARTHDATA_TOKEN")
username = os.getenv("EARTHDATA_USERNAME")
password = os.getenv("EARTHDATA_PASSWORD")
firms_key = os.getenv("FIRMS_API_KEY")

print("\nVariáveis encontradas:")
print(f"  EARTHDATA_TOKEN: {'✅ Set' if token else '❌ Not set'}")
print(f"  EARTHDATA_USERNAME: {'❌ DEVE SER REMOVIDO' if username else '✅ Removido'}")
print(f"  EARTHDATA_PASSWORD: {'❌ DEVE SER REMOVIDO' if password else '✅ Removido'}")
print(f"  FIRMS_API_KEY: {'✅ Set' if firms_key else '❌ Not set'}")

if username or password:
    print("\n⚠️ ATENÇÃO: Ainda existem EARTHDATA_USERNAME ou EARTHDATA_PASSWORD no .env")
    print("   Estas variáveis devem ser removidas!")
    print("\n   Execute no PowerShell:")
    print('   Get-Content .env | Where-Object { $_ -notmatch "EARTHDATA_USERNAME" -and $_ -notmatch "EARTHDATA_PASSWORD" } | Set-Content .env.new')
    print('   Move-Item -Force .env.new .env')
else:
    print("\n✅ SUCESSO: Arquivo .env está correto!")
    print("   Apenas EARTHDATA_TOKEN está configurado.")
    print("\n   Agora você pode iniciar a API:")
    print("   uvicorn app.main:app --reload")
