import io
import json
import os
import re
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
DEFAULT_CREDENTIALS_PATH = "credentials.json"
DEFAULT_TOKEN_PATH = "token.json"
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


def get_drive_service(
    credentials_path: Optional[str] = None,
    token_path: str = DEFAULT_TOKEN_PATH,
):
    """
    Google Drive API v3 서비스 객체를 생성하여 반환합니다.
    - 서비스 계정 키(type == "service_account")와 OAuth 클라이언트 ID(installed/web)를 모두 자동 감지하여 지원합니다.
    """
    cred_file = (
        credentials_path
        or os.environ.get("GDRIVE_CREDENTIALS")
        or DEFAULT_CREDENTIALS_PATH
    )

    if not os.path.exists(cred_file):
        raise FileNotFoundError(
            f"Google Drive 인증 파일('{cred_file}')을 찾을 수 없습니다.\n"
            "Google Cloud Console에서 OAuth 2.0 클라이언트 ID 또는 서비스 계정 JSON 키를 발급받아 "
            f"'{cred_file}' 경로에 저장하거나 --credentials 옵션으로 경로를 지정해주세요."
        )

    with open(cred_file, "r", encoding="utf-8") as f:
        cred_data = json.load(f)

    # 1. 서비스 계정(Service Account) 키인 경우
    if cred_data.get("type") == "service_account":
        creds = service_account.Credentials.from_service_account_file(
            cred_file, scopes=SCOPES
        )
        return build("drive", "v3", credentials=creds)

    # 2. OAuth 2.0 클라이언트 ID인 경우
    creds: Optional[Credentials] = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        with open(token_path, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def _find_or_create_subfolder(service, folder_name: str, parent_id: str = "root") -> str:
    """지정한 부모 폴더 아래에서 폴더를 찾고, 없으면 새로 생성하여 폴더 ID를 반환합니다."""
    escaped_name = folder_name.replace("'", "\\'")
    query = (
        f"name = '{escaped_name}' and "
        f"'{parent_id}' in parents and "
        f"mimeType = '{FOLDER_MIME_TYPE}' and "
        f"trashed = false"
    )
    response = (
        service.files()
        .list(
            q=query,
            spaces="drive",
            fields="files(id, name)",
            pageSize=1,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
    )
    files = response.get("files", [])
    if files:
        return files[0]["id"]

    # 폴더가 존재하지 않으면 생성
    folder_metadata = {
        "name": folder_name,
        "mimeType": FOLDER_MIME_TYPE,
        "parents": [parent_id],
    }
    created = (
        service.files()
        .create(body=folder_metadata, fields="id", supportsAllDrives=True)
        .execute()
    )
    return created["id"]


def resolve_folder_spec(service, folder_spec: str) -> str:
    """
    폴더 지정 문자열(폴더 ID 또는 'NotebookLM/Lottery', 'NotebookLM > Lottery' 같은 경로)을
    해석하여 최종 대상 폴더의 Google Drive ID를 반환합니다.
    """
    # '/' 또는 '>' 구분자가 포함된 경로인 경우 단계별로 폴더 탐색/생성
    if "/" in folder_spec or ">" in folder_spec:
        parts = [p.strip() for p in re.split(r"[/\>]", folder_spec) if p.strip()]
        current_parent = "root"
        for part in parts:
            current_parent = _find_or_create_subfolder(service, part, current_parent)
        return current_parent

    # 단일 문자열인 경우: 먼저 유효한 폴더 ID인지 확인하고, 아니면 루트 하위 폴더 이름으로 간주
    try:
        meta = (
            service.files()
            .get(
                fileId=folder_spec,
                fields="id, mimeType, trashed",
                supportsAllDrives=True,
            )
            .execute()
        )
        if meta.get("mimeType") == FOLDER_MIME_TYPE and not meta.get("trashed"):
            return meta["id"]
    except HttpError:
        pass

    return _find_or_create_subfolder(service, folder_spec.strip(), "root")


def upload_text_to_drive(
    content: str,
    filename: str,
    folder_id: Optional[str] = None,
    credentials_path: Optional[str] = None,
) -> dict:
    """
    텍스트 문자열을 파일로 생성하여 Google Drive에 업로드합니다.
    동일 폴더 내에 같은 이름의 파일이 이미 있으면 내용을 업데이트합니다.

    Returns:
        dict: 업로드된 파일의 메타데이터 (id, name, webViewLink)
    """
    service = get_drive_service(credentials_path=credentials_path)

    raw_folder = folder_id or os.environ.get("GDRIVE_FOLDER_ID")
    target_folder_id = resolve_folder_spec(service, raw_folder) if raw_folder else None

    media = MediaIoBaseUpload(
        io.BytesIO(content.encode("utf-8")),
        mimetype="text/plain",
        resumable=False,
    )

    # 동일 폴더에 같은 파일명이 존재하는지 확인
    escaped_filename = filename.replace("'", "\\'")
    parent_clause = f"'{target_folder_id}' in parents" if target_folder_id else "'root' in parents"
    existing_query = f"name = '{escaped_filename}' and {parent_clause} and trashed = false"
    existing = (
        service.files()
        .list(
            q=existing_query,
            spaces="drive",
            fields="files(id, name)",
            pageSize=1,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
        .get("files", [])
    )

    if existing:
        file_id = existing[0]["id"]
        uploaded_file = (
            service.files()
            .update(
                fileId=file_id,
                media_body=media,
                fields="id, name, webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )
    else:
        file_metadata: dict = {
            "name": filename,
            "mimeType": "text/plain",
        }
        if target_folder_id:
            file_metadata["parents"] = [target_folder_id]

        uploaded_file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id, name, webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )
    return uploaded_file
