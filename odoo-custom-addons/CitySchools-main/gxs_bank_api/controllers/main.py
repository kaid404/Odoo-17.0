import pytz
import subprocess
import sys
from odoo import models,fields,api,_

# Specify the package name and version you want to install
package_name = "pyramid"
package_version = ""  # You can specify a specific version here if needed 
# subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
# Use pip to install the package
# try:
#     if package_version:
#         subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package_name}=={package_version}"])
#     else:
#         subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
# except subprocess.CalledProcessError as e:
#     pass

from odoo import http
from odoo.http import request
from datetime import datetime, timezone, date
from datetime import datetime, timedelta
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

import logging
import json
from pyramid.view import view_config
from pyramid.response import Response
from datetime import datetime

_logger = logging.getLogger(__name__)
from pytz import timezone, UTC

import xml.etree.ElementTree as ET
from odoo.exceptions import UserError

from odoo.addons.account.wizard.account_payment_register import AccountPaymentRegister

@api.model
def default_get(self, fields_list):
    print('gggggggggggggggggggggg')
    # OVERRIDE
    res = super(AccountPaymentRegister,self).default_get(fields_list)

    if 'line_ids' in fields_list and 'line_ids' not in res:

        # Retrieve moves to pay from the context.

        if self._context.get('active_model') == 'account.move':
            lines = self.env['account.move'].browse(self._context.get('active_ids', [])).line_ids
        elif self._context.get('active_model') == 'account.move.line':
            lines = self.env['account.move.line'].browse(self._context.get('active_ids', []))
        else:
            print('fffffffffffffff', self._context.get('active_model'))
            history_id = self.env['account.move.history'].sudo().search([], order="id DESC",limit=1)
            _logger.info(history_id)
            _logger.info(history_id.xml_class_id)
            
            lines = history_id.xml_class_id.line_ids
            #
            # raise UserError(_(
            #     "The register payment wizard should only be called on account.move or account.move.line records."
            # ))

        if 'journal_id' in res and not self.env['account.journal'].browse(res['journal_id']).filtered_domain([
            *self.env['account.journal']._check_company_domain(lines.company_id),
            ('type', 'in', ('bank', 'cash')),
        ]):
            # default can be inherited from the list view, should be computed instead
            del res['journal_id']

        # Keep lines having a residual amount to pay.
        available_lines = self.env['account.move.line']
        valid_account_types = self.env['account.payment']._get_valid_payment_account_types()
        for line in lines:
            if line.move_id.state != 'posted':
                raise UserError(_("You can only register payment for posted journal entries."))

            if line.account_type not in valid_account_types:
                continue
            if line.currency_id:
                if line.currency_id.is_zero(line.amount_residual_currency):
                    continue
            else:
                if line.company_currency_id.is_zero(line.amount_residual):
                    continue
            available_lines |= line

        # Check.
        if not available_lines:
            raise UserError(
                _("You can't register a payment because there is nothing left to pay on the selected journal items."))
        if len(lines.company_id.root_id) > 1:
            raise UserError(_("You can't create payments for entries belonging to different companies."))
        if len(set(available_lines.mapped('account_type'))) > 1:
            raise UserError(
                _("You can't register payments for journal items being either all inbound, either all outbound."))

        res['line_ids'] = [(6, 0, available_lines.ids)]

    return res
AccountPaymentRegister.default_get = default_get

class AccountMove(models.Model):
    _name = 'account.move.history'
    xml_class_id = fields.Many2one('account.move',string="xml_class_id" ,readonly=True)

