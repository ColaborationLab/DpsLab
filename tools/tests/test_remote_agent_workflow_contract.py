from pathlib import Path
import unittest


class RemoteAgentWorkflowContractTests(unittest.TestCase):
    def test_remote_collaboration_contract_is_hardened(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[2]
            / "docs"
            / "REMOTE_AGENT_WORKFLOW.md"
        ).read_text(encoding="utf-8")

        self.assertIn("`ColaborationLab/DpsLab`", workflow)
        self.assertNotIn("`dpcs90/DpsLab`", workflow)
        self.assertIn("## Modos de permiso y entrega", workflow)
        self.assertIn("**Read**: permite auditoría y entrega lectoras", workflow)
        self.assertIn("política de forks privados", workflow)
        self.assertIn("**Write**: requiere una decisión humana posterior", workflow)
        self.assertIn("`agent/<task_id>/<slug>`", workflow)
        self.assertIn("Nunca permite trabajar sobre `main`", workflow)
        self.assertIn("el PR es\n  obligatorio", workflow)
        self.assertIn("sesión de repositorio preautorizada", workflow)
        self.assertIn("No se añaden `GH_TOKEN`, PAT", workflow)
        self.assertIn("secretos", workflow)


if __name__ == "__main__":
    unittest.main()
