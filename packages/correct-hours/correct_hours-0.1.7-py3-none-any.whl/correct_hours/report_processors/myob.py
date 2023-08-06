from correct_hours.report_processors.types import UnsupportedReportType


class MyobReportProcessor:

    def __init__(self, workbook):
        self.workbook = workbook

    def process(self):
        raise UnsupportedReportType("myob")
    