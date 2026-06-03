import paramiko
import os


def generate_ssh_key_pair():
    """Generates an SSH key pair and returns (private_key, public_key)"""
    key = paramiko.RSAKey.generate(4096)

    # Private Key
    private_key_str = ""
    with open("/tmp/temp_private.pem", "w") as private_file:
        key.write_private_key(private_file)
    with open("/tmp/temp_private.pem", "r") as private_file:
        private_key_str = private_file.read()
    os.remove("/tmp/temp_private.pem")

    # Public Key
    public_key_str = f"{key.get_name()} {key.get_base64()}"

    return private_key_str, public_key_str
