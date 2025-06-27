import subprocess
import os
import time
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
namespace = "monitoring"

def log_message(message, level="INFO"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def run_command(command, error_message, timeout=300):
    log_message(f"Executing command: {command}")
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True
        )
        
        # Read output in real-time
        stdout_lines = []
        stderr_lines = []
        
        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()
            
            if stdout_line:
                log_message(f"STDOUT: {stdout_line.strip()}")
                stdout_lines.append(stdout_line)
            
            if stderr_line:
                log_message(f"STDERR: {stderr_line.strip()}", "WARNING")
                stderr_lines.append(stderr_line)
            
            # Check if process has finished
            if process.poll() is not None:
                break
                
            # Check for timeout
            if timeout and time.time() - start_time > timeout:
                process.kill()
                error_msg = f"Command timed out after {timeout} seconds"
                log_message(error_msg, "ERROR")
                return False, error_msg
        
        # Get remaining output
        remaining_stdout, remaining_stderr = process.communicate()
        if remaining_stdout:
            log_message(f"STDOUT: {remaining_stdout.strip()}")
            stdout_lines.extend(remaining_stdout.splitlines())
        if remaining_stderr:
            log_message(f"STDERR: {remaining_stderr.strip()}", "WARNING")
            stderr_lines.extend(remaining_stderr.splitlines())
        
        if process.returncode != 0:
            error_output = "\n".join(stderr_lines)
            log_message(f"{error_message}\nError details: {error_output}", "ERROR")
            return False, error_output
            
        return True, "\n".join(stdout_lines)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_message(error_msg, "ERROR")
        return False, error_msg

def check_prerequisites():
    log_message("Checking prerequisites...")
    
    # Check if kubectl is installed
    success, _ = run_command("kubectl version --client", "kubectl is not installed or not accessible")
    if not success:
        return False
        
    # Check if helm is installed
    success, _ = run_command("helm version", "helm is not installed or not accessible")
    if not success:
        return False
        
    # Check if we can access the cluster
    success, _ = run_command("kubectl cluster-info", "Cannot access Kubernetes cluster")
    if not success:
        return False
        
    log_message("All prerequisites are satisfied")
    return True

def install_or_upgrade_prometheus():
    log_message("Starting Prometheus installation/upgrade process")
    
    if not check_prerequisites():
        log_message("Prerequisites check failed. Aborting installation.", "ERROR")
        return False

    # Add Prometheus Community Helm repository
    log_message("Adding prometheus-community repository...")
    success, _ = run_command(
        "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts",
        "Failed to add prometheus-community repository."
    )
    if not success:
        return False

    # Update Helm repositories
    log_message("Updating Helm repositories...")
    success, _ = run_command("helm repo update", "Failed to update Helm repositories.")
    if not success:
        return False

    # Path to custom values file
    custom_values_path = os.path.join(script_dir, 'custom-values.yaml')
    if not os.path.exists(custom_values_path):
        log_message(f"Custom values file not found at {custom_values_path}", "ERROR")
        return False
        
    log_message(f"Using custom values from: {custom_values_path}")

    # Install or upgrade Prometheus using Helm
    log_message("Installing/upgrading Prometheus...")
    success, _ = run_command(
        f"helm upgrade --install prometheus prometheus-community/kube-prometheus-stack --create-namespace -n {namespace} -f {custom_values_path}",
        "Failed to install or upgrade Prometheus.",
        timeout=600  # 10 minutes timeout for the installation
    )
    if not success:
        return False

    log_message(f"Prometheus installed or upgraded successfully in the {namespace} namespace!", "SUCCESS")
    return True

if __name__ == "__main__":
    start_time = time.time()
    try:
        success = install_or_upgrade_prometheus()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        log_message("Installation interrupted by user", "ERROR")
        sys.exit(1)
    except Exception as e:
        log_message(f"Unexpected error: {str(e)}", "ERROR")
        sys.exit(1)