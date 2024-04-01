from commons import crypto, meta
import sys

if len(sys.argv) < 2:
    meta.print_and_exit("First argument with secret name is required!")

secret_name = sys.argv[1]
print(f"About to remove {secret_name} secret...")

password = crypto.secret_input("Secrets encryption/decryption password: ")

print("Removing secret...")

crypto.modify_secret(secret_name, value=None, encryption_password=password)

print()
print(f"Secret removed from {crypto.secrets_file_path()} encrypted file")