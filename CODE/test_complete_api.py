"""
Script de teste completo para validar todas as fontes de dados da API.
Testa cada fonte individualmente e depois faz um teste completo.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import pytest

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.data_processor import DataProcessor
from app.services.earthdata import EarthdataService


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(name: str, success: bool, data=None):
    """Print test result."""
    status = "✅ SUCESSO" if success else "❌ FALHOU"
    print(f"\n{status} - {name}")
    if data and success:
        print(f"  Dados retornados: {type(data).__name__}")
        if hasattr(data, 'dict'):
            print(f"  Preview: {str(data.dict())[:200]}...")


@pytest.mark.asyncio
async def test_earthdata_authentication():
    """Test NASA Earthdata authentication."""
    print_section("1. Testando Autenticação NASA Earthdata")
    
    try:
        service = EarthdataService()
        if service.authenticated:
            print("✅ Autenticação bem-sucedida!")
            print(f"   Username configurado: Sim")
            return True
        else:
            print("❌ Falha na autenticação")
            print("   Verifique as credenciais no arquivo .env")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


@pytest.mark.asyncio
async def test_precipitation():
    """Test precipitation data (IMERG)."""
    print_section("2. Testando Precipitação (GPM IMERG)")
    
    try:
        processor = DataProcessor()
        # Florianópolis coordinates
        data = await processor.get_precipitation_data(-27.5954, -48.5480, 5000)
        
        if data:
            print_result("GPM IMERG", True, data)
            print(f"   Taxa de precipitação: {data.precipitation_rate_mm_hr} mm/h")
            print(f"   Fonte: {data.source}")
            return True
        else:
            print_result("GPM IMERG", False)
            print("   Nota: Pode não haver dados disponíveis para esta região/período")
            return False
    except Exception as e:
        print(f"❌ Erro ao buscar dados IMERG: {e}")
        return False


@pytest.mark.asyncio
async def test_weather():
    """Test weather data (MERRA-2)."""
    print_section("3. Testando Dados Climáticos (MERRA-2)")
    
    try:
        processor = DataProcessor()
        data = await processor.get_weather_data(-27.5954, -48.5480, 5000)
        
        if data:
            print_result("MERRA-2", True, data)
            print(f"   Temperatura: {data.temperature_celsius}°C")
            if data.wind:
                print(f"   Vento: {data.wind.speed_kmh} km/h ({data.wind.direction_cardinal})")
            print(f"   Umidade: {data.humidity_percent}%")
            return True
        else:
            print_result("MERRA-2", False)
            print("   Nota: Pode não haver dados disponíveis para esta região/período")
            return False
    except Exception as e:
        print(f"❌ Erro ao buscar dados MERRA-2: {e}")
        return False


@pytest.mark.asyncio
async def test_air_quality():
    """Test air quality data (TROPOMI + OpenAQ)."""
    print_section("4. Testando Qualidade do Ar (TROPOMI + OpenAQ)")
    
    try:
        processor = DataProcessor()
        data = await processor.get_air_quality_data(-27.5954, -48.5480, 50000)
        
        if data:
            print_result("Qualidade do Ar", True, data)
            
            # Satellite data
            if data.satellite:
                print(f"\n   Satélite (TROPOMI):")
                print(f"     Aerosol Index: {data.satellite.aerosol_index}")
                print(f"     NO2: {data.satellite.no2_mol_m2} mol/m²")
                print(f"     Qualidade: {data.satellite.quality_flag}")
            
            # Ground stations
            if data.ground_stations:
                print(f"\n   Estações Terrestres (OpenAQ):")
                print(f"     Estações encontradas: {data.ground_stations.stations_count}")
                if data.ground_stations.average:
                    avg = data.ground_stations.average
                    print(f"     PM2.5 médio: {avg.get('pm25', 'N/A')} µg/m³")
            
            return True
        else:
            print_result("Qualidade do Ar", False)
            return False
    except Exception as e:
        print(f"❌ Erro ao buscar dados de qualidade do ar: {e}")
        return False


@pytest.mark.asyncio
async def test_uv_index():
    """Test UV index data."""
    print_section("5. Testando Índice UV")
    
    try:
        processor = DataProcessor()
        data = await processor.get_uv_index_data(-27.5954, -48.5480, 5000)
        
        if data:
            print_result("Índice UV", True, data)
            print(f"   UV Index: {data.uv_index}")
            print(f"   Categoria: {data.category}")
            print(f"   Risco: {data.risk_level}")
            return True
        else:
            print_result("Índice UV", False)
            print("   Nota: Depende de dados TROPOMI disponíveis")
            return False
    except Exception as e:
        print(f"❌ Erro ao calcular índice UV: {e}")
        return False


@pytest.mark.asyncio
async def test_fire_history():
    """Test fire history data (FIRMS)."""
    print_section("6. Testando Focos de Incêndio (NASA FIRMS)")
    
    try:
        processor = DataProcessor()
        data = await processor.get_fire_history_data(-27.5954, -48.5480, 50000)
        
        if data:
            print_result("NASA FIRMS", True, data)
            print(f"   Focos ativos: {data.active_fires_count}")
            print(f"   Período: últimos {data.period_days} dias")
            if data.fires:
                nearest = data.fires[0]
                print(f"   Foco mais próximo: {nearest.distance_km} km")
            return True
        else:
            print_result("NASA FIRMS", False)
            print("   Nota: Pode não haver focos na região")
            return False
    except Exception as e:
        print(f"❌ Erro ao buscar focos de incêndio: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "🚀" * 35)
    print("  TESTE COMPLETO DA API - NASA SafeOut")
    print("🚀" * 35)
    print(f"\nData/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Localização de teste: Florianópolis, SC (-27.5954, -48.5480)")
    
    results = {}
    
    # Test 1: Authentication
    results['auth'] = await test_earthdata_authentication()
    
    if not results['auth']:
        print("\n⚠️  AVISO: Autenticação falhou. Testes NASA serão pulados.")
        print("   Configure EARTHDATA_USERNAME e EARTHDATA_PASSWORD no .env")
        return
    
    # Test 2-6: Data sources
    results['precipitation'] = await test_precipitation()
    results['weather'] = await test_weather()
    results['air_quality'] = await test_air_quality()
    results['uv_index'] = await test_uv_index()
    results['fire_history'] = await test_fire_history()
    
    # Summary
    print_section("RESUMO DOS TESTES")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal de testes: {total}")
    print(f"Testes bem-sucedidos: {passed}")
    print(f"Testes falhados: {total - passed}")
    print(f"Taxa de sucesso: {(passed/total)*100:.1f}%")
    
    print("\nDetalhes:")
    for test_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! API totalmente funcional!")
    elif passed >= total * 0.7:
        print("\n✅ Maioria dos testes passou. API funcional com algumas limitações.")
    else:
        print("\n⚠️  Vários testes falharam. Verifique a configuração.")
    
    print("\n" + "=" * 70)
    print("\nPróximos passos:")
    print("1. Inicie a API: uvicorn app.main:app --reload")
    print("2. Acesse: http://localhost:8000/test")
    print("3. Teste os endpoints via interface web")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
