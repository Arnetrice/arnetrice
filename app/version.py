"""Build metadata surfaced in the footer and at /healthz."""
import os
from datetime import datetime, timezone


SITE_VERSION = "2.0.0"

# Captured at process start; reflects the running deployment instance.
PROCESS_STARTED_AT = datetime.now(timezone.utc).isoformat()

# Build-time stamp injected by Dockerfile ARG; "unknown" locally.
BUILD_TIMESTAMP = os.environ.get("BUILD_TIMESTAMP", "unknown")
