"""
-------------------------------------------------------------------------------------------------

"""
import argparse
import csv
import json
import os
import sys

from openpyxl import load_workbook
from datetime import date, datetime

EXPLICT_COMMA_NOT_LIST = ["Query", "Condition"]


class ExcelParser:
    def __init__(self):
        pass

    @staticmethod
    def __populate_kv_dict(row, ws_hdr_keys):
        """
        This private function reads a row and create dict of this row
        with given keys ws_hdr_keys
        :param row: row to read
        :param ws_hdr_keys: keys to create dict of this row
        :return: dict of row with ws_hdr_keys keys
        """
        kv_dict = {}
        for col_number, cell in enumerate(row):
            if col_number == len(ws_hdr_keys) or ws_hdr_keys[col_number] is None:  # don't read beyond keys
                break
            if cell.value is None:  # don't add keys if value is missing..
                continue
            if col_number == 0 and isinstance(cell.value, str) and str(
                    cell.value).isspace():  # don't add keys if value is whitespaces only..
                break
            cname = ws_hdr_keys[col_number].lower()
            cvalue = cell.value
            if isinstance(cvalue, float):
                cvalue = str(int(cvalue))
            # datetime.datetime not JSON serializable?
            if isinstance(cvalue, (datetime, date)):
                cvalue = str(cvalue)  # cvalue.isoformat()

            # see if value can be converted to valid JSON
            try:
                cvalue = json.loads(cvalue)
            except:
                pass

            if isinstance(cvalue, int):
                cvalue = str(cvalue)

            # bad approach but the only way..

            if ws_hdr_keys[col_number] not in EXPLICT_COMMA_NOT_LIST and isinstance(cvalue, str) and ',' in cvalue:
                if cvalue.replace(',', '').strip() != '':
                    cvalue = [x.strip() for x in cvalue.split(',')]

            kv_dict[ws_hdr_keys[col_number]] = cvalue

        return kv_dict

    def parse(self, workbook_file, workbook_sheet='all'):
        """
        This function parse a single xlsx file file and return json
        :param workbook_file:
        :param workbook_sheet:
        :return:
        """
        (filepath, filename) = os.path.split(workbook_file)
        (filename, file_ext) = os.path.splitext(filename)
        workbook = load_workbook(filename=workbook_file, read_only=True)
        compiled_json = dict()

        for worksheet in workbook.worksheets:
            print()
            print('-' * 80)

            if workbook_sheet != 'all' and worksheet.title != workbook_sheet:
                print('Ignoring Workbook: %s, Sheet: %s' % (filename, worksheet.title))
                continue
            else:
                print('Processing Workbook: %s, Sheet: %s' % (filename, worksheet.title))

            ws_hdr_keys = []
            ws_hdr_title = ''
            ws_hdr_detected = False
            ws_row_as_keys = False
            worksheet_payload = {}

            empty_row_count = 0
            for row in worksheet.rows:
                if len(row) == 0 or row[0].value is None:  # last row in a sheet
                    empty_row_count = empty_row_count + 1
                    ws_hdr_detected = False
                    if empty_row_count == 10:
                        break
                    else:
                        continue
                elif row[0].row == 1 and row[
                    0].value != 'DocType':  # if 'DocType' is not in A1, its empty or non input type doc
                    break
                elif (ws_hdr_detected is False) and (
                        len(row) == 1 or (len(row) >= 2 and row[1].value is None)):  # headers starts from next row
                    ws_hdr_title = row[0].value
                    worksheet_payload[ws_hdr_title] = []
                    ws_hdr_detected = True
                    ws_row_as_keys = True
                    empty_row_count = 0
                    continue
                elif ws_hdr_detected is False:  # this is k,v pair BEFORE headers

                    if len(row) > 1:
                        value = row[1].value
                    else:
                        value = 'null'

                    # datetime.datetime not JSON serializable?
                    # if isinstance(value, (datetime, date)):
                    #     value = value.isoformat()

                    if row[0].value in worksheet_payload:
                        if isinstance(worksheet_payload[row[0].value], list):
                            worksheet_payload[row[0].value].append(value)
                        else:
                            value = worksheet_payload[row[0].value] + os.linesep + value

                    if hasattr(value, '__contains__') and ',' in value:
                        if value.replace(',', '').strip() != '':
                            value = [x.strip() for x in value.split(',')]

                    if (isinstance(value, int)):
                        value = str(value)
                    if isinstance(value, float):
                        cvalue = str(int(value))

                    worksheet_payload[row[0].value] = value
                    empty_row_count = 0
                    continue
                elif (ws_hdr_detected is True) and (ws_row_as_keys is True):  # store headers for the sheet
                    ws_hdr_keys = [v.value for v in row]
                    ws_row_as_keys = False
                    empty_row_count = 0
                    continue
                else:
                    kv_dict = self.__populate_kv_dict(row, ws_hdr_keys)
                    if kv_dict:  # append non-empty dictionary only
                        worksheet_payload[ws_hdr_title].append(kv_dict)
                    else:  # if dictionary is empty, that means contents for the headers are read. reset 'ws_hdr_detected' to False
                        ws_hdr_detected = False
                    empty_row_count = 0
            # end for-loop

            print('Done processing..')

            # ignore empty files
            if len(worksheet_payload) == 0:
                print('WARNING: Empty or \"Non Input\" sheet with title "' + worksheet.title + '" found.. Ignoring..')
                print('-' * 80)
                continue

            # worksheet_payload['CreationTimestamp'] = datetime.utcnow().isoformat()

            if worksheet_payload['DocType'] not in compiled_json.keys():
                compiled_json[worksheet_payload['DocType']] = dict()

            if worksheet_payload['DocType'] in ['SYS_CONFIG', 'APP_CONFIG']:
                compiled_json[worksheet_payload['DocType']] = worksheet_payload
            # compiled_json[worksheet_payload['DocType']].append(worksheet_payload)
            else:
                compiled_json[worksheet_payload['DocType']][worksheet_payload['Name']] = worksheet_payload

        return compiled_json

        # end for-loop

    def get_xlsx_document(self, xlsx_list: str, output_file_name="xlsx_document.json"):
        """
        This function converts xlsx files into json/dict

        :param xlsx_list: list of xlsx files name/path
        :param output_file_name: file name to write json
        :return: dict of xlsx files
        """
        data = dict()
        for file in xlsx_list:
            single_file_json = self.parse(file)
            for k, v in single_file_json.items():
                if data == {}:
                    data = single_file_json
                    break
                if k not in data.keys():
                    data[k] = dict()
                data[k].update(v)

        with open(output_file_name, 'w') as f:
            f.write(json.dumps(data))
        return data


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--ExcelFile', required=True)
    parser.add_argument('--OutputFolder', default='')
    args = parser.parse_args(sys.argv[1:])

    parser = ExcelParser()

    path_output_json = os.path.join(args.OutputFolder, 'output.json')
    data = parser.get_xlsx_document([args.ExcelFile], path_output_json)

    # Write CSV File for Servers
    try:
        path_servers_csv = os.path.join(args.OutputFolder, 'servers.csv')
        with open(path_servers_csv, 'w', newline='') as csvfile:
            r = data['Servers']['servers_config']['Servers'][0]
            csv_columns = r.keys()
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for row in data['Servers']['servers_config']['Servers']:
                writer.writerow(row)
    except IOError:
        print("I/O error")

    # Write CSV File for TAgs
    try:
        path_tags_csv = os.path.join(args.OutputFolder, 'tags.csv')
        with open(path_tags_csv, 'w', newline='') as tagfile:
            r = data['Tags']['tags']['TagsList'][0]
            csv_columns = r.keys()
            writer = csv.DictWriter(tagfile, fieldnames=csv_columns)
            writer.writeheader()
            for row in data['Tags']['tags']['TagsList']:
                writer.writerow(row)
    except IOError:
        print("I/O error")

    try:
        path_config_json = os.path.join(args.OutputFolder, 'config.json')
        with open(path_config_json, 'w', newline='') as f:
            config = data['Config']['Configurations']
            f.write(json.dumps(config))
    except IOError:
        print("I/O error")
    
    try:
        path_vpc_json = os.path.join(args.OutputFolder, 'vpc.json')
        with open(path_vpc_json, 'w', newline='') as f:
            vpc_config = data['VPC']['VPC_CONFIG']
            f.write(json.dumps(vpc_config))
    except IOError:
        print("I/O error")
    
    try:
        path_sg_json = os.path.join(args.OutputFolder, 'sg.json')
        with open(path_sg_json, 'w', newline='') as f:
            sg_config = data['SecurityGroups']['SG_CONFIG']
            f.write(json.dumps(sg_config))
    except IOError:
        print("I/O error")
    print(data)
