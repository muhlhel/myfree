# -*- coding: utf-8 -*-

from odoo import api, fields, models,tools, _


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    cashier_id = fields.Many2one('res.users', string="Cashier",compute="_compute_cashier_id")


    def _compute_cashier_id(self):
        for rec in self:
            rec.cashier_id = rec.user_id