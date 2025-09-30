import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import subprocess
import os
import json
import tempfile
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Simple Databricks Bundle Manager"

# App layout
app.layout = dbc.Container([
    html.H1("Databricks Bundle Manager", className="text-center mb-4"),
    html.Hr(),
    
    # Configuration Section
    dbc.Card([
        dbc.CardHeader(html.H4("Configuration")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Personal Access Token (PAT):"),
                    dbc.Input(
                        id="pat-token",
                        type="password",
                        placeholder="Enter your Databricks PAT token"
                    ),
                ], width=12),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Bundle Path:"),
                    dbc.Input(
                        id="bundle-path",
                        type="text",
                        # placeholder="/path/to/your/bundle"
                        value = "/Users/sourav.gulati/projects/python_dab/new_project_1"
                    ),
                ], width=12),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Job ID (for Bind):"),
                    dbc.Input(
                        id="job-id",
                        type="text",
                        # placeholder="e.g., 496656734454296"
                        value="295337637008564"
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("Job Key (for Bind):"),
                    dbc.Input(
                        id="job-key",
                        type="text",
                        # placeholder="e.g., my_job"
                        value="job_new"
                    ),
                ], width=6),
            ], className="mb-3"),
        ])
    ], className="mb-4"),
    
    # Action Buttons
    dbc.Card([
        dbc.CardHeader(html.H4("Actions")),
        dbc.CardBody([
            dbc.Button("Create Bundle", id="btn-create", color="primary", className="me-2"),
            dbc.Button("Validate", id="btn-validate", color="info", className="me-2"),
            dbc.Button("Bind", id="btn-bind", color="warning", className="me-2"),
            dbc.Button("Deploy", id="btn-deploy", color="success", className="me-2"),
        ])
    ], className="mb-4"),
    
    # Output Section
    dbc.Card([
        dbc.CardHeader(html.H4("Output")),
        dbc.CardBody([
            html.Pre(
                id="output",
                style={
                    "background-color": "#f8f9fa",
                    "padding": "15px",
                    "border-radius": "5px",
                    "min-height": "200px",
                    "font-family": "monospace"
                },
                children="Ready..."
            )
        ])
    ])
    
], fluid=True, className="py-4")


def check_bundle_exists(bundle_path):
    """Check if a databricks bundle exists at the given path."""
    if not os.path.exists(bundle_path):
        return False, "Path does not exist"
    
    databricks_yml = os.path.join(bundle_path, "databricks.yml")
    if os.path.exists(databricks_yml):
        return True, "Bundle exists"
    
    return False, "Path exists but no databricks.yml found"


def run_databricks_command(command, bundle_path, pat_token):
    """Run a databricks command."""
    try:
        print(f"DEBUG: Starting command execution")
        print(f"DEBUG: Command: {' '.join(command)}")
        print(f"DEBUG: Bundle path: {bundle_path}")
        print(f"DEBUG: PAT token provided: {'Yes' if pat_token else 'No'}")
        
        # Set environment variables
        env = os.environ.copy()
        env['DATABRICKS_TOKEN'] = pat_token
        
        # Add additional environment variables for non-interactive execution
        env['DATABRICKS_CLI_DO_NOT_TRACK'] = '1'
        env['DATABRICKS_CLI_SKIP_VERIFY'] = '1'
        env['TERM'] = 'dumb'  # Prevent interactive prompts
        env['PYTHONUNBUFFERED'] = '1'  # Ensure output is not buffered
        
        print(f"DEBUG: Environment variables set")
        print(f"DEBUG: DATABRICKS_TOKEN length: {len(pat_token) if pat_token else 0}")
        
        # Change to bundle directory
        original_dir = os.getcwd()
        print(f"DEBUG: Original directory: {original_dir}")
        
        if bundle_path and os.path.exists(bundle_path):
            os.chdir(bundle_path)
            print(f"DEBUG: Changed to bundle directory: {bundle_path}")
        else:
            print(f"DEBUG: Bundle path doesn't exist or is empty, staying in: {original_dir}")
        
        print(f"DEBUG: Current working directory: {os.getcwd()}")
        print(f"DEBUG: About to execute subprocess.run...")
        
        # Additional debugging - check if databricks CLI is accessible
        try:
            version_check = subprocess.run(['databricks', '--version'], capture_output=True, text=True, timeout=5)
            print(f"DEBUG: Databricks CLI version check - Exit code: {version_check.returncode}")
            print(f"DEBUG: Databricks CLI version: {version_check.stdout.strip()}")
        except Exception as version_e:
            print(f"DEBUG: Failed to check databricks version: {version_e}")
        
        # Run command with additional debugging
        print(f"DEBUG: Full command array: {command}")
        print(f"DEBUG: Environment DATABRICKS_TOKEN set: {'DATABRICKS_TOKEN' in env}")
        
        # Try with a shorter timeout first to see if it's hanging
        print(f"DEBUG: Starting subprocess with 10 second timeout...")
        start_time = datetime.now()
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,  # Shorter timeout for testing
            env=env
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        print(f"DEBUG: Subprocess took {execution_time:.2f} seconds")
        
        print(f"DEBUG: Subprocess completed with exit code: {result.returncode}")
        print(f"DEBUG: STDOUT length: {len(result.stdout) if result.stdout else 0}")
        print(f"DEBUG: STDERR length: {len(result.stderr) if result.stderr else 0}")
        
        # Return to original directory
        os.chdir(original_dir)
        print(f"DEBUG: Returned to original directory: {original_dir}")
        
        # Format output
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output = f"[{timestamp}] Command: {' '.join(command)}\n"
        output += f"Exit Code: {result.returncode}\n\n"
        
        # Print command to logs
        print(f"COMMAND EXECUTED: {' '.join(command)}")
        
        if result.stdout:
            output += "Output:\n" + result.stdout + "\n"
            print(f"DEBUG: STDOUT: {result.stdout[:200]}...")  # First 200 chars
        if result.stderr:
            output += "Error:\n" + result.stderr + "\n"
            print(f"DEBUG: STDERR: {result.stderr[:200]}...")  # First 200 chars
        
        print(f"DEBUG: Command execution completed successfully")
        return output, result.returncode == 0
        
    except subprocess.TimeoutExpired as e:
        print(f"DEBUG: Command timed out after 30 seconds")
        print(f"DEBUG: Timeout exception: {str(e)}")
        os.chdir(original_dir)
        return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Command timed out\n", False
    except Exception as e:
        print(f"DEBUG: Exception occurred: {type(e).__name__}: {str(e)}")
        print(f"DEBUG: Current directory when exception occurred: {os.getcwd()}")
        os.chdir(original_dir)
        return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: {str(e)}\n", False


