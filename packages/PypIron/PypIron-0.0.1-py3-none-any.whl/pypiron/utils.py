import re

PACKAGE_NAME_NORMALIZE_PATTERN = re.compile(r"[-_.]+")

# https://peps.python.org/pep-0426/#name
VALID_NORMALIZED_PACKAGE_NAME_PATTERN = re.compile(
    r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$", flags=re.IGNORECASE
)


def normalize_package_name(name):
    normalized_name = PACKAGE_NAME_NORMALIZE_PATTERN.sub("-", name).lower()
    if not VALID_NORMALIZED_PACKAGE_NAME_PATTERN.match(normalized_name):
        raise ValueError("Invalid project name")
    return normalized_name
