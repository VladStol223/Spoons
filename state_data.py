# this can be used for passing flags and states between modules.
# this file should never contain an "import"
# This is how we escape circular imports
_download_state = {
    "trigger_download": False,
    "downloading": False,
    "done": False,
    "ok": False,
    "done_started_at": None
}

