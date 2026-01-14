from odoo import api, fields, models
import requests
from odoo.exceptions import UserError, ValidationError
from datetime import date
from odoo import http
from odoo.http import request
import re

from odoo import http
from odoo.http import request
import hashlib
import json

import logging
from datetime import date,timedelta


_logger = logging.getLogger(__name__)


def get_token_id():
    url = "https://api.blinq.pk/api/Auth"

    # Payload containing ClientID and ClientSecret
    payload = {
        "ClientID": "2ABdYHvvJ7MCLcF",
        "ClientSecret": "FNFDyoCRczBpCr8"
    }

    # Headers (Modify if required)
    headers = {
        "Content-Type": "application/json"
    }

    # Sending POST request
    response = requests.post(url, json=payload, headers=headers)

    # Checking the response
    if response.status_code == 200:
        token = response.headers.get("Token")  # Extract token from headers
        if token:
            # print("Token:", token)
            return token
        else:
            print("Token not found in headers.")


class BankAPI(http.Controller):
    # @http.route('/blinq_CMSCollection/get', type='application/json', auth='none', methods=['GET', 'POST'], csrf=False)
    # def get_finance(self, **kwargs):

    #     _logger.info('----------------------')
    #     _logger.info(kwargs)
    #     _logger.info('?????????????????????')
    #     _logger.info(kwargs.headers)

    @http.route('/blinq_CMSCollection/get', type='json', auth='public', methods=['GET', 'POST'], csrf=False)
    def blinq_callback(self, **post):
        _logger.info('?????????????????????')
        _logger.info('?????????????????????')
        _logger.info('?????????????????????')
        _logger.info('?????????????????????')
        # Log the incoming request for debugging
        # request.env['ir.logging'].create({
        #     'name': 'BlinQ Callback',
        #     'type': 'server',
        #     'dbname': request.db,
        #     'level': 'info',
        #     'message': 'Incoming BlinQ Callback: {}'.format(post),
        #     'path': '/blinq/callback',
        #     'func': 'blinq_callback',
        #     'line': '1'
        # })

        if 1 == 1:
            # Extract JSON data from the POST request
            data = json.loads(request.httprequest.data)

            voucher = request.env['account.move'].sudo().search([('name', '=', data.get('invoice_number'))], limit=1)
            if data.get('invoice_status') == 'PAID' and voucher.sudo().payment_state != 'paid':
                payment_wizard = request.env['account.move.history'].sudo().create({'xml_class_id': voucher.id})
                payment_wizard = request.env['account.payment.register'].sudo().create({'communication': voucher.id})
                if voucher.company_id.id == 8:
                    journal = 50
                if voucher.company_id.id == 6:
                    journal = 51    
                if voucher.company_id.id == 7:
                    journal = 49
                payment_wizard.journal_id = journal
                payment_wizard.sudo().action_create_payments()
                voucher.sudo().payment_state = 'paid'
                voucher.sudo().is_online_transection = True

                return json.dumps({
                    "code": "00",
                    "message": "Invoice successfully marked as paid",
                    "status": "success",
                    "invoice_number": data.get('invoice_number')
                })

            elif voucher.sudo().payment_state == 'paid':
                return json.dumps({
                    "code": "00",
                    "message": "Invoice successfully marked as paid",
                    "status": "success",
                    "invoice_number": data.get('invoice_number')
                })


    def validate_data_integrity(self, data):
        _logger.info('?>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.')
        # Retrieve the callback_secret from Odoo configuration
        callback_secret = request.env['ir.config_parameter'].sudo().get_param('blinq.callback_secret')

        # Concatenate invoice_number and callback_secret
        concatenated_string = data.get('invoice_number') + callback_secret

        # Generate SHA-256 hash
        sha256_hash = hashlib.sha256(concatenated_string.encode()).hexdigest()

        # Generate MD5 hash from SHA-256 hash
        md5_hash = hashlib.md5(sha256_hash.encode()).hexdigest()

        # Compare the generated hash with the received data_integrity
        return md5_hash == data.get('data_integrity')


class FeeReportWizard(models.Model):
    _inherit = 'fee.discount'

    def update_move_id(self):
        res = super(FeeReportWizard, self).update_move_id()
        if self.move_id.company_id.id in [6,7,8]:
            self.move_id.block_invoice()
            self.move_id.create_invoice_to_blinq()
        return res


