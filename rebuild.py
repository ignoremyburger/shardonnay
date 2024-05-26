from base64 import b64decode
import json
from hashlib import sha256, md5
import sys
import os
import cryptocode

file_id = input("[?] > File ID: ").strip()
password = input("[?] > Password: ")

key = md5(password.encode()).hexdigest()

with open(f'instruction-{file_id}.json', 'r') as json_file:
    instruction = json.load(json_file)

file_checksum = instruction['checksum']

original_b64 = ""

print("[!] > Rebuilding")

for i in instruction['map']:
    print(f"\r[!] > Appending shard {i['shard_id']}", end="", flush=True)
    shard_checksum = i['checksum']
    with open(os.path.join(file_id + "-shards", f'{i["shard_id"]}.txt'), 'r') as shard_file:
        shard_content = cryptocode.decrypt(shard_file.readline(), key)
        # Check the integrity
        file_intact = sha256(shard_content.encode()).hexdigest() == shard_checksum
        if file_intact:
            original_b64 += shard_content
        else:
            print(f"[!] > Shard {i['shard_id']} has a checksum error")
            sys.exit()

print("\n")

with open(f'{instruction["file_name"]}.{instruction["file_ext"]}', 'wb') as original_image_file:
    assembled_bytes = b64decode(original_b64)
    if sha256(assembled_bytes).hexdigest() != file_checksum:
        print("[!] > File integrity is not ensured")
        sys.exit()
    original_image_file.write(assembled_bytes)
    print("Success!")