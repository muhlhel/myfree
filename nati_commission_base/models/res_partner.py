# -*- coding: utf-8 -*-


from odoo import api, fields, models,_




class ResPartnerInherited(models.Model):
	_inherit = "res.partner"

	commission = fields.Float("Commission",compute='_compute_user_commission')
	commission_line_ids = fields.One2many('commission.base','sales_partner', 'Commission Lines')

	def _compute_user_commission(self):
		for partner in self:
			partner.commission = 0.0
			for c_line in partner.commission_line_ids :
				partner.commission += c_line.amount