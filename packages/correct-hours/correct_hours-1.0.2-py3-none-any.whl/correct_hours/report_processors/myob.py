from openpyxl import Workbook

from correct_hours.types import UnsupportedReportType


class MyobReportProcessor:

    def __init__(self, workbook: Workbook) -> None:
        self.workbook = workbook

    def process(self) -> None:
        raise UnsupportedReportType("myob")
    