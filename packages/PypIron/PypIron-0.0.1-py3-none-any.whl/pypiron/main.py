import secrets
from functools import lru_cache

import uvicorn
from fastapi import (
    FastAPI,
    Form,
    File,
    UploadFile,
    BackgroundTasks,
    Request,
    HTTPException,
    Depends,
    status,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import RedirectResponse, PlainTextResponse

from pypiron import config
from pypiron.storage_backends import S3StorageBackend, PackageFilenameInfo
from pypiron.utils import normalize_package_name

app = FastAPI()

security = HTTPBasic()


@lru_cache()
def backend():
    return S3StorageBackend(
        s3_path=config.PACKAGES_S3_URL,
    )


@app.get("/simple/")
async def simple_packages_list():
    return RedirectResponse(backend().get_simple_index_url())


@app.get("/simple/{package_name}/")
async def simple_package_files_list(package_name):
    normalized_package_name = normalize_package_name(package_name)
    if normalized_package_name != package_name:
        return RedirectResponse(f"/simple/{normalized_package_name}/", status_code=301)

    return RedirectResponse(backend().get_simple_package_index_url(package_name))


@app.get("/packages/{package_name}/{filename}")
async def package_file_download(package_name, filename):
    normalized_package_name = normalize_package_name(package_name)
    if normalized_package_name != package_name:
        return RedirectResponse(f"/simple/{normalized_package_name}/", status_code=301)
    return RedirectResponse(backend().get_package_file_url(package_name, filename))


@app.post("/")
def update(
    background_tasks: BackgroundTasks,
    action: str = Form(alias=":action"),
    content: UploadFile = File(None),
    gpg_signature: UploadFile = File(None),
    credentials: HTTPBasicCredentials = Depends(security),
):
    correct_username = secrets.compare_digest(
        credentials.username, config.ADMIN_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, config.ADMIN_PASSWORD
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    if action == "file_upload":
        package_info = PackageFilenameInfo.from_filename(content.filename)
        if backend().package_file_exists(package_info.distribution, content.filename):
            raise HTTPException(status_code=409, detail="Item already uploaded")

        if gpg_signature:
            if content.filename[:-3] != gpg_signature.filename[:-3]:
                raise HTTPException(
                    status_code=400, detail="Signature filename doesn't match."
                )

        background_tasks.add_task(
            backend().upload_package,
            filename=content.filename,
            file_obj=content.file,
            signature_filename=gpg_signature.filename if gpg_signature else None,
            signature_file_obj=gpg_signature.file if gpg_signature else None,
        )


#
# @app.api_route("/{full_path:path}")
# async def catch_all(request: Request, full_path: str):
#     """For debugging"""
#     print("full_path: " + full_path)
#     return PlainTextResponse("OK")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
