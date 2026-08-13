# SteamPathFinder

A Python utility for locating Steam libraries and installed games on Windows
and Linux, including SteamOS on Steam Deck.

## Supported platforms

- Windows 10 and 11
- Linux Steam installations on Arch Linux, SteamOS, Debian, Ubuntu, and other
  distributions that use the standard Steam directory layout
- Steam installed through Flatpak or Snap when its data directory is visible
  to the Python process

SteamPathFinder reads `libraryfolders.vdf`, so games installed in secondary
libraries such as a Steam Deck microSD card are detected without hard-coding a
mount path.

## Installation

```console
pip install SteamPathFinder
```

On SteamOS, use a virtual environment rather than modifying the read-only base
system:

```console
python3 -m venv .venv
source .venv/bin/activate
pip install SteamPathFinder
```

## Basic usage

```python
from SteamPathFinder import get_app_path, get_game_path, get_steam_path


steam_path = get_steam_path()
print("Steam client data:", steam_path)

app_id = "1998340"

# The Steam library containing the application. This can be an internal drive,
# an external drive, or a Steam Deck microSD card.
library_path = get_app_path(steam_path, app_id)
print("Steam library:", library_path)

# The folder name is read from appmanifest_<app_id>.acf. This avoids
# case-sensitivity problems on Linux.
game_path = get_game_path(steam_path, app_id)
print("Game path:", game_path)
```

Passing the game folder name remains supported for compatibility:

```python
game_path = get_game_path(
    steam_path,
    "1998340",
    "Labyrinth of Galleria The Moon Society",
)
```

## Steam path discovery

On Windows, SteamPathFinder reads the Steam registry entries. On Linux, it
checks the standard native, Flatpak, and Snap data directories, including:

- `~/.steam/root`
- `~/.steam/steam`
- `$XDG_DATA_HOME/Steam`
- `~/.local/share/Steam`
- `~/.steam/debian-installation`
- `~/.var/app/com.valvesoftware.Steam/data/Steam`

For a non-standard installation, set `STEAM_PATH` to the Steam client data
directory containing `steamapps/libraryfolders.vdf`:

```console
export STEAM_PATH=/path/to/Steam
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
