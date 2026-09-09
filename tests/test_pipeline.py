import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agents.evidence_validator_agent import evidence_validator_agent
from graph import _proximo_passo_apos_validacao
from agents.recommender_agent import (
    RecomendacaoEstruturada,
    RespostaRecomendacoesEstruturada,
    erro_de_quota,
    formatar_recomendacoes_estruturadas,
)


class PipelineTest(unittest.TestCase):
    def test_validator_preserves_valid_nvidia_product(self):
        state = {
            "recomendacoes": {"Maritaca AI": "Tecnologia: NVIDIA NeMo\nJustificativa: caso Writer"},
            "tentativas_validacao": 0,
        }
        result = evidence_validator_agent(state)
        self.assertEqual(result["alertas_validacao"], {})
        self.assertIn("NVIDIA NeMo", result["recomendacoes"]["Maritaca AI"])
        self.assertEqual(result["tentativas_validacao"], 1)

    def test_validator_blocks_unknown_product(self):
        state = {
            "recomendacoes": {"Teste": "Tecnologia: Produto Inventado"},
            "tentativas_validacao": 0,
        }
        result = evidence_validator_agent(state)
        self.assertIn("Teste", result["alertas_validacao"])
        self.assertEqual(_proximo_passo_apos_validacao(result), "retry")

    def test_second_validation_failure_goes_to_briefing(self):
        state = {"alertas_validacao": {"Teste": ["Produto Inventado"]}, "tentativas_validacao": 2}
        self.assertEqual(_proximo_passo_apos_validacao(state), "briefing")

    def test_structured_recommendation_formats_only_allowed_sources(self):
        resposta = RespostaRecomendacoesEstruturada(
            recomendacoes=[
                RecomendacaoEstruturada(
                    tecnologia="NVIDIA NeMo",
                    justificativa_tecnica="Suporta customização de LLMs.",
                    justificativa_negocio="Acelera o desenvolvimento.",
                    prioridade="alta",
                    complexidade_implementacao="média",
                    proxima_acao_sugerida="Executar um piloto.",
                    evidencias_usadas=[
                        "https://nvidia.com/valid",
                        "https://example.com/inventada",
                    ],
                )
            ]
        )
        texto = formatar_recomendacoes_estruturadas(
            resposta,
            [{"produto": "NVIDIA NeMo", "url": "https://nvidia.com/valid"}],
        )
        self.assertIn("https://nvidia.com/valid", texto)
        self.assertNotIn("https://example.com/inventada", texto)

    def test_empty_structured_recommendation_is_explicit(self):
        texto = formatar_recomendacoes_estruturadas(
            RespostaRecomendacoesEstruturada(recomendacoes=[]),
            [],
        )
        self.assertIn("não foi possível identificar", texto.lower())

    def test_quota_error_is_detected_without_fallback(self):
        self.assertTrue(erro_de_quota(Exception("Error 429: tokens per day")))
        self.assertFalse(erro_de_quota(Exception("schema not supported")))


if __name__ == "__main__":
    unittest.main()
