O projeto é um serviço de backend em python para uma aplicação que consome dados oriundos de diversas fontes, principalmente dados publicados pela NASA na plataforma Earthdata;

O projeto deve receber uma chamada de API informando latitude e longitude e perímetro em metros;
O projeto deve utilizar a biblioteca earthaccess disponível em https://earthaccess.readthedocs.io/
O projeto deve responder com dados em formato JSON com as informações obtidas das fontes abaixo:

1. Precipitação (Chuva) 💧
		Previsão para as Próximas Horas (IMERG)
		Fonte: Integrated Multi-satellite Retrievals for GPM (IMERG).
		Nome Técnico (Short Name): GPM_3IMERGHHE
		Link para Exploração: https://gpm.nasa.gov/data/imerg
		Acesso Programático (Recomendado): Use a biblioteca earthaccess em Python para buscar pelo short_name e baixar os dados mais recentes para sua área de interesse.


2. Qualidade do Ar 🌬
	A. Visão do Satélite (TEMPO)
	O que é: A missão mais nova da NASA, focada em poluição na América do Norte (mas o desafio lista como um recurso chave). Para o Brasil, uma ótima alternativa é o TROPOMI no Sentinel-5P.
	Fonte: TROPOMI Aerosol Index (AI) ou Nitrogen Dioxide (NO2).
	Nome Técnico (Short Name): S5P_L2_AER_AI (para Aerosol Index) ou S5P_NRTI_L2_NO2 (para NRT NO2).
	Link para Exploração: https://sentinel.esa.int/web/sentinel/missions/sentinel-5p

	B. Validação em Solo (OpenAQ)
	O que é: Uma plataforma que agrega dados de estações de monitoramento de qualidade do ar do mundo todo, incluindo várias no Brasil.
	Link da API (Recomendado): https://docs.openaq.org/	
	Acesso Programático: Use a API REST deles. É muito simples fazer uma chamada para pegar os dados mais recentes de PM2.5 para uma cidade específica como Florianópolis. Existe também uma biblioteca Python py-openaq.

3. Vento, Temperatura e Umidade 🌡
	O que é: MERRA-2. Um modelo de reanálise da NASA que fornece um "mapa" global e consistente de variáveis do tempo.
	Fonte: M2I1NXASM (Instantaneous, Single-Level, Assimilation).
	Nome Técnico (Short Name): M2I1NXASM
	Link para Exploração: https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/
	Acesso Programático (Recomendado): earthaccess. As variáveis que você vai querer de dentro dos arquivos são U2M e V2M (componentes do vento a 2m), T2M (temperatura a 2m) e QV2M (umidade a 2m).

4. Índice UV e "História Ambiental" 🔥
	A. Índice UV
	O que é: O mesmo satélite TROPOMI que mede a qualidade do ar também pode ser usado para estimar o índice UV.
	Fonte: TROPOMI UV Aerosol Index.
	Nome Técnico (Short Name): S5P_L2__AER_AI (o mesmo do Aerosol Index, o arquivo contém múltiplas variáveis).
	Acesso Programático: earthaccess.

	B. Focos de Incêndio (para a "História Ambiental")
	O que é: VIIRS Active Fires. Detecta focos de calor na superfície, indicando possíveis queimadas.
	Fonte: VIIRS/Suomi NPP Thermal Anomalies/Active Fire.
	Link da API (Recomendado): NASA FIRMS (Fire Information for Resource Management System) API. É a forma mais fácil e direta.
	Link: https://firms.modaps.eosdis.nasa.gov/web-services/

Para dados em grade (grade-based data) como IMERG, TROPOMI, MERRA-2: Sua ferramenta principal será a biblioteca earthaccess em Python.
Para dados de pontos (point-based data) como estações em solo e focos de incêndio: Use as APIs específicas (OpenAQ e FIRMS), que são mais diretas.

Comece instalando o earthaccess, autentique com seu Earthdata Login e tente baixar um arquivo de cada uma dessas fontes. Ter o fluxo de dados funcionando é o passo mais importante.Ferramenta Essencial nº 1: Sua Conta na NASA
Ferramenta Essencial nº 2: A Biblioteca Python para Acessar Tudo
Link: https://earthaccess.readthedocs.io/
