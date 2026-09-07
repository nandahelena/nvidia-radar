from typing import TypedDict


class RadarState(TypedDict):
    consulta: str
    criterios_busca: dict
    startups_encontradas: list
    classificacoes: dict
    fontes_startup: dict
    recomendacoes: dict
    alertas_validacao: dict
    evidencias: dict
    briefing: str
    tentativas_validacao: int
