import uuid

def generate_uuid():
    """
    Generate a new UUID string.

    Returns:
        str: A UUID string used as the primary key for files or folders.
    
    Example:
        >>> from utils.idgen import generate_uuid
        >>> file_id = generate_uuid()
        >>> print(file_id)
    """
    return str(uuid.uuid4())

# Uncomment the lines below to generate a sample UUID for testing
# sample_id = generate_uuid()
# print(sample_id)
