# -*- coding: utf-8 -*-

from odoo import api, fields, models,tools, _


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    marketing_per_id = fields.Many2one('res.partner', string="Marketing Person")

    @api.onchange('partner_id')
    def oc_partner(self):
        self.update({
            'marketing_per_id': self.partner_id.marketing_per_id.id
        })
