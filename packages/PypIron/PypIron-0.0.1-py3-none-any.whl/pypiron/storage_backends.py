import re
from dataclasses import dataclass, fields
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

from pypiron.index_gen import (
    generate_global_package_index,
    generate_package_files_index,
)
from pypiron.utils import normalize_package_name

_PACKAGE_FILENAME_RE = re.compile(
    r"^(?P<distribution>.+?)-(?P<version>\d.*?)"
    r"(-(?P<build_tag>\d.*?))?"
    r"-(?P<python_version>.+?)"
    r"-(?P<abi>.+?)"
    r"-(?P<platform>.+?)"
    r"\.(?P<extension>whl|asc|tar\.gz)$"
)


@dataclass
class PackageFilenameInfo:
    distribution: str
    version: str
    build_tag: str
    python_version: str
    abi: str
    platform: str
    extension: str

    @classmethod
    def from_filename(cls, filename):
        m = _PACKAGE_FILENAME_RE.search(filename)
        if m:
            kwargs = {f.name: m.group(f.name) for f in fields(cls)}
            kwargs["distribution"] = normalize_package_name(kwargs["distribution"])
            return cls(**kwargs)


class StorageBackendError(Exception):
    pass


class PackageFileExistsError(StorageBackendError):
    pass


class S3StorageBackend:
    INDEX_FILENAME = "__index.html"

    def __init__(self, s3_path, aws_access_key_id=None, aws_secret_access_key=None):
        s3_url_parts = urlparse(s3_path)
        self.s3_bucket = s3_url_parts.hostname
        self.s3_prefix = ""

        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key

        self._s3_client = None

    def s3(self):
        if self._s3_client is None:
            self._s3_client = boto3.client(
                "s3",
                aws_access_key_id=self._aws_access_key_id,
                aws_secret_access_key=self._aws_secret_access_key,
            )

        return self._s3_client

    def _get_signed_url(self, path):
        return self.s3().generate_presigned_url(
            "get_object", Params={"Bucket": self.s3_bucket, "Key": path}
        )

    def _upload_file(self, path, file_obj, content_type=""):
        self.s3().put_object(
            Body=file_obj, Bucket=self.s3_bucket, Key=path, ContentType=content_type
        )

    def _file_exists(self, path):
        try:
            self.s3().head_object(Bucket=self.s3_bucket, Key=path)
            return True
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "404":
                return False
            raise

    def _list_dirs(self, path):
        paginator = self.s3().get_paginator("list_objects_v2")

        for result in paginator.paginate(
            Bucket=self.s3_bucket, Prefix=path, Delimiter="/"
        ):
            for prefix in result.get("CommonPrefixes"):
                yield prefix.get("Prefix").strip("/").split("/")[-1]

    def _list_files(self, path):
        paginator = self.s3().get_paginator("list_objects_v2")

        for result in paginator.paginate(Bucket=self.s3_bucket, Prefix=path):
            for key in result.get("Contents"):
                path = key.get("Key")
                if path.endswith("__index.html"):
                    continue
                yield "/" + path

    def package_file_exists(self, package_name, filename):
        path = f"packages/{package_name}/{filename}"
        return self._file_exists(path)

    def list_packages(self):
        return list(self._list_dirs(f"packages/"))

    def list_package_distributions(self, package_name):
        pkg_prefix = f"packages/{package_name}"
        return [f.split("/")[-1] for f in self._list_files(pkg_prefix)]

    def get_simple_index_url(self):
        return self._get_signed_url(f"packages/{self.INDEX_FILENAME}")

    def get_simple_package_index_url(self, package_name):
        return self._get_signed_url(f"packages/{package_name}/{self.INDEX_FILENAME}")

    def get_package_file_url(self, package_name, filename):
        return self._get_signed_url(f"packages/{package_name}/{filename}")

    def upload_package(
        self, filename, file_obj, signature_filename, signature_file_obj
    ):
        filename_info = PackageFilenameInfo.from_filename(filename)
        if not filename_info:
            return

        self._upload_file(
            path=f"packages/{filename_info.distribution}/{filename}", file_obj=file_obj
        )
        if signature_file_obj and signature_filename:

            self._upload_file(
                path=f"packages/{filename_info.distribution}/{signature_filename}",
                file_obj=signature_file_obj,
            )

        self._update_package_files_index(filename_info.distribution)

        self._update_global_package_index()

    def _update_package_files_index(self, package_name):
        paths = [
            f"/packages/{package_name}/{p}"
            for p in self.list_package_distributions(package_name)
        ]
        index_html = generate_package_files_index(package_name, paths)
        self._upload_file(
            path=f"packages/{package_name}/{self.INDEX_FILENAME}",
            file_obj=index_html,
            content_type="text/html",
        )

    def _update_global_package_index(self):
        index_html = generate_global_package_index(self.list_packages())
        self._upload_file(
            path=f"packages/{self.INDEX_FILENAME}",
            file_obj=index_html,
            content_type="text/html",
        )
