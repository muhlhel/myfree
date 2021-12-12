# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InvoiceOrder(models.Model):

    _inherit = 'account.move'

    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(string=_("Amount In Words:"), compute='_compute_amount_in_word')

    # for KSA invoice
    narration = fields.Text(translate=True)

    delivery_date = fields.Date(string='Delivery Date', default=fields.Date.context_today, copy=False)
    show_delivery_date = fields.Boolean(compute='_compute_show_delivery_date')
    qr_code_str = fields.Char(string='Zatka QR Code', compute='_compute_qr_code_str')
    confirmation_datetime = fields.Datetime(string='Confirmation Date', readonly=True, copy=False)

    @api.depends('country_code', 'move_type')
    def _compute_show_delivery_date(self):
        for move in self:
            move.show_delivery_date = move.country_code == 'SA' and move.move_type in ('out_invoice', 'out_refund')

    @api.depends('amount_total', 'amount_untaxed', 'confirmation_datetime', 'company_id', 'company_id.vat')
    def _compute_qr_code_str(self):
        """ Generate the qr code for Saudi e-invoicing. Specs are available at the following link at page 23
        https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/20210528_ZATCA_Electronic_Invoice_Security_Features_Implementation_Standards_vShared.pdf
        """
        def get_qr_encoding(tag, field):
            company_name_byte_array = field.encode('UTF-8')
            company_name_tag_encoding = tag.to_bytes(length=1, byteorder='big')
            company_name_length_encoding = len(company_name_byte_array).to_bytes(length=1, byteorder='big')
            return company_name_tag_encoding + company_name_length_encoding + company_name_byte_array

        for record in self:
            qr_code_str = ''
            if record.confirmation_datetime and record.company_id.vat:
                seller_name_enc = get_qr_encoding(1, record.company_id.display_name)
                company_vat_enc = get_qr_encoding(2, record.company_id.vat)
                time_sa = fields.Datetime.context_timestamp(self.with_context(tz='Asia/Riyadh'), record.confirmation_datetime)
                timestamp_enc = get_qr_encoding(3, time_sa.isoformat())
                invoice_total_enc = get_qr_encoding(4, str(record.amount_total))
                total_vat_enc = get_qr_encoding(5, str(record.currency_id.round(record.amount_total - record.amount_untaxed)))

                str_to_encode = seller_name_enc + company_vat_enc + timestamp_enc + invoice_total_enc + total_vat_enc
                qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
            record.qr_code_str = qr_code_str

    def _post(self, soft=True):
        res = super()._post(soft)
        for record in self:
            if record.country_code == 'SA' and record.move_type in ('out_invoice', 'out_refund'):
                if not record.show_delivery_date:
                    raise UserError(_('Delivery Date cannot be empty'))
                if record.delivery_date < record.invoice_date:
                    raise UserError(_('Delivery Date cannot be before Invoice Date'))
                self.write({
                    'confirmation_datetime': fields.Datetime.now()
                })
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tax_amount = fields.Float(string='Tax Amount', compute='_compute_tax_amount', digits='Product Price')

    @api.depends('price_subtotal', 'price_total')
    def _compute_tax_amount(self):
        for record in self:
            record.tax_amount = record.price_total - record.price_subtotal
