from commons import meta, crypto
from os import path, environ

SECRETS_PATH_VAR = "SECRETS_PATH"

print(f"Decrypting {meta.current_env()} env secrets...")
secrets = crypto.decrypted_secrets()

if meta.is_current_env_local():
    local_env_file = path.join(meta.config_dir(), "local.env")
    meta.execute_bash_script(f"""
        . {local_env_file}                         
        mkdir -p ${SECRETS_PATH_VAR}
        """)

    for k, v in secrets.items():
        meta.execute_bash_script(f"""
        . {local_env_file}                         
        echo "Local env, deploying {k} secret to local ${SECRETS_PATH_VAR}..."
        echo "${v}" > "${SECRETS_PATH_VAR}/{k}.txt"
        """)

    print("...")
    print("Secrets were deployed locally!")
else:
    remote_host = environ["REMOTE_HOST"]
    secrets_path = environ[SECRETS_PATH_VAR]
    prod_env_file = path.join(meta.config_dir(), "prod.env")
    meta.execute_bash_script(f"""
    . {prod_env_file}
    ssh {remote_host} 'mkdir -p {secrets_path}' 
    """)
    for k, v in secrets.items():
        print(f"Deploying {k} secret...")
        meta.execute_bash_script(f"""
        . {prod_env_file}
        ssh {remote_host} 'echo "{v}" > "{secrets_path}/{k}.txt"'                         
        """)

    print("...")
    print("Secrets were deployed to a remote machine!")