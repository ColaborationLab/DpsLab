import unittest
from unittest.mock import patch

from dpslab.i18n import SUPPORTED_LOCALES, _catalog, messages, normalize_locale, placeholders, resolved_locale, tr


class LocalizationTests(unittest.TestCase):
    def test_catalogs_have_same_stable_keys_and_nonempty_values(self) -> None:
        keys = set(_catalog("en"))
        for locale in SUPPORTED_LOCALES:
            catalog = _catalog(locale)
            self.assertEqual(set(catalog), keys)
            self.assertTrue(all(isinstance(value, str) and value for value in catalog.values()))

    def test_locale_aliases_auto_and_fallback(self) -> None:
        self.assertEqual(normalize_locale("es-MX"), "es")
        self.assertEqual(normalize_locale("esES"), "es")
        self.assertEqual(normalize_locale("pt_BR"), "pt-BR")
        self.assertEqual(normalize_locale("ptBR"), "pt-BR")
        with patch("dpslab.i18n.system_locale.getlocale", return_value=("pt_BR", "UTF-8")):
            self.assertEqual(resolved_locale("auto"), "pt-BR")
            self.assertEqual(messages("auto")["app.title"], "DpsLab — Comparação de loadouts")
        self.assertEqual(tr("status.saved", "pt-BR", name="Drena"), "Perfil 'Drena' salvo.")
        self.assertEqual(tr("missing.key", "es"), "missing.key")

    def test_placeholder_inventory_is_identical(self) -> None:
        for key, text in _catalog("en").items():
            expected = placeholders(text)
            for locale in SUPPORTED_LOCALES:
                self.assertEqual(placeholders(_catalog(locale)[key]), expected, key)
