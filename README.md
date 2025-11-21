# CodeGate

CodeGate is a Linux productivity tool that blocks distracting applications and requires you to solve a coding challenge to regain access.

## Features
*   **Distraction Blocking**: Uses `SIGSTOP` to pause distracting processes (e.g., Discord, Browser) without killing them.
*   **Productive Unlocking**: Solve a random algorithm/data structure problem to unblock your apps.
*   **Offline Ready**: Works without an internet connection using a bundled challenge set.
*   **Secure**: Runs in user-space, no root privileges required.

## Prerequisites
*   Linux OS (tested on Ubuntu/Debian)
*   Python 3.10+
*   `pip`

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/mouwaficbdr/codegate.git
    cd codegate
    ```

2.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Start the application:
    ```bash
    python src/main.py
    ```

2.  Configure your blocked applications in `config.json` (created on first run).

## Development

*   **GUI**: Built with PySide6.
*   **Process Management**: Uses `psutil`.

## License
MIT