@app.callback(
    Output("output", "children"),
    [Input("btn-create", "n_clicks"),
     Input("btn-validate", "n_clicks"),
     Input("btn-bind", "n_clicks"),
     Input("btn-deploy", "n_clicks")],
    [State("pat-token", "value"),
     State("bundle-path", "value"),
     State("job-id", "value"),
     State("job-key", "value")]
)
def handle_actions(btn_create, btn_validate, btn_bind, btn_deploy, pat_token, bundle_path, job_id, job_key):
    print(f"CALLBACK DEBUG: handle_actions called")
    print(f"CALLBACK DEBUG: btn_create={btn_create}, btn_validate={btn_validate}, btn_bind={btn_bind}, btn_deploy={btn_deploy}")
    
    ctx = dash.callback_context
    if not ctx.triggered:
        print(f"CALLBACK DEBUG: No trigger, returning 'Ready...'")
        return "Ready..."
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    print(f"CALLBACK DEBUG: Button triggered: {button_id}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"CALLBACK DEBUG: Starting processing at {timestamp}")
    
    # Validate inputs
    if not pat_token:
        return f"[{timestamp}] Error: Please enter your PAT token"
    
    if not bundle_path:
        return f"[{timestamp}] Error: Please enter bundle path"
    
    if button_id == "btn-create":
        # Check if bundle already exists
        exists, message = check_bundle_exists(bundle_path)
        
        if exists:
            return f"[{timestamp}] Bundle already exists at: {bundle_path}\n{message}"
        
        # Create the directory if it doesn't exist
        if not os.path.exists(bundle_path):
            try:
                os.makedirs(bundle_path, exist_ok=True)
                output = f"[{timestamp}] Created directory: {bundle_path}\n"
            except Exception as e:
                return f"[{timestamp}] Error creating directory: {str(e)}"
        else:
            output = f"[{timestamp}] Directory exists: {bundle_path}\n"
        
        # Initialize bundle using custom template with config file
        template_path = "./dab-container-template"
        config_file = "./dab-container-template/config.json"
        
        command = [
            "databricks", "bundle", "init", template_path, 
            "--output-dir", f"{bundle_path}",
            "--config-file", config_file
        ]
        # Run init command from parent directory, not from bundle_path
        parent_dir = os.path.dirname(bundle_path) or os.getcwd()
        result, success = run_databricks_command(command, parent_dir, pat_token)
        
        return output + result
    
    elif button_id == "btn-validate":
        # Check if bundle exists
        exists, message = check_bundle_exists(bundle_path)
        
        if not exists:
            return f"[{timestamp}] Error: {message} at {bundle_path}"
        
        # Run validate command
        command = ["databricks", "bundle", "validate"]
        result, success = run_databricks_command(command, bundle_path, pat_token)
        
        return result
    
    elif button_id == "btn-bind":
        # Validate bind-specific inputs
        if not job_id:
            return f"[{timestamp}] Error: Please enter Job ID for binding"
        
        if not job_key:
            return f"[{timestamp}] Error: Please enter Job Key for binding"
        
        # Check if bundle exists
        exists, message = check_bundle_exists(bundle_path)
        
        if not exists:
            return f"[{timestamp}] Error: {message} at {bundle_path}"
        
        # Run bundle generate job command
        generate_command = [
            "databricks", "bundle", "generate", "job", 
            "--existing-job-id", job_id,
            "--key", job_key,
            "--force"
        ]
        result1, success1 = run_databricks_command(generate_command, bundle_path, pat_token)
        
        if not success1:
            return result1
        
        # Run bundle deployment bind command
        bind_command = [
            "databricks", "bundle", "deployment", "bind", 
            job_key, job_id, "--auto-approve","--target", "dev"
        ]
        result2, success2 = run_databricks_command(bind_command, bundle_path, pat_token)
        
        # Combine both outputs
        combined_output = result1 + "\n" + "="*50 + "\n" + result2
        
        print(f"CALLBACK DEBUG: Bind operation completed, returning combined output")
        return combined_output
    
    elif button_id == "btn-deploy":
        # Check if bundle exists
        exists, message = check_bundle_exists(bundle_path)
        
        if not exists:
            return f"[{timestamp}] Error: {message} at {bundle_path}"
        
        # Run bundle deploy command
        deploy_command = ["databricks", "bundle", "deploy", "--target", "dev"]
        result, success = run_databricks_command(deploy_command, bundle_path, pat_token)
        
        print(f"CALLBACK DEBUG: Deploy operation completed")
        return result
    
    print(f"CALLBACK DEBUG: No button matched, returning 'Ready...'")
    return "Ready..."


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)