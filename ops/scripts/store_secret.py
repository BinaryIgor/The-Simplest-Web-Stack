from commons import crypto, meta
import sys

if len(sys.argv) < 2:
    meta.print_and_exit("First argument with secret name is required!")

secret_name = sys.argv[1]
print(f"About to store {secret_name} secret...")

if len(sys.argv) >= 3:
    secret_value = sys.argv[2]
else:
    print("Secret value not given, generating it...")
    if "password" in secret_name:
        secret_value = crypto.random_password()
    else:
        secret_value = crypto.random_key()

password = crypto.secret_input("Secrets encryption/decryption password: ")

print("Storing secret...")

crypto.modify_secret(secret_name, secret_value, encryption_password=password)

print()
print(f"Secret stored in {crypto.secrets_file_path()} encrypted file")