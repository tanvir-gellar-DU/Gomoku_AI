# Gomoku AI

Small **Gomoku (Five-in-a-Row)** implementation with a simple AI and both **GUI** and **CLI** frontends.



##  Features

* Play **Human vs AI**, **Human vs Human**, or run **AI vs AI** simulations
* Simple **minimax / heuristic engine** with search and time limits
* **Tkinter GUI** with fullscreen board and optional sound effects
* Small, **self-contained codebase** intended for learning and experimentation

---

##  Requirements

* **Python 3.12+**
  *(Developed and tested on CPython 3.12+)*
* **tkinter** (included with most Python installations)
* **pytest** (for running tests)
* **pygame** *(optional, for sound support)*
  If not installed, the GUI falls back to the system bell

---

##  Quick Start

### 1️⃣ Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2️⃣ Install optional dependencies

```bash
pip install pytest
pip install pygame   # optional, for sound playback
```

---

##  Running the GUI

From the repository root:

```bash
python -m src.ui_gui
```

Use the start screen to select:

* Human vs Human
* Human vs AI
* AI vs AI simulation

---

##  Running the CLI

To start the text-based interface:

```bash
python -m src.ui_cli
```

---

##  Sound / Audio Notes

* To use custom sounds, create a folder:

  ```
  src/sounds/
  ```
* Supported filenames (all optional):

  * `move.wav`
  * `win.wav`
  * `lose.wav`
  * `draw.wav`

If **pygame** is installed, the GUI uses `pygame.mixer`.
Otherwise, it falls back to the system bell.

---

##  Tests

Run unit tests with:

```bash
pytest
```

---

## Development Notes

* The GUI uses **relative imports**, so always run it with:

  ```bash
  python -m src.ui_gui
  ```
* The engine, search, and evaluation modules are intentionally **small and readable**
* Ideal for experimenting with:

  * Improved heuristics
  * Alternative search strategies
  * Performance tuning





