import enum

# https://github.com/transmission/transmission/blob/main/libtransmission/transmission.h

class TR_STATUS(enum.IntEnum):
    STOPPED = 0        # Torrent is stopped
    CHECK_WAIT = 1     # Queued to check files
    CHECK = 2          # Checking files
    DOWNLOAD_WAIT = 3  # Queued to download
    DOWNLOAD = 4       # Downloading
    SEED_WAIT = 5      # Queued to seed
    SEED = 6           # Seeding
