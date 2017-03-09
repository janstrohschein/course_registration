import xlsxwriter
#from xlsxwriter import Workbook, worksheet
from collections import OrderedDict
import re
from io import BytesIO

class ExcelWriter():
    """

    """
    def __init__(self):
        """

        :return:
        """
        # creates a file object you can write information to
        self.output = BytesIO()
        # creates an excel workbook, using the StringIO object as the file
        self.out_wb = xlsxwriter.Workbook(self.output, {'constant_memory': True})
        self.curr_row = 0
        self.bold = self.out_wb.add_format({'bold': True})

    def write_student_list(self, course, field_list, student_list):
        """

        :param course:
        :param field_list:
        :param student_list:
        :return:
        """

        ws = self.out_wb.add_worksheet('Übersicht')
        ws.set_column('A:N', 12)

        row = []
        for field in field_list:
            row.append(field)

        ws.write_row(self.curr_row, 0, row, self.bold)
        self.curr_row += 1

        for key, student in student_list.items():
            row = []

            for item in student.items():
                row.append(item[1])

            ws.write_row(self.curr_row, 0, row)
            self.curr_row += 1


