from base64 import b64encode
import uuid
from hashlib import sha256, md5
import textwrap
import json
import os
import cryptocode

# Get user input
file_name = input("[?] > Filename: ")
password = input("[?] > Password: ")

key = md5(password.encode()).hexdigest()

print("[!] > Loading file")

with open(file_name, 'rb') as test_file_read:
    # Check if another shard already exists
    file_content = test_file_read.read()
    file_checksum = sha256(file_content).hexdigest()
    file_unique_id = md5(file_checksum.encode()).hexdigest()
    print("[!] > File checksum: " + file_checksum)
    content = b64encode(file_content).decode()
    recommended_shard_size = (len(content) - (len(content) % 100)) / 100
    chunk_size = int(input(f'[?] > Chunk size (recommended chunk size: {recommended_shard_size}): '))
    print("[!] > Generating config")
    shard_config = {
        "file_id": file_unique_id,
        "file_ext": file_name.split('.')[-1],
        "file_name": file_name.split('.')[0]
    }

print("[!] > Deleting original")
os.remove(file_name)

shard_config['checksum'] = file_checksum
    
print("[!] > Dicing")
sharded_content = textwrap.wrap(content, chunk_size)

shard_config.update({
    "map": []
})

# Create a shard folder
print("[!] > Creating a folder")
os.mkdir(f"{file_unique_id}-shards")

print("[!] > Sharding")
current_shard = 0
for content in sharded_content:
    current_shard += 1
    shard_id = str(uuid.uuid4())
    shard_checksum = sha256(content.encode()).hexdigest()
    with open(f'{file_unique_id}-shards/{shard_id}.txt', 'w') as shard:
        shard.write(cryptocode.encrypt(content, key))
    shard_config['map'].append({
        "shard_id": shard_id,
        "checksum": shard_checksum
    })
    print(f"\r[!] > Shard {shard_id} created ({current_shard}/{len(sharded_content)})", end="", flush=True)

print("\n")

with open(f"instruction-{file_unique_id}.json", "w") as json_file:
    json.dump(shard_config, json_file, indent=4, ensure_ascii=False)

print(f"[!] > Sharding complete. Use this file ID to rebuild your file: {file_unique_id}")