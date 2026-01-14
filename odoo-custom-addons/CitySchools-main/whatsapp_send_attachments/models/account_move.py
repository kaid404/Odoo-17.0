import logging

from PyPDF2 import PdfFileReader, PdfFileWriter

import base64
import io
import os

from odoo import models, fields, _, api

import requests

_logger = logging.getLogger(__name__)
import time


class AccountMove(models.Model):
    _inherit = 'account.move'
    voucher_sent = fields.Boolean(string="Voucher Sent", store=True)
    receipt_sent = fields.Boolean(string="Receipt Sent", store=True)
    whatsapp_status = fields.Html(string='Whatsapp Status')
    wrong_number = fields.Html(string='Invalid Number')

    def send_voucher_whatsapp_message(self):
        
        months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }

        # [42, 80]
        #6,7,8
        start_time = time.time()
        if self:
            previos_invoice = self.env['account.move'].search(
                [('move_type', '=', 'out_invoice'), ('is_fee_invoice', '=', True), ('voucher_sent', '=', False),('company_id','in',[2,6,7,8]),
                 ('payment_state', 'in', ['not_paid']), ('id', '=', self.id), ('partner_id.mobile', '!=', False)],
                limit=1)
        else:
            previos_invoice = self.env['account.move'].search(
                [('move_type', '=', 'out_invoice'), ('is_fee_invoice', '=', True), ('voucher_sent', '=', False),('company_id','in',[2,6,7,8]),
                 ('payment_state', 'in', ['not_paid']), ('wrong_number', '=', False),
                 ('partner_id.mobile', '!=', False)], limit=1)

        if previos_invoice:
            
            report_id = self.env.ref('city_school.report_city_school_detail')
            if previos_invoice[0].company_id in [6,7,8]:
                report_data = report_id._render_qweb_pdf('fee_voucher.fee_voucher_print_action',
                                                         res_ids=previos_invoice.ids,
                                                         data={'name': "saad"})
            else:
                report_data = report_id._render_qweb_pdf('fee_voucher_backup.fee_voucher_print_action_old',
                                                         res_ids=previos_invoice.ids,
                                                         data={'name': "saad"})

            end_time = time.time()
            print(end_time - start_time, len(previos_invoice))
            _logger.info(end_time - start_time, len(previos_invoice))

            report_binary = report_data[0]
            #
            # attachment = self.env['ir.attachment'].create({
            #     'name': 'Low Stock Notificationnne  ',
            #     'datas': base64.b64encode(report_binary),
            #     'type': 'binary',
            # })

            # attachment_binary = base64.b64decode(attachment.datas)
            output_dir = '/tmp'

            multi_page_pdf_path = os.path.join(output_dir, 'multi_page_invoice.pdf')

            binary_data = base64.b64decode(base64.b64encode(report_binary))

            # attachment.unlink()
            with open(multi_page_pdf_path, 'wb') as f:
                f.write(binary_data)

            with open(multi_page_pdf_path, 'rb') as multi_pdf:
                reader = PdfFileReader(multi_pdf)
                for page_number in range(reader.getNumPages()):
                    writer = PdfFileWriter()
                    writer.addPage(reader.getPage(page_number))

                    single_page_pdf_path = f'/tmp/invoice_page_{page_number + 1}.pdf'
                    with open(single_page_pdf_path, 'wb') as single_pdf:
                        writer.write(single_pdf)
                        # attachment_binary = base64.b64decode(self.invoice_pdf_report_file)
                        #
                    print('llllllll')
                    _logger.info(
                        '-------------------------------------------------------------------------------------')
                    # _logger.info(previos_invoice[page_number].partner_id.mobile)
                    _logger.info(previos_invoice[page_number].partner_id.name)
                    number_n = previos_invoice[page_number].partner_id.mobile.replace("+", "").replace(" ", "")
                    if number_n:
                        if number_n[0] == '0':
                            number_n = '92' + number_n[1:]

                    _logger.info(number_n)

                    url = "https://7103.media.greenapi.com/waInstance7103138190/sendFileByUpload/43d917fdef8147e2a1d3e190e654091c9c7240043da6484d80"
                    url = "https://7103.media.greenapi.com/waInstance7103157899/sendFileByUpload/50973cf7301847929e959a57989958574f7ba6f8376e47c7b2"
                    url = "https://7700.media.greenapi.com/waInstance7700158158/sendFileByUpload/baed87786a5747bc8a6b9a4f4c4b37ed2b4433a370e645829f"

                    if previos_invoice[page_number].company_id.id in [6,7,8]:
                        url = "https://7700.media.greenapi.com/waInstance7700183902/sendFileByUpload/d9fadc38435d4538bbc71008bf8760c5c9875203af21407797"

                    payload = {
                        'chatId': f'{number_n}@c.us'
                    }
                    with open(f'/tmp/invoice_page_{page_number + 1}.pdf', 'rb') as pdf_file:
                        file_content = pdf_file.read()

                    # Attach the binary file content to send instead of the file path
                    files = [
                        ('file', (
                            f'Fee challan for the month of {months[previos_invoice[page_number].invoice_date.month]} of {previos_invoice[page_number].partner_id.name}',
                            io.BytesIO(file_content), 'application/pdf'))
                    ]
                    headers = {}

                    response = requests.post(url, data=payload, files=files)
                    print(response.text.encode('utf8'))
                    _logger.info(response.text.encode('utf8'))
                    if len(number_n) != 12:
                        previos_invoice[page_number].wrong_number = False
                        self.message_post(
                            body=f"The fee voucher could not be sent via WhatsApp. The provided number {number_n} appears to be invalid or not connected to WhatsApp. Please verify the number and try again.",
                            subtype_xmlid="mail.mt_note"  # Standard note subtype
                        )
                    else:
                        previos_invoice[page_number].voucher_sent = True
                        previos_invoice[page_number].wrong_number = False
                        previos_invoice[page_number].whatsapp_status = response.text

                        self.message_post(
                            body=f"Fee voucher sent successfully via WhatsApp.",
                            subtype_xmlid="mail.mt_note"  # Standard note subtype
                        )

                    os.remove(f'/tmp/invoice_page_{page_number + 1}.pdf')
                os.remove(multi_page_pdf_path)

            # print(response.text.encode('utf8'))

    
    
    
    
    
    
    
    @api.constrains('payment_state')
    def send_receipt_whatsapp_message(self):
        months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }

        # [42, 80]
        for rec in self:
            start_time = time.time()
            previos_invoice = self.env['account.move'].search(
                [('move_type', '=', 'out_invoice'), ('is_fee_invoice', '=', True), ('receipt_sent', '=', False),('company_id','in',[2,6,7,8]),
                 ('payment_state', 'in', ['paid']), ('id', '=', rec.id), ('partner_id.mobile', '!=', False)], limit=1)
            if previos_invoice:

                report_id = self.env.ref('city_school.report_city_school_detail')
                report_data = report_id._render_qweb_pdf('city_school.report_city_school_detail',
                                                         res_ids=previos_invoice.ids,
                                                         data={'name': "saad"})

                end_time = time.time()
                print(end_time - start_time, len(previos_invoice))
                _logger.info(end_time - start_time, len(previos_invoice))

                report_binary = report_data[0]
                #
                # attachment = self.env['ir.attachment'].create({
                #     'name': 'Low Stock Notificationnne  ',
                #     'datas': base64.b64encode(report_binary),
                #     'type': 'binary',
                # })

                # attachment_binary = base64.b64decode(attachment.datas)
                output_dir = '/tmp'

                multi_page_pdf_path = os.path.join(output_dir, 'multi_page_invoice.pdf')

                binary_data = base64.b64decode(base64.b64encode(report_binary))

                # attachment.unlink()
                with open(multi_page_pdf_path, 'wb') as f:
                    f.write(binary_data)

                with open(multi_page_pdf_path, 'rb') as multi_pdf:
                    reader = PdfFileReader(multi_pdf)
                    for page_number in range(reader.getNumPages()):
                        writer = PdfFileWriter()
                        writer.addPage(reader.getPage(page_number))

                        single_page_pdf_path = f'/tmp/invoice_page_{page_number + 1}.pdf'
                        with open(single_page_pdf_path, 'wb') as single_pdf:
                            writer.write(single_pdf)
                            # attachment_binary = base64.b64decode(self.invoice_pdf_report_file)
                            #
                        print('llllllll')
                        _logger.info(
                            '-------------------------------------------------------------------------------------')
                        _logger.info(previos_invoice[page_number].partner_id.mobile)
                        _logger.info(previos_invoice[page_number].partner_id.name)
                        number_n = previos_invoice[page_number].partner_id.mobile.replace("+", "").replace(" ", "")
                        if number_n:
                            if number_n[0] == '0':
                                number_n = '92' + number_n[1:]
                        _logger.info(number_n)

                        url = "https://7103.media.greenapi.com/waInstance7103138190/sendFileByUpload/43d917fdef8147e2a1d3e190e654091c9c7240043da6484d80"
                        url = "https://7103.media.greenapi.com/waInstance7103157899/sendFileByUpload/50973cf7301847929e959a57989958574f7ba6f8376e47c7b2"
                        url = "https://7700.media.greenapi.com/waInstance7700158158/sendFileByUpload/baed87786a5747bc8a6b9a4f4c4b37ed2b4433a370e645829f"

                        if previos_invoice[page_number].company_id.id in [6,7,8]:
                            url = "https://7700.media.greenapi.com/waInstance7700183902/sendFileByUpload/d9fadc38435d4538bbc71008bf8760c5c9875203af21407797"


                        payload = {
                            'chatId': f'{number_n}@c.us'
                        }
                        with open(f'/tmp/invoice_page_{page_number + 1}.pdf', 'rb') as pdf_file:
                            file_content = pdf_file.read()

                        # Attach the binary file content to send instead of the file path
                        files = [
                            ('file', (
                                f'Fee receipt for the month of {months[previos_invoice[page_number].invoice_date.month]} of {previos_invoice[page_number].partner_id.name}',
                                io.BytesIO(file_content), 'application/pdf'))
                        ]
                        headers = {}

                        response = requests.post(url, data=payload, files=files)
                        print(response.text.encode('utf8'))
                        _logger.info(response.text.encode('utf8'))
                        if len(number_n) != 12:
                            previos_invoice[page_number].wrong_number = False
                            previos_invoice[page_number].message_post(
                                body=f"The fee receipt could not be sent via WhatsApp. The provided number {number_n} appears to be invalid or not connected to WhatsApp. Please verify the number and try again.",
                                subtype_xmlid="mail.mt_note"  # Standard note subtype
                            )
                        else:
                            previos_invoice[page_number].wrong_number = True
                            previos_invoice[page_number].receipt_sent = True
                            previos_invoice[
                                page_number].whatsapp_status = f"""{previos_invoice[page_number].whatsapp_status}<br/>{response.text}"""
                            previos_invoice[page_number].message_post(
                                body=f"Fee receipt sent successfully via WhatsApp.",
                                subtype_xmlid="mail.mt_note"  # Standard note subtype
                            )

                        os.remove(f'/tmp/invoice_page_{page_number + 1}.pdf')
                    os.remove(multi_page_pdf_path)

                    # print(response.text.encode('utf8'))
