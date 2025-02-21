# Server Restore Automation Script

This repository contains a Python script (`server100.py`) that automates the restoration process for a server using SSH and bench commands. The script uses `pexpect` to handle interactive prompts (such as sudo and LetsEncrypt confirmations) and loads its configuration from environment variables.

## Features

- Connects to a remote server via SSH using credentials provided in environment variables.
- Executes commands to restore a site backup.
- Handles interactive prompts automatically.
- Configurable via a `.env` file.

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/itsyosefali/frappe_script_site.git
   cd frappe_script_site
