import os
import sys

import vdf


__all__ = [
    "get_vdf_file_path",
    "get_steam_path",
    "get_app_path",
    "get_game_path",
]


if os.name == "nt":
    import winreg


def _find_steam_root(candidates):
    """Return the first candidate containing Steam's library registry."""
    for candidate in candidates:
        if not candidate:
            continue

        try:
            candidate = os.path.realpath(
                os.path.abspath(os.path.expanduser(os.fspath(candidate)))
            )
        except (OSError, RuntimeError, TypeError):
            continue

        library_registry = os.path.join(
            candidate, "steamapps", "libraryfolders.vdf"
        )
        if os.path.isfile(library_registry):
            return candidate

    return None


def _get_windows_steam_candidates():
    registry_locations = (
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam", "SteamPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Valve\Steam",
            "InstallPath",
        ),
    )

    candidates = []
    for hive, subkey, value_name in registry_locations:
        key = None
        try:
            key = winreg.OpenKey(hive, subkey)
            value, _ = winreg.QueryValueEx(key, value_name)
        except OSError:
            continue
        finally:
            if key is not None:
                winreg.CloseKey(key)

        if value:
            candidates.append(value)

    return candidates


def _get_linux_steam_candidates():
    home = os.path.expanduser("~")
    xdg_data_home = os.environ.get(
        "XDG_DATA_HOME", os.path.join(home, ".local", "share")
    )

    return [
        os.path.join(home, ".steam", "root"),
        os.path.join(home, ".steam", "steam"),
        os.path.join(xdg_data_home, "Steam"),
        os.path.join(home, ".local", "share", "Steam"),
        os.path.join(home, ".steam", "debian-installation"),
        os.path.join(
            home,
            ".var",
            "app",
            "com.valvesoftware.Steam",
            "data",
            "Steam",
        ),
        os.path.join(
            home,
            "snap",
            "steam",
            "common",
            ".local",
            "share",
            "Steam",
        ),
    ]


def get_vdf_file_path(steam_path):
    vdf_file_path = os.path.join(
        os.fspath(steam_path), "steamapps", "libraryfolders.vdf"
    )

    if not os.path.isfile(vdf_file_path):
        raise FileNotFoundError(
            "ERROR: libraryfolders.vdf file does not exist: {}".format(
                vdf_file_path
            )
        )

    return vdf_file_path


def get_steam_path():
    """Return the Steam client data directory for Windows or Linux."""
    candidates = [os.environ.get("STEAM_PATH")]

    if os.name == "nt":
        candidates.extend(_get_windows_steam_candidates())
    elif sys.platform.startswith("linux"):
        candidates.extend(_get_linux_steam_candidates())
    else:
        raise OSError("Unsupported platform: {}".format(sys.platform))

    steam_path = _find_steam_root(candidates)
    if steam_path:
        return steam_path

    raise FileNotFoundError(
        "ERROR: Steam installation could not be found. "
        "Set STEAM_PATH to the Steam client data directory."
    )


def _load_vdf_file(vdf_file_path, description):
    try:
        with open(vdf_file_path, "r", encoding="utf-8") as file:
            data = file.read()
    except (OSError, UnicodeError) as exc:
        raise IOError(
            "ERROR: Unable to read {}. {}".format(description, exc)
        ) from exc

    try:
        parsed = vdf.loads(data)
    except Exception as exc:
        raise ValueError(
            "ERROR: Unable to parse {}. {}".format(description, exc)
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError("ERROR: {} does not contain a VDF object.".format(description))

    return parsed


def get_app_path(steam_path, app_id):
    """Return the Steam library directory containing *app_id*."""
    app_id = str(app_id)
    vdf_file_path = get_vdf_file_path(steam_path)
    parsed = _load_vdf_file(vdf_file_path, "libraryfolders.vdf")

    libraryfolders = parsed.get("libraryfolders")
    if not isinstance(libraryfolders, dict):
        raise ValueError(
            "ERROR: libraryfolders.vdf does not contain libraryfolders."
        )

    found_in_registry = False

    for folder in libraryfolders.values():
        if not isinstance(folder, dict):
            continue

        library_path = folder.get("path")
        if not isinstance(library_path, str) or not library_path:
            continue

        apps = folder.get("apps", {})
        listed = isinstance(apps, dict) and app_id in apps
        manifest_path = os.path.join(
            library_path, "steamapps", "appmanifest_{}.acf".format(app_id)
        )
        has_manifest = os.path.isfile(manifest_path)

        if listed or has_manifest:
            found_in_registry = True
            if os.path.isdir(library_path):
                return os.path.realpath(library_path)

    if found_in_registry:
        raise FileNotFoundError(
            "ERROR: The Steam library containing app {} is not accessible."
            .format(app_id)
        )

    raise FileNotFoundError(
        "ERROR: Could not find the installation path for app {}.".format(app_id)
    )


def _get_manifest_install_dir(library_path, app_id):
    manifest_path = os.path.join(
        library_path, "steamapps", "appmanifest_{}.acf".format(app_id)
    )
    if not os.path.isfile(manifest_path):
        raise FileNotFoundError(
            "ERROR: Steam app manifest does not exist: {}".format(manifest_path)
        )

    parsed = _load_vdf_file(
        manifest_path, "appmanifest_{}.acf".format(app_id)
    )
    app_state = parsed.get("AppState")
    if not isinstance(app_state, dict):
        raise ValueError(
            "ERROR: The app manifest does not contain AppState: {}".format(
                manifest_path
            )
        )

    install_dir = app_state.get("installdir")
    if not isinstance(install_dir, str) or not install_dir:
        raise ValueError(
            "ERROR: The app manifest does not contain installdir: {}".format(
                manifest_path
            )
        )

    return install_dir


def get_game_path(app_id):
    """Return a game's install directory using only its Steam app ID."""
    app_id = str(app_id)
    steam_path = get_steam_path()
    app_path = get_app_path(steam_path, app_id)
    game_name = _get_manifest_install_dir(app_path, app_id)

    game_path = os.path.join(app_path, "steamapps", "common", game_name)

    if not os.path.isdir(game_path):
        raise FileNotFoundError(
            "ERROR: The game path does not exist: {}".format(game_path)
        )

    return os.path.realpath(game_path)
