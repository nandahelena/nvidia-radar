import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agents.evidence_validator_agent import evidence_validator_agent
from graph import _proximo_passo_apos_validacao


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


if __name__ == "__main__":
    unittest.main()