class BlinqCreateInvoice(models.Model):
    _inherit = "account.move"

    billId = fields.Char(string="1BillId",related='student_id.billId')
    is_online_transection = fields.Boolean(string='Online Transection',store=True)
    synced_to_blinq = fields.Boolean(string='Synced To Bilinq')
    disable_from_blinq = fields.Boolean(string='Disable From Bilinq')


    @api.constrains('payment_state')
    def automate_paid_to_blinq(self):
        for rec in self:
            if rec.payment_state == 'paid' and rec.company_id.id in [6,7,8] and rec.is_fee_invoice == True:
                rec.pay_invoice()


    @api.constrains('child_move_ids','state')
    def sync_installments_to_blinq(self):
        for rec in self:
            if rec.company_id.id in [6, 7, 8] and rec.child_move_ids and rec.is_fee_invoice == True:

                for ins in rec.child_move_ids:
                    if ins.state == 'posted':
                        ins.create_invoice_to_blinq()

                if rec.state == 'posted':
                    rec.create_invoice_to_blinq()


    def action_mark_fine(self):
        res = super(BlinqCreateInvoice, self).action_mark_fine()
        due_invoices = self.env['account.move'].search(
            [('invoice_date_due', '<', date.today()), ('state', '=', 'posted'),
             ('payment_state', 'in', ['not_paid']), ('is_fee_invoice', '=', True), ('super_invoice', '=', False),('company_id','in',[6,7,8])])
        for i in due_invoices:
            i.synced_to_blinq = False
            # due_invoices[0].create_invoice_after_fine()

        return res

    def get_invoice_status(self):
        # url = f"https://staging-api.blinq.pk/invoice/getstatus/{self.name}"
        headers = {
            "Token": f"{get_token_id()}"
        }
        url = f"https://api.blinq.pk/invoice/getstatus?InvoiceNumber={self.name}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            invoice_data = data.get("ResponseDetail", [])[0]
            invoice_amount = invoice_data.get("InvoiceAmount", "N/A")
            invoice_status = invoice_data.get("InvoiceStatus", "N/A")

            raise ValidationError(f"Invoice Amount: {invoice_amount}, Status: {invoice_status}")
        else:
            print("Error:", response.status_code, response.text)

    def paid_invoices(self):
        headers = {
            "Token": f"{get_token_id()}"
        }
        url = f"https://api.blinq.pk/invoice/getpaidinvoices?startDate={date.today()}&endDate={date.today()}"
        response = requests.get(url, headers=headers)

        data = response.json()
        if data.get('Message') == "Record fetched successfully":
            invoice_numbers = [item["InvoiceNumber"] for item in data["ResponseDetail"]]
            for voucher in invoice_numbers:
                _logger.info(f">>>>>>>>>>>>>>>>>>>>>>{voucher}")
                voucher = self.env['account.move'].search([('name', '=', voucher)])
                _logger.info(f">>>>>>>>>>>>>>>>>>>>>>{voucher.sudo().payment_state}")
                if voucher.sudo().payment_state != 'paid':
                    payment_wizard = self.env['account.move.history'].sudo().create({'xml_class_id': voucher.id})
                    payment_wizard = self.env['account.payment.register'].sudo().create({'communication': voucher.id})
    
                    if voucher.company_id.id == 8:
                        journal = 50
                    if voucher.company_id.id == 6:
                        journal = 51    
                    if voucher.company_id.id == 7:
                        journal = 49
                    payment_wizard.journal_id = journal
                    payment_wizard.sudo().action_create_payments()
                    voucher.sudo().payment_state = 'paid'
                    voucher.sudo().is_online_transection = True
        print(response.text)

    def block_invoice_in_bulk(self, inv_ids):
        # url = f"https://staging-api.blinq.pk/invoice/markasblocked?csvInvoices=INV-1233,INV-44444"
        _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        all_invoices = self.env['account.move'].search([('id', 'in', inv_ids)])
        empty_str = ''
        for i in all_invoices:
            if empty_str == '':
                empty_str = i.name
            else:
                empty_str = empty_str + ',' + i.name
        headers = {
            "Token": f"{get_token_id()}"
        }
        _logger.info(empty_str)
        url = f"https://api.blinq.pk/invoice/markasblocked?csvInvoices={empty_str}"
        response = requests.get(url, headers=headers)
        for rec in self:
            rec.synced_to_blinq = False
            rec.disable_from_blinq = True
        print(response.text)
        _logger.info(response.text)

    def block_invoice(self):
        # url = f"https://staging-api.blinq.pk/invoice/markasblocked?csvInvoices=INV-1233,INV-44444"
        headers = {
            "Token": f"{get_token_id()}"
        }
        url = f"https://api.blinq.pk/invoice/markasblocked?csvInvoices={self.mapped('name')[0]}"
        response = requests.get(url, headers=headers)
        for rec in self:
            rec.synced_to_blinq = False
            rec.disable_from_blinq = True
        print(response.text)
        _logger.info('??????????>>>>>>>>>>')
        _logger.info(response.text)

    def pay_invoice(self):
        # url = f"https://staging-api.blinq.pk/invoice/markasblocked?csvInvoices=INV-1233,INV-44444"
        headers = {
            "Token": f"{get_token_id()}"
        }
        url = f"https://api.blinq.pk/invoice/markaspaid?csvInvoices={self.mapped('name')[0]}"
        response = requests.get(url, headers=headers)
        # for rec in self:
        #     rec.synced_to_blinq = False
        #     rec.disable_from_blinq = True
        print(response.text)

    def unpay_invoice(self):
        # url = f"https://staging-api.blinq.pk/invoice/markasblocked?csvInvoices=INV-1233,INV-44444"
        headers = {
            "Token": f"{get_token_id()}"
        }
        url = f"https://api.blinq.pk/invoice/markasunpaid?csvInvoices={self.mapped('name')[0]}"
        response = requests.get(url, headers=headers)
        # for rec in self:
        #     rec.synced_to_blinq = False
        #     rec.disable_from_blinq = True
        print(response.text)

    def create_invoice_to_blinq(self):

        _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        url = "https://api.blinq.pk/invoice/create"
        headers = {
            "Token": f"{get_token_id()}"
        }
        payload = []
        for rec in self:
            print(rec,'>>>>>>>>>>>>>>>>>>>>>>>>>',rec.synced_to_blinq)
            if rec.synced_to_blinq == True:

                rec.block_invoice()

            updated_number = re.sub(r'^\+?92', '0', rec.student_id.mobile).replace(" ", "")
            # updated_number2 = re.sub(r'^\+?92', '0', rec.partner_id.phone).replace(" ", "")
            # _logger.info(f"{updated_number}>>>>>>{updated_number2}")
            due_date = rec.invoice_date_due
            if due_date < date.today():
                due_date = date.today() + timedelta(days=7)
            payload1 = {
                "ConsumerId": f"{rec.student_id.id}",
                "InvoiceNumber": f"{rec.name}",
                "InvoiceAmount": f"{rec.amount_total}",
                "InvoiceDueDate": f"{due_date}",
                "ValidityDate": f"{due_date}",
                "InvoiceType": "Service",
                "IssueDate": f"{rec.invoice_date}",
                "InvoiceExpireAfterSeconds": "0",
                "CustomerName": f"{rec.partner_id.id}",
                "CustomerMobile1": updated_number,
                "CustomerMobile2": updated_number,
                "CustomerMobile3": "",
                "CustomerEmail1": f"{rec.student_id.email}" if rec.student_id.email else 'managingdirector@cityhighschool.pk',
                "CustomerEmail2": "",
                "CustomerEmail3": "",
                "CustomerAddress": "NIL"
            }
            payload.append(payload1)

        print(payload)
        _logger.info(payload)
        # response = requests.post(url, headers=headers, data=payload)
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        if data.get('Message') == "All invoices successfully created!":
            for rec in self:
                rec.synced_to_blinq = True
                rec.disable_from_blinq = False
        else:
            raise ValidationError(response.text)
        print(response.text)
        _logger.info(response.text)

    def create_invoice_to_blinq_in_bulk(self):
        url = "https://api.blinq.pk/invoice/create"
        headers = {
            "Token": f"{get_token_id()}"
        }
        payload = []
        all_invoices = self.env['account.move'].search([ ('state', '=', 'posted'),('payment_state', 'in', ['not_paid']), ('is_fee_invoice', '=', True),('synced_to_blinq','=',False),('company_id','in',[6,7,8])],limit=45)

        # all_invoices = self.env['account.move'].search([('id','in',[22504,22503,22502,22501,22500,22499,22498,22497,22496,22495,22494,22493,22492,22491,21564,21563,21562,21561,21560])])
        # all_invoices = self.env['account.move'].search(
        #     [('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('payment_state', 'in', ['not_paid']),
        #      ('synced_to_blinq', '=', False)])
        for rec in all_invoices:
            rec.block_invoice()
            if rec.synced_to_blinq == True:
                rec.block_invoice()
            if rec.student_id.mobile:

                updated_number = re.sub(r'^\+?92', '0', rec.student_id.mobile).replace(" ", "")
                # updated_number2 = re.sub(r'^\+?92', '0', rec.partner_id.phone).replace(" ", "")
                payload1 = {
                    "ConsumerId": f"{rec.student_id.id}",
                    "InvoiceNumber": f"{rec.name}",
                    "InvoiceAmount": f"{rec.amount_total}",
                    "InvoiceDueDate": f"{rec.invoice_date_due + timedelta(days=4)}",
                    "ValidityDate": f"{rec.invoice_date_due + timedelta(days=4)}",
                    "InvoiceType": "Service",
                    "IssueDate": f"{rec.invoice_date}",
                    "InvoiceExpireAfterSeconds": "0",
                    "CustomerName": f"{rec.partner_id.id}",
                    "CustomerMobile1": updated_number,
                    "CustomerMobile2": updated_number,
                    "CustomerMobile3": "",
                    "CustomerEmail1": f"{rec.student_id.email}" if rec.student_id.email else 'managingdirector@cityhighschool.pk',
                    "CustomerEmail2": "",
                    "CustomerEmail3": "",
                    "CustomerAddress": "NIL"
                }
                payload.append(payload1)

        print(payload)
        # response = requests.post(url, headers=headers, data=payload)
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        print(data.get('Message'))
        _logger.info(f"{len(payload)}>>>>>>>>>>>>>>>>>>>>>>>{data.get('Message')}")
        if data.get('Message') == "All invoices successfully created!":
            for rec in all_invoices:
                rec.synced_to_blinq = True
                rec.disable_from_blinq = False

        elif 'Monthly Uploaded Invoice Limit' in  data.get('Message'):
            pass
        else:
            for rec in all_invoices:
                
                    
                if rec.name not in str(response.text):
                    rec.synced_to_blinq = True
                    rec.disable_from_blinq = False
                else:
                    rec.synced_to_blinq = False
                    rec.disable_from_blinq = False
            
            if 'already exist' in data.get('Message'):
                for rec in all_invoices:
                    if rec.name in str(response.text):
                        rec.synced_to_blinq = True
                        rec.disable_from_blinq = False

        _logger.info(response.text)

    def create_invoice_after_fine(self):
        url = "https://api.blinq.pk/invoice/create"
        headers = {
            "Token": f"{get_token_id()}"
        }
        payload = []
        all_invoices = self.env['account.move'].search(
            [('invoice_date_due', '<', date.today()), ('state', '=', 'posted'),
             ('payment_state', 'in', ['not_paid']), ('is_fee_invoice', '=', True), ('super_invoice', '=', False),('synced_to_blinq','=',False),('company_id','in',[6,7,8])],limit=50)

        all_invoices = self.env['account.move'].search([ ('state', '=', 'posted'),('payment_state', 'in', ['not_paid']), ('is_fee_invoice', '=', True),('synced_to_blinq','=',False),('company_id','in',[6,7,8])],limit=45)

        # all_invoices = self.env['account.move'].search([ ('state', '=', 'posted'),('payment_state', 'in', ['not_paid']), ('is_fee_invoice', '=', True),('synced_to_blinq','=',False)])
        print(all_invoices,'dddddddddddddddd')
        if all_invoices:
            all_invoices[1].block_invoice_in_bulk(all_invoices.ids)

        for rec in all_invoices:
            updated_number = re.sub(r'^\+?92', '0', rec.student_id.mobile).replace(" ", "")
            # updated_number2 = re.sub(r'^\+?92', '0', rec.partner_id.phone).replace(" ", "")
            payload1 = {
                "ConsumerId": f"{rec.student_id.id}",
                "InvoiceNumber": f"{rec.name}",
                "InvoiceAmount": f"{rec.amount_total}",
                "InvoiceDueDate": f"{date.today() + timedelta(days=7)}",
                "ValidityDate": f"{rec.invoice_date_due}",
                "InvoiceType": "Service",
                "IssueDate": f"{rec.invoice_date}",
                "InvoiceExpireAfterSeconds": "0",
                "CustomerName": f"{rec.partner_id.id}",
                "CustomerMobile1": updated_number,
                "CustomerMobile2": updated_number,
                "CustomerMobile3": "",
                "CustomerEmail1": f"{rec.student_id.email}" if rec.student_id.email else 'managingdirector@cityhighschool.pk',
                "CustomerEmail2": "",
                "CustomerEmail3": "",
                "CustomerAddress": "NIL"
            }
            payload.append(payload1)

        print(payload)
        # response = requests.post(url, headers=headers, data=payload)
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        print(data.get('Message'))
        _logger.info(f"{len(payload)}>>>>>>>>>>>>>>>>>>>>>>>{data.get('Message')}")
        if data.get('Message') == "All invoices successfully created!":
            for rec in all_invoices:
                rec.synced_to_blinq = True
                rec.disable_from_blinq = False

        elif 'Monthly Uploaded Invoice Limit' in  data.get('Message'):
            pass
        else:
            for rec in all_invoices:
                
                    
                if rec.name not in str(response.text):
                    rec.synced_to_blinq = True
                    rec.disable_from_blinq = False
                else:
                    rec.synced_to_blinq = False
                    rec.disable_from_blinq = False
            
            if 'already exist' in data.get('Message'):
                for rec in all_invoices:
                    if rec.name in str(response.text):
                        rec.synced_to_blinq = True
                        rec.disable_from_blinq = False


        print(response.text)



