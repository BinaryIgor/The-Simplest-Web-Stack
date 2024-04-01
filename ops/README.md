# Automation of all kinds of operations

## Setup env
```
cd scripts
bash set_up_scripts_env.bash
```

This will create virtual Python environment and install required dependencies (mostly requests for making http requests).
Then, we can actually create infra; we also need to have *DigitalOcean* token with write permissions.

```
# activate venv environment
source venv/bin/activate
export DO_API_TOKEN=<your digital ocean API token>
python3 prepare_infra.py
```