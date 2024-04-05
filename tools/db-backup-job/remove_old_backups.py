import os

backups_path = os.environ.get("BACKUPS_PATH", "/tmp/db-backups")
max_backups = int(os.environ.get("MAX_BACKUPS", "10"))

backups = sorted(os.listdir(backups_path))

to_remove = len(backups) - max_backups
if to_remove > 0:
    print(f"Max number of backups ({max_backups}) was reached, removing the oldest ones...")
    to_remove_backups = backups[0:to_remove]
    for b in to_remove_backups:
        b_to_remove = os.path.join(backups_path, b)
        print(f"Removing {b_to_remove} backup...")
        os.remove(b_to_remove)
    print()
    print(f"Oldest {to_remove_backups} backups were removed")
else:
    print(f"No need to remove backups, since we have {len(backups)} and {max_backups} are allowed")
