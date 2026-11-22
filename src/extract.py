import time
from typing import Any
import requests
from src.config import Config


def req_com_retry(
    url: str,
    params: dict[str, Any],
    rate_limit: float = 0.4,
    retries: int = 3,
    timeout: int = 30,
) -> Any:
    erro_final: Exception | None = None

    for tentativa in range(retries + 1):
        if tentativa > 0:
            time.sleep(2 ** (tentativa - 1))
        elif rate_limit > 0:
            time.sleep(rate_limit)

        try:
            res = requests.get(url, params=params, timeout=timeout)
            if res.status_code == 429 or res.status_code >= 500:
                res.raise_for_status()

            res.raise_for_status()
            return res.json()

        except requests.RequestException as erro:
            erro_final = erro
            if hasattr(erro, "response") and erro.response is not None:
                if 400 <= erro.response.status_code < 500 and erro.response.status_code != 429:
                    raise

    raise RuntimeError(f"Falha ao consultar {url} após {retries} tentativas: {erro_final}") from erro_final

def extrair_pib_world_bank(
    paises_iso3: list[str],
    indicador: str,
    ano_ini: int,
    ano_fim: int,
    config: Config,
) -> list[dict[str, Any]]:
    paises_str = ";".join(paises_iso3)
    url = f"https://api.worldbank.org/v2/country/{paises_str}/indicator/{indicador}"
    registros: list[dict[str, Any]] = []
    pagina = 1

    while True:
        dados = req_com_retry(
            url,
            {"format": "json", "date": f"{ano_ini}:{ano_fim}", "per_page": 500, "page": pagina},
            config.rate_limit_seconds,
            config.max_retries,
        )

        if not isinstance(dados, list) or len(dados) < 2:
            break

        meta, items = dados[0], dados[1]
        if isinstance(items, list):
            registros.extend(items)

        total_paginas = int(meta.get("pages", 1))
        if pagina >= total_paginas:
            break
        pagina += 1

    return registros

def extrair_clima_open_meteo(
    paises: list[dict[str, Any]],
    config: Config,
) -> list[dict[str, Any]]:
    url = "https://archive-api.open-meteo.com/v1/archive"
    resultados: list[dict[str, Any]] = []

    for pais in paises:
        params = {
            "latitude": pais["lat"],
            "longitude": pais["lon"],
            "start_date": config.start_date,
            "end_date": config.end_date,
            "daily": "temperature_2m_mean,precipitation_sum",
            "timezone": "UTC",
        }
        dados = req_com_retry(url, params, config.rate_limit_seconds, config.max_retries)

        daily = dados.get("daily", {})
        resultados.append({
            "iso2": pais["iso2"],
            "iso3": pais["iso3"],
            "pais_ref": pais["pais_ref"],
            "datas": daily.get("time", []),
            "temps_media": daily.get("temperature_2m_mean", []),
            "chuvas_mm": daily.get("precipitation_sum", []),
        })

    return resultados