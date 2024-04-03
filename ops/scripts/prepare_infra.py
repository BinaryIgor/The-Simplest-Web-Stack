import requests
from os import environ
import sys
import time

USER_PLACEHOLDER = "_user_placeholder_"

DROPLETS_RESOURCE = "droplets"
FIREWALLS_RESOURCE = "firewalls"
VOLUMES_RESOURCE = "volumes"

ID = "id"
NAME = "name"

SSH_KEY_FINGERPRINTS = ["a0:3a:d4:d8:52:4a:8b:34:50:fd:20:c7:19:a1:8a:b4"]

# Customize this params for your needs
# full machine slugs reference: https://slugs.do-api.dev/
MACHINE_SLUG = "s-1vcpu-2gb-amd"
REGION = "fra1"

MACHINE_NAME = "the-simplest-stack-machine"
# db volume name needs to be synchronized, if changed!
DB_VOLUME_NAME = "db-volume"
DB_VOLUME_SIZE = 10

FIREWALL_NAME = f"{MACHINE_NAME}-firewall"

IMAGE = "ubuntu-22-04-x64"

# used also in deploy/other scripts - be careful with changing!
MACHINE_USER = "deploy"

DIGITAL_OCEAN_API_URL = "https://api.digitalocean.com/v2"

def print_and_exit(message):
    print(message)
    sys.exit(1)

API_TOKEN = environ.get("DO_API_TOKEN")
if API_TOKEN is None:
    print_and_exit("DO_API_TOKEN env variable needs to be supplied with valid digital ocean token")

if len(SSH_KEY_FINGERPRINTS) == 0:
    print_and_exit("SSH_KEY_FINGERPRINTS can't be empty. Without them, you will not have access to created machines!")

AUTH_HEADER = {"Authorization": f"Bearer {API_TOKEN}"}

with open("init_machine.bash") as f:
    INIT_MACHINE = f.read().replace(USER_PLACEHOLDER, MACHINE_USER)


# To debug user data, run:
# cat /var/log/cloud-init-output.log | grep userdata
# ...on the droplet
MACHINE_CONFIG = {
    "name": MACHINE_NAME,
    "region": REGION,
    "size": MACHINE_SLUG,
    "image": IMAGE,
    "ssh_keys": SSH_KEY_FINGERPRINTS,
    "backups": False,
    "ipv6": True,
    "monitoring": True,
    "user_data": INIT_MACHINE
}

DB_VOLUME_CONFIG = {
    "name": DB_VOLUME_NAME,
    "size_gigabytes": DB_VOLUME_SIZE,
    "region": REGION,
    "filesystem_type": "ext4"
}

FIREWALL_ALL_ADDRESSES =  {
    "addresses": [
        "0.0.0.0/0",
        "::/0"
    ]
}
FIREWALL_CONFIG = {
    "name": FIREWALL_NAME,
    "inbound_rules": [
        {
            "protocol": "icmp",
            "ports": "0",
            "sources": FIREWALL_ALL_ADDRESSES
        },
        {
            "protocol": "tcp",
            "ports": "22",
            "sources": FIREWALL_ALL_ADDRESSES
        },
        {
            "protocol": "tcp",
            "ports": "80",
            "sources": FIREWALL_ALL_ADDRESSES
        },
        {
            "protocol": "tcp",
            "ports": "443",
            "sources": FIREWALL_ALL_ADDRESSES
        }
    ],
    "outbound_rules": [
        {
            "protocol": "tcp",
            "ports": "0",
            "destinations": FIREWALL_ALL_ADDRESSES
        },
        {
            "protocol": "udp",
            "ports": "0",
            "destinations": FIREWALL_ALL_ADDRESSES
        },
        {
            "protocol": "icmp",
            "ports": "0",
            "destinations": FIREWALL_ALL_ADDRESSES
        }
    ]
}

def get_resources(resource):
    response = requests.get(f'{DIGITAL_OCEAN_API_URL}/{resource}', headers=AUTH_HEADER)
    response.raise_for_status()
    return response.json()[resource]


def create_resource(path, resource, data):
    response = requests.post(f'{DIGITAL_OCEAN_API_URL}/{path}', headers=AUTH_HEADER, json=data)
    if not response.ok:
        print_and_exit(f'''Fail to create {resource}!
        Code: {response.status_code}
        Body: {response.text}''')

    return response.json()[resource]

