# -*- coding: utf-8 -*-


from odoo import api, fields, models,_


class ResPartner(models.Model):
	_inherit = "res.partner"

	is_accountant = fields.Boolean("Is Accountant")
	accountant_per_id = fields.Many2one('res.partner',string="Accountant",domain=[('is_accountant','=',True)])

