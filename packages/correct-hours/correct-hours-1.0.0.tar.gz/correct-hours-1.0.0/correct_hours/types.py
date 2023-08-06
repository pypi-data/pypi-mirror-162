import dataclasses
from datetime import datetime

RATES_FILENAME = "rates.xlsx"
OUTPUT_FOLDER = "output"
HOURS_NEW_FILE_PREFIX = "copy_"


class CorrectHoursError(Exception):
    pass


@dataclasses.dataclass
class UnsupportedReportType(CorrectHoursError):
    report_type: str

    def __str__(self) -> str:
        return f"Report not supported: {self.report_type}"


@dataclasses.dataclass
class RateNotFound(CorrectHoursError):
    rate_label: str
    date: datetime

    def __str__(self) -> str:
        return (
            f"Rate not found for label \"{self.rate_label}\" and date \"{self.date.date()}\". "
            "Make sure the rates file has an entry for this combination. "
            "Also make sure the entry in the rate file doesn't have any trailing spaces."
        )


@dataclasses.dataclass
class RateFileNotFound(CorrectHoursError):
    rate_filePath: str

    def __str__(self) -> str:
        return (
            f"Rate file not found in this location: \"{self.rate_filePath}\". "
            f"Please make sure you have a file \"{RATES_FILENAME}\" in the same directory where your "
            f"reports are located."
        )


@dataclasses.dataclass
class InvalidReportType(CorrectHoursError):
    report_type: str

    def __str__(self):
        return f"Invalid report type provided: {self.report_type}"