def create_droplets_if_needed():
    droplet_names_ids = {}

    for d in get_resources(DROPLETS_RESOURCE):
        d_name = d[NAME]
        if d_name == MACHINE_NAME:
            droplet_names_ids[MACHINE_NAME] = d[ID]

    # Eventual consistency of Digital Ocean: sometimes new droplets are not visible immediately after creation
    new_droplet_names = []

    if MACHINE_NAME in droplet_names_ids:
        print(f"{MACHINE_NAME} exists, skipping its creation!")
    else:
        new_droplet_names.append(MACHINE_NAME)
        print(f"Creating {MACHINE_NAME}...")
        created_droplet = create_resource(DROPLETS_RESOURCE, "droplet", MACHINE_CONFIG)
        droplet_names_ids[MACHINE_NAME] = created_droplet[ID]
        print(f"{MACHINE_NAME} created!")

    if len(new_droplet_names) == 0:
        return droplet_names_ids

    print()

    while True:
        for d in get_resources(DROPLETS_RESOURCE):
            d_status = d['status']
            d_name = d[NAME]
            if d_status == 'active' and d_name in new_droplet_names:
                new_droplet_names.remove(d_name)

        if new_droplet_names:
            print(f"Waiting for {new_droplet_names} droplets to become active...")
            time.sleep(5)
        else:
            print()
            print("All droplets are active!")
            print()
            break

    return droplet_names_ids

def create_and_attach_db_volume_if_needed(droplet_names_ids):
    volume_exists = False
    volume_attached = False
    machine_droplet_id = droplet_names_ids[MACHINE_NAME]
    for v in get_resources(VOLUMES_RESOURCE):
        if v[NAME] == DB_VOLUME_NAME:
            volume_exists = True
            attached_to_droplets = v["droplet_ids"]
            volume_attached = machine_droplet_id in attached_to_droplets
            break

    if volume_exists:
        print("Volume exists, skipping its creation!")
    else:
        print("Creating volume...")
        create_resource(VOLUMES_RESOURCE, "volume", DB_VOLUME_CONFIG)
        print("Volume created!")
        time.sleep(1)

    if not volume_attached:
        print("Volume not attached, attaching it!")
        attach_volume(machine_droplet_id)
        print("Volume attached!")


def attach_volume(droplet_id):
    response = requests.post(f'{DIGITAL_OCEAN_API_URL}/{VOLUMES_RESOURCE}/actions', headers=AUTH_HEADER, json={
        "type": "attach",
        "volume_name": DB_VOLUME_NAME,
        "droplet_id": droplet_id
    })
    if not response.ok:
        print_and_exit(f'''Fail to attach volume!
        Code: {response.status_code}
        Body: {response.text}''')

def create_and_assign_firewall_if_needed(droplet_names_ids):
    firewall_id = None
    assigned_droplet_ids = []
    for f in get_resources(FIREWALLS_RESOURCE):
        if f[NAME] == FIREWALL_NAME:
            firewall_id = f[ID]
            assigned_droplet_ids = f["droplet_ids"]
            break


    if firewall_id:
        print("Firewall exists, skipping its creation!")
    else:
        print("Firewall does not exist, creating it..")
        created_firewall = create_resource(FIREWALLS_RESOURCE, "firewall", FIREWALL_CONFIG)
        firewall_id = created_firewall[ID]
        print("Firewall created!")
        time.sleep(1)

    droplet_ids = droplet_names_ids.values()
    to_assign_droplet_ids = [did for did in droplet_ids if did not in assigned_droplet_ids]

    if len(to_assign_droplet_ids) > 0:
        print(f"{len(to_assign_droplet_ids)} droplets are not assinged to firewall, assigning them...")
        assign_firewall(firewall_id, to_assign_droplet_ids)
        print("Droplets assigned!")
    else:
        print("Droplets are assigned to firewalls already!")


def assign_firewall(firewall_id, droplet_ids):
    response = requests.post(f'{DIGITAL_OCEAN_API_URL}/{FIREWALLS_RESOURCE}/{firewall_id}/{DROPLETS_RESOURCE}',
                             headers=AUTH_HEADER,
                             json={ "droplet_ids": droplet_ids })
    if not response.ok:
        print_and_exit(f'''Fail to assign firewall to droplets!
        Code: {response.status_code}
        Body: {response.text}''')


print("Needed droplets:")
print(f"Machine: {MACHINE_SLUG}")
print()

print("Creating droplets, if needed...")

droplet_names_ids = create_droplets_if_needed()
print()
print("...")
print()
time.sleep(1)

print("Droplets prepared, creating and attaching volume if needed...")

create_and_attach_db_volume_if_needed(droplet_names_ids)
print()
print("...")
print()
time.sleep(1)

print("Volume created and attached, creating and assigning firewall if needed...")

create_and_assign_firewall_if_needed(droplet_names_ids)
print()
print("...")
print()

print("Everything should be ready!")
print()
print("Get your machine addresses from DigitalOcean UI and start experimenting!")