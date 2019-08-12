import unittest

from mock import patch

from infraboxcli.commands import clear_cache


class TestClearCache(unittest.TestCase):
    def test_clear_cache(self):
        with patch("infraboxcli.CLI_SETTINGS") as settings:
            # Testing without option
            with self.assertRaises(SystemExit) as e:
                clear_cache([])
            self.assertEqual(e.exception.code, 0)

            settings.clear_cache.assert_called_with(force=True)
            settings.save.assert_called_with()

            # Testing with option
            settings.reset_mock()
            with self.assertRaises(SystemExit) as e:
                clear_cache(["--full"])
            self.assertEqual(e.exception.code, 0)
            settings.clear_cache.assert_called_with(force=True)
            settings.clear_history.assert_called_with(["project_id", "build_id", "job_id"])
            settings.clear_known_project_names.assert_called_with()
            self.assertEqual(settings.id_env, {"project_id": None, "build_id": None, "job_id": None})
            settings.save.assert_called_with()
