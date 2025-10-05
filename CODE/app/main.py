"""Main FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from datetime import datetime
import logging
import time

from app.config import get_settings
from app.routers import environmental

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    response.headers["X-Process-Time-Ms"] = str(int(process_time))
    return response


# Include routers
app.include_router(
    environmental.router,
    prefix="/api/v1",
    tags=["Environmental Data"]
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "docs": "/docs",
        "test": "/test",
        "health": "/health",
        "info": "/api/v1/info"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": settings.app_version
    }


@app.get("/test", response_class=HTMLResponse, tags=["Testing"])
async def test_page():
    """Interactive test page for the API."""
    html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NASA SafeOut API - Teste Interativo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .section {
            margin-bottom: 30px;
        }
        
        .section h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        
        input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        button {
            padding: 15px 25px;
            font-size: 1em;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            color: white;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        
        .btn-info {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .response-container {
            margin-top: 20px;
        }
        
        .response-box {
            background: #f8f9fa;
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            min-height: 200px;
            max-height: 500px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .loading {
            text-align: center;
            color: #667eea;
            font-size: 1.2em;
            padding: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .status-success {
            background: #d4edda;
            color: #155724;
        }
        
        .status-error {
            background: #f8d7da;
            color: #721c24;
        }
        
        .presets {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }
        
        .preset-btn {
            padding: 8px 15px;
            background: #e9ecef;
            border: 2px solid #dee2e6;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s;
        }
        
        .preset-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 NASA SafeOut API</h1>
            <p>Teste Interativo de Dados Ambientais</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📍 Coordenadas e Raio</h2>
                
                <div class="presets">
                    <strong style="display: block; margin-bottom: 10px; color: #667eea;">🇧🇷 Brasil:</strong>
                    <button class="preset-btn" onclick="setPreset(-27.5954, -48.5480, 'Florianópolis, SC')">📍 Florianópolis, SC</button>
                    <button class="preset-btn" onclick="setPreset(-23.5505, -46.6333, 'São Paulo, SP')">📍 São Paulo, SP</button>
                    <button class="preset-btn" onclick="setPreset(-22.9068, -43.1729, 'Rio de Janeiro, RJ')">📍 Rio de Janeiro, RJ</button>
                    <button class="preset-btn" onclick="setPreset(-15.7801, -47.9292, 'Brasília, DF')">📍 Brasília, DF</button>
                    
                    <strong style="display: block; margin: 15px 0 10px 0; color: #667eea;">🇺🇸 Estados Unidos:</strong>
                    <button class="preset-btn" onclick="setPreset(40.7128, -74.0060, 'New York, NY')">📍 New York, NY</button>
                    <button class="preset-btn" onclick="setPreset(34.0522, -118.2437, 'Los Angeles, CA')">📍 Los Angeles, CA</button>
                    <button class="preset-btn" onclick="setPreset(41.8781, -87.6298, 'Chicago, IL')">📍 Chicago, IL</button>
                    <button class="preset-btn" onclick="setPreset(29.7604, -95.3698, 'Houston, TX')">📍 Houston, TX</button>
                    <button class="preset-btn" onclick="setPreset(33.4484, -112.0740, 'Phoenix, AZ')">📍 Phoenix, AZ</button>
                    <button class="preset-btn" onclick="setPreset(37.7749, -122.4194, 'San Francisco, CA')">📍 San Francisco, CA</button>
                    <button class="preset-btn" onclick="setPreset(47.6062, -122.3321, 'Seattle, WA')">📍 Seattle, WA</button>
                    <button class="preset-btn" onclick="setPreset(25.7617, -80.1918, 'Miami, FL')">📍 Miami, FL</button>
                </div>
                
                <div class="form-group">
                    <label for="latitude">Latitude (-90 a 90):</label>
                    <input type="number" id="latitude" step="0.0001" min="-90" max="90" value="-27.5954">
                </div>
                
                <div class="form-group">
                    <label for="longitude">Longitude (-180 a 180):</label>
                    <input type="number" id="longitude" step="0.0001" min="-180" max="180" value="-48.5480">
                </div>
                
                <div class="form-group">
                    <label for="radius">Raio (metros, 100 a 50000):</label>
                    <input type="number" id="radius" step="100" min="100" max="50000" value="5000">
                </div>
            </div>
            
            <div class="section">
                <h2>🧪 Testes Disponíveis</h2>
                
                <div class="button-grid">
                    <button class="btn-primary" onclick="testFullAPI()">🌍 Teste Completo</button>
                    <button class="btn-success" onclick="testHealth()">❤️ Health Check</button>
                    <button class="btn-info" onclick="testInfo()">ℹ️ Info da API</button>
                    <button class="btn-warning" onclick="testInvalidCoords()">⚠️ Teste Erro (Coords Inválidas)</button>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Resposta da API</h2>
                <div class="response-container">
                    <div id="response" class="response-box">
Aguardando requisição...

Dica: Clique em um dos botões acima para testar a API!
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        
        function setPreset(lat, lon, name) {
            document.getElementById('latitude').value = lat;
            document.getElementById('longitude').value = lon;
            showResponse(`📍 Localização definida: ${name}\\n\\nLatitude: ${lat}\\nLongitude: ${lon}`, 'info');
        }
        
        function showLoading() {
            document.getElementById('response').innerHTML = 
                '<div class="loading"><div class="spinner"></div>Carregando...</div>';
        }
        
        function showResponse(data, type = 'success') {
            const responseDiv = document.getElementById('response');
            const badge = type === 'success' 
                ? '<span class="status-badge status-success">✓ Sucesso</span>' 
                : type === 'error'
                ? '<span class="status-badge status-error">✗ Erro</span>'
                : '';
            
            const formattedData = typeof data === 'object' 
                ? JSON.stringify(data, null, 2) 
                : data;
            
            responseDiv.innerHTML = badge + '\\n\\n' + formattedData;
        }
        
        async function makeRequest(url, options = {}) {
            showLoading();
            try {
                const response = await fetch(url, options);
                const data = await response.json();
                
                if (response.ok) {
                    showResponse(data, 'success');
                } else {
                    showResponse(data, 'error');
                }
            } catch (error) {
                showResponse(`Erro na requisição:\\n${error.message}`, 'error');
            }
        }
        
        function testHealth() {
            makeRequest(`${API_BASE}/health`);
        }
        
        function testInfo() {
            makeRequest(`${API_BASE}/api/v1/info`);
        }
        
        function testFullAPI() {
            const lat = parseFloat(document.getElementById('latitude').value);
            const lon = parseFloat(document.getElementById('longitude').value);
            const radius = parseInt(document.getElementById('radius').value);
            
            if (isNaN(lat) || isNaN(lon) || isNaN(radius)) {
                showResponse('Por favor, preencha todos os campos corretamente!', 'error');
                return;
            }
            
            if (lat < -90 || lat > 90) {
                showResponse('Latitude deve estar entre -90 e 90!', 'error');
                return;
            }
            
            if (lon < -180 || lon > 180) {
                showResponse('Longitude deve estar entre -180 e 180!', 'error');
                return;
            }
            
            if (radius < 100 || radius > 50000) {
                showResponse('Raio deve estar entre 100 e 50000 metros!', 'error');
                return;
            }
            
            const payload = {
                latitude: lat,
                longitude: lon,
                radius_meters: radius
            };
            
            makeRequest(`${API_BASE}/api/v1/environmental-data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
        }
        
        function testInvalidCoords() {
            const payload = {
                latitude: 100,  // Inválido
                longitude: -48.5480,
                radius_meters: 5000
            };
            
            makeRequest(`${API_BASE}/api/v1/environmental-data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
        }
        
        // Permitir Enter para submeter
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                testFullAPI();
            }
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
