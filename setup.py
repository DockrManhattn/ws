import os
import shutil

def ensure_local_bin_exists():
    local_bin_path = os.path.expanduser("~/.local/bin")
    if not os.path.exists(local_bin_path):
        print(f"Directory {local_bin_path} does not exist. Creating it...")
        os.makedirs(local_bin_path)
        print(f"Directory {local_bin_path} has been created.")
    else:
        print(f"Directory {local_bin_path} already exists.")
    return local_bin_path

def copy_ws_to_local_bin():
    source_file = os.path.join(os.getcwd(), "ws.py")
    local_bin_path = ensure_local_bin_exists()
    destination_file = os.path.join(local_bin_path, "ws.py")
    try:
        shutil.copy(source_file, destination_file)
        print(f"Copied {source_file} to {destination_file}")
        os.chmod(destination_file, 0o755)
        print(f"Set executable permissions for {destination_file}")
    except FileNotFoundError:
        print(f"Error: {source_file} not found. Make sure it exists in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_shell_config_file():
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return os.path.expanduser("~/.zshrc")
    elif "bash" in shell:
        return os.path.expanduser("~/.bashrc")
    else:
        print("Unknown shell. Alias will not be added.")
        return None

def add_alias_to_shell_config():
    shell_config_file = get_shell_config_file()
    if not shell_config_file:
        return

    alias_command = "alias ws='python3 ~/.local/bin/ws.py'"
    try:
        with open(shell_config_file, "r") as file:
            config_content = file.read()
        
        # Check if the alias already exists
        if alias_command in config_content:
            print(f"The alias is already present in {shell_config_file}.")
            return
        
        # Add the alias to the config file
        with open(shell_config_file, "a") as file:
            file.write(f"\n{alias_command}\n")
        print(f"Alias added to {shell_config_file}.")
    except FileNotFoundError:
        print(f"{shell_config_file} not found. Creating a new one and adding the alias.")
        with open(shell_config_file, "w") as file:
            file.write(f"{alias_command}\n")
        print(f"Alias added to {shell_config_file}.")
    except Exception as e:
        print(f"An error occurred while adding the alias: {e}")

if __name__ == "__main__":
    copy_ws_to_local_bin()
    add_alias_to_shell_config()