class BlinqCreateConsumer(models.Model):
    _inherit = "op.student"

    billId = fields.Char(string="1BillId")

    def get_consumer(self):
        url = "https://api.blinq.pk/consumer/getconsumerdata?consumerCode=000201580"
        response = requests.get(url)
        print(response.text)

    def disable_consumer(self):
        # "https://staging-api.blinq.pk/consumer/disable?ConsumerCode={ConsumerCode}"
        url = "https://api.blinq.pk/consumer/disable?ConsumerCode={ConsumerCode}"
        headers = {
            "Token": "wR3Yge/OJVFZfwYigWRbIYkflFpNdb+LK9/9UU6EaJtb105oTRmr/2iqW/CX9HrEOBc8SFdPiNaZyRyXUN7PueA1r7ejWojBgDbGX1c3Umo="
        }
        response = requests.post(url, headers=headers)

    def sync_to_blinq_in_bulk(self):
        students = self.env['op.student'].search([('billId','=',False),('company_id','in',[6,7,8])],limit=80)
        for rec in students:
            rec.create_consumer()

    def create_consumer(self):
        _logger.info('55555555555555555555555')
        url = "https://api.blinq.pk/consumer/create"
        headers = {
            "Token": f"{get_token_id()}"
        }
        try:
            updated_number = re.sub(r'^\+?92', '0', self.mobile).replace(" ", "")
            # updated_number = re.sub(r'^\+?92', '0', self.partner_id.mobile).replace(" ", "")
            # updated_number2 = re.sub(r'^\+?92', '0', self.partner_id.phone).replace(" ", "")
        except:

            raise ValidationError('Kindly Add Mobile/Phone number on partner')

        # updated_number = re.sub(r'^\+?92', '0', self.partner_id.mobile)
        # updated_number2 = re.sub(r'^\+?92', '0', self.partner_id.phone)
        # _logger.info(f"{updated_number2},///////{updated_number}")
        payload = {
            "ConsumerCode": f"{self.id}",
            "Name": f"{self.partner_id.name}",
            "Mobile1": updated_number,
            "Mobile2": updated_number,
            "Mobile3": f"",
            "Email1": f"{self.email}" if self.email else 'managingdirector@cityhighschool.pk',
            "Email2": f"",
            "Email3": f"",
            "Address": f""
        }

        payload = [payload]

        response = requests.post(url, headers=headers, json=payload)

        data = response.json()
        print(data.get('Message'))
        if 'already exist' in data.get('Message'):
            self.billId = f"1003330388{self.id}"    
        
        elif data.get('Message') != "All consumers successfully created!":
            raise ValidationError(response.text)


        data = response.json()
        consumer = data.get("ResponseDetail", [])[0]
        billId = consumer.get("1BillId", "N/A")

        self.billId = f"{billId}"

        _logger.info(response.text)
        print(response.text)

    # def update_consumer(self):
    #     url = "https://staging-api.blinq.pk/consumer/update"
    #     headers = {
    #         "Token": f"{get_token_id()}"
    #     }
    #
    #     updated_number = re.sub(r'^\+?92', '0', self.partner_id.mobile)
    #     updated_number2 = re.sub(r'^\+?92', '0', self.partner_id.phone)
    #     payload = {
    #         "ConsumerCode": f"{self.partner_id.id}",
    #         "Name": f"{self.partner_id.name}",
    #         "Mobile1": updated_number,
    #         "Mobile2": updated_number2,
    #         "Mobile3": f"",
    #         "Email1": f"{self.partner_id.email}",
    #         "Email2": f"",
    #         "Email3": f"",
    #         "Address": f""
    #     }
    #
    #     print('[--------------]', payload)
    #
    #     payload = [payload]
    #
    #     # response = requests.post(url, headers=headers, json=payload)
    #     response = requests.post(url, headers=headers, json=payload)
    #     print(response.text)
