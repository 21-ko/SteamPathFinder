import os
import tempfile
import unittest
from unittest import mock

import SteamPathFinder.SteamPathFinder as finder


LIBRARY_VDF_HEADER = '"libraryfolders"\n{\n'


def escape_vdf(value):
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def create_steam_root(path):
    steamapps = os.path.join(path, "steamapps")
    os.makedirs(steamapps, exist_ok=True)
    with open(
        os.path.join(steamapps, "libraryfolders.vdf"),
        "w",
        encoding="utf-8",
    ) as file:
        file.write(LIBRARY_VDF_HEADER + "}\n")


class FakeWinreg:
    HKEY_CURRENT_USER = object()
    HKEY_LOCAL_MACHINE = object()

    def __init__(self, steam_path):
        self.steam_path = steam_path
        self.closed_keys = []

    def OpenKey(self, hive, subkey):
        if hive is self.HKEY_CURRENT_USER and subkey == r"SOFTWARE\Valve\Steam":
            return object()
        raise FileNotFoundError

    def QueryValueEx(self, key, value_name):
        if value_name == "SteamPath":
            return self.steam_path, None
        raise FileNotFoundError

    def CloseKey(self, key):
        self.closed_keys.append(key)


class SteamPathFinderTests(unittest.TestCase):
    def test_steam_path_environment_override(self):
        with tempfile.TemporaryDirectory() as steam_root:
            create_steam_root(steam_root)
            with mock.patch.dict(
                os.environ, {"STEAM_PATH": steam_root}, clear=True
            ):
                self.assertEqual(
                    finder.get_steam_path(), os.path.realpath(steam_root)
                )

    def test_linux_standard_steam_root(self):
        with tempfile.TemporaryDirectory() as home:
            steam_root = os.path.join(home, ".steam", "root")
            create_steam_root(steam_root)
            original_expanduser = os.path.expanduser

            def expand_test_home(path):
                if path == "~":
                    return home
                return original_expanduser(path)

            with mock.patch.object(finder.os, "name", "posix"), mock.patch.object(
                finder.sys, "platform", "linux"
            ), mock.patch.object(
                finder.os.path, "expanduser", side_effect=expand_test_home
            ), mock.patch.dict(
                os.environ, {}, clear=True
            ):
                self.assertEqual(
                    finder.get_steam_path(), os.path.realpath(steam_root)
                )

    def test_windows_registry_path(self):
        with tempfile.TemporaryDirectory() as steam_root:
            create_steam_root(steam_root)
            fake_winreg = FakeWinreg(steam_root)

            with mock.patch.object(
                finder, "winreg", fake_winreg, create=True
            ), mock.patch.object(finder.os, "name", "nt"), mock.patch.dict(
                os.environ, {}, clear=True
            ):
                self.assertEqual(
                    finder.get_steam_path(), os.path.realpath(steam_root)
                )

            self.assertEqual(len(fake_winreg.closed_keys), 1)

    def test_app_path_finds_secondary_library(self):
        with tempfile.TemporaryDirectory() as directory:
            steam_root = os.path.join(directory, "Steam")
            library_path = os.path.join(directory, "SD Card", "SteamLibrary")
            os.makedirs(os.path.join(steam_root, "steamapps"))
            os.makedirs(os.path.join(library_path, "steamapps"))

            vdf_text = (
                LIBRARY_VDF_HEADER
                + '    "0"\n    {\n'
                + '        "path" "{}"\n'.format(escape_vdf(steam_root))
                + '        "apps"\n        {\n        }\n'
                + "    }\n"
                + '    "1"\n    {\n'
                + '        "path" "{}"\n'.format(escape_vdf(library_path))
                + '        "apps"\n        {\n'
                + '            "1998340" "1"\n'
                + "        }\n"
                + "    }\n"
                + "}\n"
            )
            with open(
                os.path.join(steam_root, "steamapps", "libraryfolders.vdf"),
                "w",
                encoding="utf-8",
            ) as file:
                file.write(vdf_text)

            self.assertEqual(
                finder.get_app_path(steam_root, 1998340),
                os.path.realpath(library_path),
            )

    def test_app_path_rejects_an_unmounted_library(self):
        with tempfile.TemporaryDirectory() as steam_root:
            steamapps = os.path.join(steam_root, "steamapps")
            os.makedirs(steamapps)
            missing_library = os.path.join(steam_root, "missing")
            vdf_text = (
                LIBRARY_VDF_HEADER
                + '    "1"\n    {\n'
                + '        "path" "{}"\n'.format(escape_vdf(missing_library))
                + '        "apps"\n        {\n'
                + '            "1998340" "1"\n'
                + "        }\n"
                + "    }\n"
                + "}\n"
            )
            with open(
                os.path.join(steamapps, "libraryfolders.vdf"),
                "w",
                encoding="utf-8",
            ) as file:
                file.write(vdf_text)

            with self.assertRaisesRegex(FileNotFoundError, "not accessible"):
                finder.get_app_path(steam_root, "1998340")

    def test_game_path_uses_manifest_install_dir(self):
        with tempfile.TemporaryDirectory() as steam_root:
            steamapps = os.path.join(steam_root, "steamapps")
            game_name = "Case Sensitive Game"
            game_path = os.path.join(steamapps, "common", game_name)
            os.makedirs(game_path)

            library_vdf = (
                LIBRARY_VDF_HEADER
                + '    "0"\n    {\n'
                + '        "path" "{}"\n'.format(escape_vdf(steam_root))
                + '        "apps"\n        {\n'
                + '            "1998340" "1"\n'
                + "        }\n"
                + "    }\n"
                + "}\n"
            )
            with open(
                os.path.join(steamapps, "libraryfolders.vdf"),
                "w",
                encoding="utf-8",
            ) as file:
                file.write(library_vdf)

            manifest = (
                '"AppState"\n{\n'
                + '    "appid" "1998340"\n'
                + '    "installdir" "{}"\n'.format(escape_vdf(game_name))
                + "}\n"
            )
            with open(
                os.path.join(steamapps, "appmanifest_1998340.acf"),
                "w",
                encoding="utf-8",
            ) as file:
                file.write(manifest)

            with mock.patch.dict(
                os.environ, {"STEAM_PATH": steam_root}, clear=True
            ):
                self.assertEqual(
                    finder.get_game_path("1998340"),
                    os.path.realpath(game_path),
                )

    def test_game_path_rejects_the_old_multi_argument_api(self):
        with self.assertRaises(TypeError):
            finder.get_game_path("/path/to/Steam", "1998340")


if __name__ == "__main__":
    unittest.main()
