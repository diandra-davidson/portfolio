# Python Workspace

A simple Python workspace configured with a virtual environment.

## Project Structure

```
portfolio/
├── .github/
│   └── copilot-instructions.md
├── .venv/                    # Virtual environment (auto-generated)
├── main.py                   # Main application entry point
├── requirements.txt          # Project dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Getting Started

### Prerequisites

- Python 3.13 or higher

### Installation

The virtual environment has already been configured. To activate it manually:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/MacOS:**
```bash
source .venv/bin/activate
```

### Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### Running the Application

```powershell
python main.py
```

## Development

Add your Python dependencies to `requirements.txt` and install them using:

```powershell
python -m pip install -r requirements.txt
```

## License

This project is open source and available under your chosen license.
