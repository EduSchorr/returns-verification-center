import unittest

from classificador_respostas import classify_reply

class ClassificationTests(unittest.TestCase):
    def test_detects_returned_case(self):
        result = classify_reply("Retorno", "Recebemos a devolução do item.")
        self.assertEqual(result.status, "RETURNED")

    def test_negative_terms_take_priority(self):
        result = classify_reply("Pendência", "Cliente não devolveu o produto.")
        self.assertEqual(result.status, "PENDING")

    def test_unknown_reply_requires_review(self):
        result = classify_reply("Atualização", "Estamos verificando internamente.")
        self.assertEqual(result.status, "REVIEW")

if __name__ == "__main__":
    unittest.main()
