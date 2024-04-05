from commons import crypto

old_password = crypto.secret_input("Old secrets encryption/decryption password: ")
new_password = crypto.secret_input("New secrets encryption/decryption password: ")

crypto.reencrypt_secrets(old_password, new_password)

print()
print("Secrets can be decrypted only with a new password right now!")