class BankAPI(http.Controller):

    @http.route('/MBL_CMSCollection/get', type='http', auth='none', methods=['GET', 'POST'])
    def get_finance(self, **kwargs):
        try:
            xml_bytes = request.httprequest.data
            x = xml_bytes.decode("utf-8", errors="ignore")
            root = ET.fromstring(x)
            voucher_id = root.find('.//VoucherNumber').text
            # voucher_id = kwargs.get('VoucherNumber')
            token = root.find('.//Token').text
            # token = kwargs.get('Token')
            if token != 'test_token':
                resp = ET.Element("CityVoucherPAYResponse")
                success = ET.SubElement(resp, "success")
                success.text = "false"
                result = ET.SubElement(resp, "result")
                result.text = "Failed"
                code = ET.SubElement(resp, "StatusCode")
                code.text = "093"
                codeDescription = ET.SubElement(resp, "codeDescription")
                codeDescription.text = "Authentication Token is invalid"
                # Create an ElementTree object
                tree = ET.ElementTree(resp)
                # Generate the XML as a string
                xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")

                # Print the XML response
                return json.dumps(xml_response)
            voucher = request.env['account.move'].sudo().search([('name', '=', voucher_id)])
            if not voucher:
                resp = ET.Element("CityVoucherPAYResponse")
                success = ET.SubElement(resp, "success")
                success.text = "false"
                result = ET.SubElement(resp, "result")
                result.text = "Failed"
                code = ET.SubElement(resp, "StatusCode")
                code.text = "091"
                codeDescription = ET.SubElement(resp, "codeDescription")
                codeDescription.text = "Voucher Id is invalid"
                xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")
                return json.dumps(xml_response)
            if voucher.payment_state == 'paid':
                resp = ET.Element("CityVoucherPAYResponse")
                success = ET.SubElement(resp, "success")
                success.text = "false"
                result = ET.SubElement(resp, "result")
                result.text = "Failed"
                code = ET.SubElement(resp, "StatusCode")
                code.text = "097"
                codeDescription = ET.SubElement(resp, "codeDescription")
                codeDescription.text = "Voucher is Already Paid"
                xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")
                return json.dumps(xml_response)

            amt = 0

            # if voucher.invoice_date_due < date.today() and voucher.payment_state != 'partial' and not voucher.super_invoice:
            #     fee_st = request.env['fee.structure'].search([
            #         ('classes', '=', voucher.student_id.year_id.id),
            #         ('date_start', '<=', date.today()),
            #         ('date_end', '>=', date.today())
            #     ], limit=1)
            #     amt = int(fee_st.late_fee)

            root = ET.Element("CityVoucherFetchResponse")

            # Create child elements and set their text values
            success = ET.SubElement(root, "success")
            success.text = "true"

            result = ET.SubElement(root, "result")

            responseCode = ET.SubElement(result, "ResponseCode")
            responseCode.text = '00'

            responseDesc = ET.SubElement(result, "ResponseDesc")
            responseDesc.text = voucher.payment_state

            student_name = ET.SubElement(result, "student_name")
            student_name.text = voucher.student_id.first_name

            student_id = ET.SubElement(result, "student_id")
            student_id.text = str(voucher.student_id.id)

            dueDate = ET.SubElement(result, "DueDate")
            dueDate.text = f"{voucher.invoice_date_due.year}{voucher.invoice_date_due.month}{voucher.invoice_date_due.day}"

            amount_WID_Date = ET.SubElement(result, "Amount_WID_Date")
            amount_WID_Date.text = f"{voucher.amount_residual + amt:.2f}"

            amount_AD_Date = ET.SubElement(result, "Amount_AD_Date")
            amount_AD_Date.text = f"{voucher.amount_residual + amt:.2f}"

            billingMonth = ET.SubElement(result, "BillingMonth")
            billingMonth.text = f"{voucher.invoice_date_due.year}{voucher.invoice_date_due.month}{voucher.invoice_date_due.day}"
            remarks = ET.SubElement(result, "Remarks")
            remarks.text = 'Remarks'
            xml_response = ET.tostring(root, encoding="utf-16").decode("utf-16")
            response = request.make_response(xml_response, [('Content-Type', 'application/xml; charset=UTF-8')])
            response.content_type = 'application/xml'

            return response
        except Exception as e:
            resp = ET.Element("CityVoucherPAYResponse")
            success = ET.SubElement(resp, "success")
            success.text = "false"
            result = ET.SubElement(resp, "result")
            result.text = "Failed"
            code = ET.SubElement(resp, "StatusCode")
            code.text = "096"
            codeDescription = ET.SubElement(resp, "codeDescription")
            codeDescription.text = f"{e}"
            # Create an ElementTree object
            tree = ET.ElementTree(resp)
            # Generate the XML as a string
            xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")

            # Print the XML response
            print(xml_response)

            return json.dumps(xml_response)

    @http.route('/MBL_CMSCollection/get/backup', type='http', auth='none', methods=['GET', 'POST'])
    def get_finance_backup(self, **kwargs):
        try:
            voucher_id = kwargs.get('VoucherNumber')
            token = kwargs.get('Token')
            if token != 'test_token':
                resp = ET.Element("CityVoucherPAYResponse")
                success = ET.SubElement(resp, "success")
                success.text = "false"
                result = ET.SubElement(resp, "result")
                result.text = "Failed"
                code = ET.SubElement(resp, "StatusCode")
                code.text = "093"
                codeDescription = ET.SubElement(resp, "codeDescription")
                codeDescription.text = "Authentication Token is invalid"
                # Create an ElementTree object
                tree = ET.ElementTree(resp)
                # Generate the XML as a string
                xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")

                # Print the XML response
                return json.dumps(xml_response)
            voucher = request.env['account.move'].sudo().search([('name', '=', voucher_id)])
            if not voucher:
                resp = ET.Element("cityVoucherPAYResponse")
                success = ET.SubElement(resp, "success")
                success.text = "false"
                result = ET.SubElement(resp, "result")
                result.text = "Failed"
                code = ET.SubElement(resp, "StatusCode")
                code.text = "091"
                codeDescription = ET.SubElement(resp, "codeDescription")
                codeDescription.text = "Voucher Id is invalid"
                xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")
                return json.dumps(xml_response)
            if voucher.payment_state == 'paid':
                resp = ET.Element("CityVoucherPAYResponse")
                success = ET.SubElement(resp, "success")
                success.text = "false"
                result = ET.SubElement(resp, "result")
                result.text = "Failed"
                code = ET.SubElement(resp, "StatusCode")
                code.text = "097"
                codeDescription = ET.SubElement(resp, "codeDescription")
                codeDescription.text = "Voucher is Already Paid"
                xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")
                return json.dumps(xml_response)

            amt = 0

            # if voucher.invoice_date_due < date.today() and voucher.payment_state != 'partial' and not voucher.super_invoice:

            #     fee_st = request.env['fee.structure'].search([
            #         ('classes', '=', voucher.student_id.year_id.id),
            #         ('date_start', '<=', date.today()),
            #         ('date_end', '>=', date.today())
            #     ], limit=1)
            #     amt = int(fee_st.late_fee)

            root = ET.Element("CityVoucherFetchResponse")

            # Create child elements and set their text values
            success = ET.SubElement(root, "success")
            success.text = "true"

            result = ET.SubElement(root, "result")

            responseCode = ET.SubElement(result, "ResponseCode")
            responseCode.text = '00'

            responseDesc = ET.SubElement(result, "ResponseDesc")
            responseDesc.text = voucher.payment_state

            student_name = ET.SubElement(result, "student_name")
            student_name.text = voucher.student_id.first_name

            student_id = ET.SubElement(result, "student_id")
            student_id.text = str(voucher.student_id.id)

            dueDate = ET.SubElement(result, "DueDate")
            dueDate.text = f"{voucher.invoice_date_due.year}{voucher.invoice_date_due.month}{voucher.invoice_date_due.day}"

            amount_WID_Date = ET.SubElement(result, "Amount_WID_Date")
            amount_WID_Date.text = f"{voucher.amount_residual + amt:.2f}"

            amount_AD_Date = ET.SubElement(result, "Amount_AD_Date")
            amount_AD_Date.text = f"{voucher.amount_residual + amt:.2f}"


            billingMonth = ET.SubElement(result, "BillingMonth")
            billingMonth.text = f"{voucher.invoice_date_due.year}{voucher.invoice_date_due.month}{voucher.invoice_date_due.day}"
            remarks = ET.SubElement(result, "Remarks")
            remarks.text = 'Remarks'
            xml_response = ET.tostring(root, encoding="utf-16").decode("utf-16")
            response = request.make_response(xml_response, [('Content-Type', 'application/xml; charset=UTF-8')])
            response.content_type = 'application/xml'

            return response
        except Exception as e:
            resp = ET.Element("CityVoucherPAYResponse")
            success = ET.SubElement(resp, "success")
            success.text = "false"
            result = ET.SubElement(resp, "result")
            result.text = "Failed"
            code = ET.SubElement(resp, "StatusCode")
            code.text = "096"
            codeDescription = ET.SubElement(resp, "codeDescription")
            codeDescription.text = f"{e}"
            # Create an ElementTree object
            tree = ET.ElementTree(resp)
            # Generate the XML as a string
            xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")

            # Print the XML response
            print(xml_response)

            return json.dumps(xml_response)
        # except:
        #     print('fail')


    @http.route('/MBL_CMSCollection/post', type='http', auth='public', csrf=False, request_method='POST')
    def create_payment(self, **rec):
        # try:
        if 1==1:    
            xml_bytes = request.httprequest.data

            # Parse the XML data
            x = xml_bytes.decode("utf-8", errors="ignore")
            root = ET.fromstring(x)
            voucher_id = root.find('.//VoucherNumber').text
            token_id = root.find('.//Token').text
            amount = root.find('.//TransAmount').text
            resp = ET.Element("CityVoucherPAYResponse")
            success = ET.SubElement(resp, "success")
            success.text = "true"
            result = ET.SubElement(resp, "result")
            result.text = "Posted Successfully."
            code = ET.SubElement(resp, "code")
            code.text = "00"
            codeDescription = ET.SubElement(resp, "codeDescription")
            codeDescription.text = "Posted Successfully."

            voucher = request.env['account.move'].sudo().search([('name', '=', voucher_id)])

            if token_id != 'test_token':
                resp = ET.Element("CityVoucherPAYResponse")
                success = ET.SubElement(resp, "success")
                success.text = "false"
                result = ET.SubElement(resp, "result")
                result.text = "Failed"
                code = ET.SubElement(resp, "StatusCode")
                code.text = "093"
                codeDescription = ET.SubElement(resp, "codeDescription")
                codeDescription.text = "Authentication Token is invalid"
                # Create an ElementTree object
                tree = ET.ElementTree(resp)
                # Generate the XML as a string
                xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")

                # Print the XML response
                return json.dumps(xml_response)
            if not voucher:
                resp = ET.Element("CityVoucherPAYResponse")
                success = ET.SubElement(resp, "success")
                success.text = "false"
                result = ET.SubElement(resp, "result")
                result.text = "Failed"
                code = ET.SubElement(resp, "StatusCode")
                code.text = "091"
                codeDescription = ET.SubElement(resp, "codeDescription")
                codeDescription.text = "Voucher Id is invalid"
                xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")
                return json.dumps(xml_response)
            if voucher.payment_state == 'paid':
                resp = ET.Element("CityVoucherPAYResponse")
                success = ET.SubElement(resp, "success")
                success.text = "false"
                result = ET.SubElement(resp, "result")
                result.text = "Failed"
                code = ET.SubElement(resp, "StatusCode")
                code.text = "096"
                codeDescription = ET.SubElement(resp, "codeDescription")
                codeDescription.text = "Voucher is Already Paid"
                xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")
                return json.dumps(xml_response)
            # if voucher.invoice_date_due < date.today() and voucher.payment_state != 'partial' and not voucher.super_invoice:

            #     fee_st = request.env['fee.structure'].search([
            #         ('classes', '=', voucher.student_id.year_id.id),
            #         ('date_start', '<=', date.today()),
            #         ('date_end', '>=', date.today())
            #     ], limit=1)
            #     amt = int(fee_st.late_fee)
            amt = 0    
            requird_amount = f"{voucher.amount_residual}"

            if float(amount) != float(requird_amount):
                resp = ET.Element("CityVoucherPAYResponse")
                success = ET.SubElement(resp, "success")
                success.text = "false"
                result = ET.SubElement(resp, "result")
                result.text = "Failed"
                code = ET.SubElement(resp, "StatusCode")
                code.text = "096"
                codeDescription = ET.SubElement(resp, "codeDescription")
                codeDescription.text = "Amount Incorrect"
                xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")
                return json.dumps(xml_response)


            payment_wizard = request.env['account.move.history'].sudo().create({'xml_class_id':voucher.id})
            payment_wizard = request.env['account.move.history'].sudo().create({'xml_class_id':voucher.id})

            payment_wizard = request.env['account.payment.register'].sudo().create({'communication': voucher.id})
            payment_wizard.sudo().action_create_payments()
            voucher.sudo().payment_state = 'paid'
            # if voucher.invoice_date_due < date.today() and voucher.payment_state != 'partial' and not voucher.super_invoice:
            #     fee_st = request.env['fee.structure'].search([
            #         ('classes', '=', voucher.student_id.year_id.id),
            #         ('date_start', '<=', date.today()),
            #         ('date_end', '>=', date.today())
            #     ], limit=1)
            #     amt = int(fee_st.late_fee)

            #     if amt > 0:

            #         fine_invoic = request.env['account.move'].sudo().search([('super_invoice','=',voucher.id)])

            #         payment_wizard = request.env['account.move.history'].sudo().create({'xml_class_id': fine_invoic.id})
            #         payment_wizard = request.env['account.payment.register'].sudo().create({'communication': fine_invoic.id})
            #         payment_wizard.sudo().action_create_payments()
            #         fine_invoic.sudo().payment_state = 'paid'



            xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")

            # Print the XML response
            print(xml_response)

            return json.dumps(xml_response)

        # except Exception as e:
        #     resp = ET.Element("SAEPONVoucherPAYResponse")
        #     success = ET.SubElement(resp, "success")
        #     success.text = "false"
        #     result = ET.SubElement(resp, "result")
        #     result.text = "Failed"
        #     code = ET.SubElement(resp, "StatusCode")
        #     code.text = "096"
        #     codeDescription = ET.SubElement(resp, "codeDescription")
        #     codeDescription.text = f"{e}"
        #     xml_response = ET.tostring(resp, encoding="utf-16").decode("utf-16")

        #     # Print the XML response
        #     print(xml_response)

        #     return json.dumps(xml_response)
