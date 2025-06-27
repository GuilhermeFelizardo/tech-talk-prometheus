import subprocess
import os

def run_command(command, error_message):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError:
        print(error_message)
        return False
    return True

def install_nginx_ingress():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    custom_values_path = os.path.join(script_dir, 'custom-values.yaml')

    # Add the nginx-stable repository
    if not run_command("helm repo add nginx-stable https://helm.nginx.com/stable", "Error adding the nginx-stable repository."):
        return

    # Update Helm repositories
    if not run_command("helm repo update", "Error updating Helm repositories."):
        return

    # Install NGINX Ingress Controller
    if not run_command(f"helm upgrade --install nginx-ingress nginx-stable/nginx-ingress --namespace nginx-ingress --create-namespace -f {custom_values_path}", "Error installing NGINX Ingress Controller with Helm."):
        return

    print("NGINX Ingress Controller installed successfully.")

if __name__ == "__main__":
    install_nginx_ingress()