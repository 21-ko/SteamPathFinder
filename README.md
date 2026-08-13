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
from SteamPathFinder import get_game_path


game_path = get_game_path("1998340")
print("Game path:", game_path)
```

`get_game_path()` automatically finds Steam, locates the library containing the
app ID, and reads the exact folder name from `appmanifest_<app_id>.acf`. No
Steam path or game folder name is required. This also avoids case-sensitivity
problems on Linux.

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
