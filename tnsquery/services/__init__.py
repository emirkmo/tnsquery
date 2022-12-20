"""Services for tnsquery."""
from tnsquery.services.tns import (
    TNSAPI,
    TNSURL,
    TNSBot,
    fetch_tns_transient,
    fetch_tns_transients,
)

__all__ = ["fetch_tns_transient", "fetch_tns_transients", "TNSAPI", "TNSBot", "TNSURL"]
