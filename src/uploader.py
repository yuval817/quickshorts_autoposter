import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from googleapiclient.errors import ResumableUploadError
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def _yt_client():
    creds = Credentials.from_authorized_user_info({
        "client_id": os.getenv("YT_CLIENT_ID"),
        "client_secret": os.getenv("YT_CLIENT_SECRET"),
        "refresh_token": os.getenv("YT_REFRESH_TOKEN"),
        "token_uri": "https://oauth2.googleapis.com/token"
    }, SCOPES)
    return build("youtube", "v3", credentials=creds)

def upload_video(path, title, description, privacy_status="public"):
    youtube = _yt_client()
    body = {
        "snippet": {"title": title, "description": description, "categoryId": "22"},
        "status": {"privacyStatus": privacy_status}
    }
    media = MediaFileUpload(path, chunksize=-1, resumable=True)

    try:
        req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
        vid = resp.get("id")
        print(f"Video uploaded: https://www.youtube.com/watch?v={vid}")
        return vid

    except (ResumableUploadError, HttpError) as e:
        msg = str(e)
        if "uploadLimitExceeded" in msg:
            print("YouTube daily upload limit reached — video rendered but not uploaded.")
            print(f"Rendered file path: {path}")
            return None
        raise
