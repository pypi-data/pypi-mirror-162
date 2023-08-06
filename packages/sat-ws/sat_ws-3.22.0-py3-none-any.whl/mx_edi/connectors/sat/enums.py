import enum


class DownloadType(enum.Enum):
    """Helper to select the download type"""

    ISSUED = "RfcEmisor"
    RECEIVED = "RfcReceptor"


class RequestType(enum.Enum):
    """Helper to select the request type"""

    CFDI = "CFDI"
    METADATA = "Metadata"
