import logging
import os
import re

from fastapi import APIRouter
from fastapi.responses import JSONResponse

LOG = logging.getLogger(__name__)


router = APIRouter(
    prefix="/version",
    tags=["version"],
)
"""
Place the version file of the application in the same directory where the app.py is located.
The version file does not need any extention.
It should only contaion the version on the first line in this format: 0.0.1
"""
current_version = None
try:
    current_file_dir = os.path.dirname(os.path.realpath("__file__"))
    version_file = os.path.join(current_file_dir, "version")
    LOG.info(f"version file path: {version_file}")
    lines = []
    with open(version_file) as f:
        lines = f.readlines()
    first_line = lines[0]
    pattern = re.compile("([0-9]+\.){2}([0-9]+)")
    m = re.match(pattern, first_line)
    if m:
        current_version = m.group(0)
        LOG.info(f"Version file has been read and version is set to {current_version}")
    else:
        LOG.error("Could not read version file")
except Exception as ex:
    LOG.error("Could not read version file")


@router.get("")
async def get_version():
    LOG.info(f"The current version is {current_version}")
    return JSONResponse(content={"version": current_version})
