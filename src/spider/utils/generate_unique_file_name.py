import os
import uuid


def generate_unique_file_name(instance, filename):
    # Use a unique filename to prevent overwriting existing files
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(f"uploads/", filename)
