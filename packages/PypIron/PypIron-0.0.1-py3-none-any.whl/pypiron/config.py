import logging
import random
import os
import string

logger = logging.getLogger(__name__)

# example: s3://my-python-packages-zmckxpo (only bucket currently used)

AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)

PACKAGES_S3_URL = os.getenv("PYPIRON_PACKAGES_S3_URL", None)
ADMIN_USERNAME = os.getenv("PYPIRON_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("PYPIRON_ADMIN_PASSWORD", None)
ADMIN_PASSWORD_GENERATED = False

if ADMIN_PASSWORD is None:
    letters = string.ascii_uppercase
    r = random.Random()
    # deterministic so we get the same password across processes
    r.seed(f"{AWS_ACCESS_KEY_ID}+{AWS_SECRET_ACCESS_KEY}+{PACKAGES_S3_URL}", version=2)
    ADMIN_PASSWORD = "".join(r.choice(letters) for i in range(50))
    ADMIN_PASSWORD_GENERATED = True
    logger.warning(
        f"*** Generated password (you should set your own): {ADMIN_PASSWORD}"
    )
