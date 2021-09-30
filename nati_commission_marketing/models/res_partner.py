# -*- coding: utf-8 -*-


from odoo import api, fields, models,_


class ResPartner(models.Model):
	_inherit = "res.partner"

	is_marketing = fields.Boolean("Is Marketing Person")
	marketing_per_id = fields.Many2one('res.partner',string="Marketing Person",domain=[('is_marketing','=',True)])

