from enum import StrEnum


class ProcessingJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingJobType(StrEnum):
    EXTRACT_TEXT = "extract_text"
    GENERATE_THUMBNAIL = "generate_thumbnail"
