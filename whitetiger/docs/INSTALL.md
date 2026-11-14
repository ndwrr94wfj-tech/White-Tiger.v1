# WhiteTiger – Installation Guide

## Windows

1. Go to https://www.python.org/downloads/ and download the latest Python 3.
2. Run the installer.  
   **Important:** tick the checkbox **“Add python.exe to PATH”**.
3. Open a new Command Prompt or PowerShell window.
4. Verify:

   ```cmd
   python --version
   ```

5. Place `whitetiger.py` (and the optional `plugins` folder) anywhere you like.
6. `cd` into that folder and run:

   ```cmd
   python whitetiger.py
   ```

If colours look broken in older Windows terminals, use Windows Terminal (Microsoft Store) or run with `--no-color`.

## macOS

```bash
# Check current Python
python3 --version

# If missing or too old, install with Homebrew
brew install python

# Run
python3 whitetiger.py
```

## Linux

### Debian / Ubuntu / Kali

```bash
sudo apt update
sudo apt install -y python3
python3 whitetiger.py
```

### Fedora / RHEL

```bash
sudo dnf install -y python3
python3 whitetiger.py
```

### Arch / Manjaro

```bash
sudo pacman -S python
python3 whitetiger.py
```

## Optional convenience (Linux / macOS)

```bash
chmod +x whitetiger.py
./whitetiger.py
```

## Running a single module without the menu

```bash
python3 whitetiger.py --module 1
python3 whitetiger.py --list
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` not found | Use `python3` or reinstall Python with PATH option |
| Colours missing | Use a modern terminal (Windows Terminal, iTerm2, etc.) or `--no-color` |
| SSL errors | The tool already disables certificate verification for OSINT work |
| Permission denied on Linux | `chmod +x whitetiger.py` |

No external packages are required. Everything is pure Python standard library.
