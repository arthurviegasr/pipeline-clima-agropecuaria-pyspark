import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    wb_indicator: str
    start_date: str
    end_date: str
    rate_limit_seconds: float
    max_retries: int
    output_dir: str
    quality_report_path: str

# Info. dos países relacionados para consulta na API
TOP_30_PAISES: list[dict[str, object]] = [
    {"iso2": "US", "iso3": "USA", "pais_ref": "Estados Unidos", "lat": 38.9072, "lon": -77.0369},
    {"iso2": "CN", "iso3": "CHN", "pais_ref": "China", "lat": 39.9042, "lon": 116.4074},
    {"iso2": "DE", "iso3": "DEU", "pais_ref": "Alemanha", "lat": 52.5200, "lon": 13.4050},
    {"iso2": "JP", "iso3": "JPN", "pais_ref": "Japão", "lat": 35.6762, "lon": 139.6503},
    {"iso2": "IN", "iso3": "IND", "pais_ref": "Índia", "lat": 28.6139, "lon": 77.2090},
    {"iso2": "GB", "iso3": "GBR", "pais_ref": "Reino Unido", "lat": 51.5072, "lon": -0.1276},
    {"iso2": "FR", "iso3": "FRA", "pais_ref": "França", "lat": 48.8566, "lon": 2.3522},
    {"iso2": "IT", "iso3": "ITA", "pais_ref": "Itália", "lat": 41.9028, "lon": 12.4964},
    {"iso2": "BR", "iso3": "BRA", "pais_ref": "Brasil", "lat": -15.7939, "lon": -47.8828},
    {"iso2": "CA", "iso3": "CAN", "pais_ref": "Canadá", "lat": 45.4215, "lon": -75.6972},
    {"iso2": "KR", "iso3": "KOR", "pais_ref": "Coreia do Sul", "lat": 37.5665, "lon": 126.9780},
    {"iso2": "AU", "iso3": "AUS", "pais_ref": "Austrália", "lat": -35.2809, "lon": 149.1300},
    {"iso2": "ES", "iso3": "ESP", "pais_ref": "Espanha", "lat": 40.4168, "lon": -3.7038},
    {"iso2": "MX", "iso3": "MEX", "pais_ref": "México", "lat": 19.4326, "lon": -99.1332},
    {"iso2": "ID", "iso3": "IDN", "pais_ref": "Indonésia", "lat": -6.2088, "lon": 106.8456},
    {"iso2": "NL", "iso3": "NLD", "pais_ref": "Países Baixos", "lat": 52.3676, "lon": 4.9041},
    {"iso2": "SA", "iso3": "SAU", "pais_ref": "Arábia Saudita", "lat": 24.7136, "lon": 46.6753},
    {"iso2": "TR", "iso3": "TUR", "pais_ref": "Turquia", "lat": 39.9334, "lon": 32.8597},
    {"iso2": "CH", "iso3": "CHE", "pais_ref": "Suíça", "lat": 46.9480, "lon": 7.4474},
    {"iso2": "PL", "iso3": "POL", "pais_ref": "Polônia", "lat": 52.2297, "lon": 21.0122},
    {"iso2": "SE", "iso3": "SWE", "pais_ref": "Suécia", "lat": 59.3293, "lon": 18.0686},
    {"iso2": "NO", "iso3": "NOR", "pais_ref": "Noruega", "lat": 59.9139, "lon": 10.7522},
    {"iso2": "DK", "iso3": "DNK", "pais_ref": "Dinamarca", "lat": 55.6761, "lon": 12.5683},
    {"iso2": "FI", "iso3": "FIN", "pais_ref": "Finlândia", "lat": 60.1699, "lon": 24.9384},
    {"iso2": "IE", "iso3": "IRL", "pais_ref": "Irlanda", "lat": 53.3498, "lon": -6.2603},
    {"iso2": "BE", "iso3": "BEL", "pais_ref": "Bélgica", "lat": 50.8503, "lon": 4.3517},
    {"iso2": "AT", "iso3": "AUT", "pais_ref": "Áustria", "lat": 48.2082, "lon": 16.3738},
    {"iso2": "NZ", "iso3": "NZL", "pais_ref": "Nova Zelândia", "lat": -41.2865, "lon": 174.7762},
    {"iso2": "SG", "iso3": "SGP", "pais_ref": "Singapura", "lat": 1.3521, "lon": 103.8198},
    {"iso2": "PT", "iso3": "PRT", "pais_ref": "Portugal", "lat": 38.7223, "lon": -9.1393},
]

def get_config() -> Config:
    return Config(
        wb_indicator=os.getenv("WB_INDICATOR", "NV.AGR.TOTL.ZS"),
        start_date=os.getenv("START_DATE", "2023-01-01"),
        end_date=os.getenv("END_DATE", "2025-12-31"),
        rate_limit_seconds=float(os.getenv("RATE_LIMIT_SECONDS", "0.4")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        output_dir=os.getenv("OUTPUT_DIR", "output/pib_clima_parquet"),
        quality_report_path=os.getenv("QUALITY_REPORT_PATH", "output/data_quality_report.json"),
    )