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

## keyring-pass Setup

If `keyring` falls back to `keyring.backends.fail.Keyring`, the `pass` CLI is usually missing or not initialized.

1. Install system dependencies:

```bash
sudo apt-get update
sudo apt-get install -y pass gnupg
```

2. Install Python packages:

```bash
python -m pip install keyring keyring-pass
```

3. Create or use a GPG key and initialize `pass`:

```bash
gpg --full-generate-key
gpg --list-secret-keys --keyid-format LONG
pass init <YOUR_GPG_KEY_ID>
```

4. Verify backend discovery:

```bash
python -c "import keyring; print(keyring.get_keyring())"
```

Expected output should reference `keyring_pass.PasswordStoreBackend` (or another non-fail backend).

## License

This project is open source and available under your chosen license.
