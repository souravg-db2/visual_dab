# Databricks Bundle Manager

A simple Python Dash web application for managing Databricks bundles.

## Features

- **Simple Configuration**: Just set bundle path, target environment, and profile
- **Smart Initialization**: Creates bundles if path doesn't exist, detects existing bundles
- **Bundle Commands**: Initialize, validate, deploy, run, and destroy operations
- **Custom Commands**: Execute any databricks bundle command
- **Real-time Output**: View command execution results

## Prerequisites

- Python 3.7+
- Databricks CLI installed and configured

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Databricks CLI is installed and configured:
   ```bash
   # Install Databricks CLI if not already installed
   pip install databricks-cli
   
   # Configure with your Databricks workspace
   databricks configure --token
   
   # Optional: Configure additional profiles
   databricks configure --token --profile myprofile
   ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser: `http://localhost:8050`

3. Configure:
   - **Bundle Path**: Path to your bundle directory (existing or new)
   - **Target Environment**: Environment name (e.g., dev, staging, prod)
   - **Databricks Profile**: Profile name or DEFAULT

4. Use commands:
   - **Initialize**: Creates bundle if path doesn't exist, detects if exists
   - **Validate**: Validates bundle configuration
   - **Deploy**: Deploys bundle to target environment
   - **Run**: Executes a job (specify job name)
   - **Destroy**: Removes deployed resources
   - **Custom Command**: Execute any databricks bundle command

## How It Works

### Bundle Path Logic:
- **Path doesn't exist**: Creates new bundle with `databricks bundle init`
- **Path exists, no bundle**: Initializes bundle in existing directory
- **Path exists with bundle**: Uses existing bundle for all operations

### Command Execution:
- **Initialize**: Runs from appropriate directory to create bundle
- **Other commands**: Changes to bundle directory and executes command
- **All commands**: Automatically adds `--target` and `--profile` parameters

## Examples

### New Bundle:
1. Set Bundle Path: `/Users/me/my-new-project`
2. Click Initialize → Creates new bundle at that path

### Existing Bundle:
1. Set Bundle Path: `/Users/me/existing-project` 
2. Click Validate → Runs validation from that directory

### Commands Generated:
- `databricks bundle init default-python --output-dir my-project --target dev --profile myprofile`
- `databricks bundle validate --target dev --profile myprofile`
- `databricks bundle deploy --target dev --profile myprofile`

## Troubleshooting

- **Command not found**: Install Databricks CLI
- **Authentication errors**: Configure CLI with `databricks configure --token`
- **Bundle not found**: Check bundle path points to correct directory
- **Permission errors**: Ensure proper workspace permissions