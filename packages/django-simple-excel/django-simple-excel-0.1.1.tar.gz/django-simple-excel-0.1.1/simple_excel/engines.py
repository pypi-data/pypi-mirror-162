from io import BytesIO

import xlsxwriter
from django.http import HttpResponse


class BaseEngine:
    def write(self, headers, body):
        raise NotImplementedError()

    def get_response(self, filename) -> HttpResponse:
        raise NotImplementedError()


class ExcelEngine(BaseEngine):
    def __init__(self):
        self.is_written = False
        # init xlsx writer
        self.buffer = BytesIO()
        self.workbook = xlsxwriter.Workbook(self.buffer, options={'remove_timezone': True})
        self.worksheet = self.workbook.add_worksheet()

    def get_response(self, filename):
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment;filename="{filename}"'
        response.write(self.get_content())

        return response

    def write(self, headers, body):
        self.write_headers(headers)
        self.write_body(body)
        self.is_written = True

    def write_headers(self, headers):
        for i, value in enumerate(headers):
            self.worksheet.write(0, i, value)

    def write_body(self, body):
        for i, row in enumerate(body, 1):
            for j, value in enumerate(row):
                self.worksheet.write(i, j, value)

    def get_content(self):
        if not self.is_written:
            raise ValueError("Excel workbook is empty, write first")
        self.workbook.close()
        return self.buffer.getvalue()
