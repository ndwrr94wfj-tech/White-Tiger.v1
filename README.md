# WhiteTiger v1.0

**osint · csint · pentest multitool**  
Single-file · stdlib only · Python 3.8+ · zero dependencies

```
python3 whitetiger.py
```

---

## Features

- 100 modules (pentest / OSINT / CSINT / utilities)
- Themes, live banner, matrix rain, ambient glow
- Port scanning, web fuzzing, TLS audit, subdomain takeover, JWT, stego, etc.
- Temp mail, site mirror, report forge, vault, and more
- Plugin support (`./plugins/*.py`)
- JSON reports written next to the script

---

## Install & Run

### Requirements

- **Python 3.8 or newer** (3.10+ recommended)
- No `pip install` needed – pure standard library

### Windows

1. Download & install Python from [python.org](https://www.python.org/downloads/)  
   (check the box **“Add Python to PATH”**)
2. Download this repository (Code → Download ZIP) or clone it
3. Open **Command Prompt** or **PowerShell** in the folder that contains `whitetiger.py`
4. Run:

```cmd
python whitetiger.py
```

Useful flags:

```cmd
python whitetiger.py --no-anim
python whitetiger.py --theme=matrix
python whitetiger.py --list
python whitetiger.py --module 1
```

### macOS

1. Python 3 is usually already present. Check:

```bash
python3 --version
```

If missing, install via Homebrew:

```bash
brew install python
```

2. Open **Terminal** in the project folder and run:

```bash
python3 whitetiger.py
```

### Linux (Ubuntu / Debian / Fedora / Arch …)

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y python3

# Fedora
sudo dnf install -y python3

# Arch
sudo pacman -S python
```

Then:

```bash
python3 whitetiger.py
```

### Optional – make it executable (Linux / macOS)

```bash
chmod +x whitetiger.py
./whitetiger.py
```

---

## Command-line flags

| Flag | Description |
|------|-------------|
| `--no-anim` | Skip boot sequence & intro animation |
| `--calm` | Disable glow, flash, stripes, sweep |
| `--no-color` | Disable colours (clean for piping) |
| `--fast` | Higher FPS, no intro |
| `--rain` | Matrix rain backdrop |
| `--glitch` / `--no-glitch` | Banner glitch effect |
| `--fps=N` | Target frames per second (5-60) |
| `--theme=NAME` | ice, blood, matrix, vapor, amber, cyan, mono, rust, nord, sakura, toxic |
| `--layout=auto\|boxes\|flat` | Menu layout |
| `--module N` | Launch a single module by number |
| `--list` | Print all modules and exit |
| `--selftest` | Verify helpers resolve |

---

## Usage inside the tool

- Type a **module number** (e.g. `1`) and press Enter
- `/word` – filter modules by keyword
- `H` – help · `S` – settings · `T` – cycle theme · `R` – random module
- `B` – batch runner · `Q` – quit

Reports are saved as `wt_*.json` in the current working directory.  
Module 96 merges them into a single HTML report.

---

## Plugins

Drop any `.py` file that defines a list named `MODULES` into the `plugins/` folder:

```python
# plugins/example.py
def my_module():
    print("hello from plugin")

MODULES = [
    ("My Tool", "short description", my_module),
]
```

They appear automatically under the **PLUGINS** category.

---

## Author

**@azerkash**

```
python3 whitetiger.py
```
