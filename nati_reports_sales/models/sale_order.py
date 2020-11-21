# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from datetime import datetime
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(string=_("Amount In Words:"), compute='_compute_amount_in_word')