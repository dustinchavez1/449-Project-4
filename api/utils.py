import logging.config
import base64
import hashlib
import secrets


def get_logger():
    return logging.getLogger(__name__)


ALGORITHM = "pbkdf2_sha256"


def hash_password(password, salt=None, iterations=260000):
    if salt is None:
        salt = secrets.token_hex(16)
    assert salt and isinstance(salt, str) and "$" not in salt
    assert isinstance(password, str)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
    return "{}${}${}${}".format(ALGORITHM, iterations, salt, b64_hash)


def verify_password(password, password_hash):
    if (password_hash or "").count("$") != 3:
        return False
    algorithm, iterations, salt, b64_hash = password_hash.split("$", 3)
    iterations = int(iterations)
    assert algorithm == ALGORITHM
    compare_hash = hash_password(password, salt, iterations)
    return secrets.compare_digest(password_hash, compare_hash)


def join(data1, data2, key1, key2):
    result = []

    for record1 in data1:
        for record2 in data2:
            if record1[key1] == record2[key2]:
                # Create a new record by combining fields from both records
                new_record = {**record1, **record2}
                result.append(new_record)

    return result