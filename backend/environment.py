import os
import sys
from dotenv import load_dotenv


load_dotenv()

def get_url() -> str:
    ats_url = os.environ.get("ATS_URL")

    host_name = os.environ.get("HOST_NAME", "https://conductor.amd.com")
    if not ats_url:
        ats_url = host_name
    return ats_url


def get_email() -> str:
    amd_email = (os.environ.get("AMD_EMAIL") or "").lower().strip()
    ats_email = (os.environ.get("ATS_EMAIL") or "").lower().strip()
    if ats_email and not amd_email:
        amd_email = ats_email
    return amd_email


def get_secret() -> str:
    return (os.environ.get("ATS_SECRET") or "").strip()


AMD_EMAIL = get_email()
ATS_EMAIL = get_email()
ATS_SECRET = get_secret()
ATS_URL = get_url()
HOST_NAME = get_url()

BOOL_STRINGS = {"true": True, "false": False}
VERIFY_CERTS = BOOL_STRINGS.get(os.environ.get("VERIFY_CERTS", "False").lower(), True)

REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 180))
