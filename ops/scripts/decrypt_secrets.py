from commons import meta, crypto
import json

print(f"Decrypting {meta.current_env()} env secrets...")
secrets = crypto.decrypted_secrets()
print()
print("Decrypted secrets:")
print(json.dumps(secrets, indent=2))

