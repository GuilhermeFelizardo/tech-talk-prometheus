import subprocess

def run_command(command, error_message):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    if process.returncode != 0:
        print(error_message)
        print(f"Error details: {err.decode('utf-8')}")
        return False
    return True

def install_reflector():
    if not run_command("helm repo add emberstack https://emberstack.github.io/helm-charts", "Error adding Emberstack repository."):
        return

    if not run_command("helm repo update", "Error updating Helm repositories."):
        return

    if not run_command("helm install reflector emberstack/reflector --namespace kube-system", "Error installing Reflector with Helm."):
        return

    print("Reflector installed successfully!")

if __name__ == "__main__":
    install_reflector()