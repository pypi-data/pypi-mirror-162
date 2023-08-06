from openpyxl import load_workbook
from argparse import ArgumentParser
from pathlib import Path

from correct_hours.report_processors.myob import MyobReportProcessor
from correct_hours.report_processors.xero import XeroReportProcessor

parser = ArgumentParser()
parser.add_argument("directory", help="Location of Excel files", type=str)
parser.add_argument(
    "-t",
    "--report-type",
    dest="report_type",
    help="Report type",
    type=str,
    default="xero",
    choices=['xero', 'myob']
)

args = parser.parse_args()
directory = args.directory
report_type = args.report_type


def get_new_file_name(filepath):
    path = Path(filepath)
    return f"{path.parent.absolute()}/output/copy_{path.name}"


class InvalidReportType(Exception):
    pass


# create output folder
Path(f"{directory}/output").mkdir(parents=True, exist_ok=True)
files = Path(directory).glob('*')
for f in files:
    if f.is_file():
        if not str.startswith(f.name, "~"):
            filepath = f.absolute()
            print(f"Processing file {filepath}...")
            workbook = load_workbook(filename=filepath)
            if report_type == 'xero':
                processor = XeroReportProcessor(workbook)
            elif report_type == 'myob':
                processor = MyobReportProcessor(workbook)
            else:
                raise InvalidReportType(f"Invalid report type provided: {report_type}")
            processor.process()
            new_file_name = get_new_file_name(filepath)
            workbook.save(filename=new_file_name)
            print(f"Finished processing file. Created file {new_file_name}.")
