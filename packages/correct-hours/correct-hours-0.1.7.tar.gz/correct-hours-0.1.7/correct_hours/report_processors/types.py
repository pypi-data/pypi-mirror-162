
class UnsupportedReportType(Exception):

    def __init__(self, report_type):
        self.report_type = report_type

    def __str__(self):
        return f"Report not supported: {self.report_type}"
