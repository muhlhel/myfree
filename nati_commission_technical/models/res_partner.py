# -*- coding: utf-8 -*-


from odoo import api, fields, models,_


class ResPartner(models.Model):
	_inherit = "res.partner"

	is_technical = fields.Boolean("Is Technical Person")
	technical_per_id = fields.Many2one('res.partner',string="Technical Person",domain=[('is_technical','=',True)])

