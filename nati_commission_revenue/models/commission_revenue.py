# -*- coding: utf-8 -*-
from datetime import datetime, timedelta ,date
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from collections import Counter 


class ProfitRules(models.Model):
	_name = 'commission.profit.rules'
	_description = 'Commission Profit Rules'

	start_qty = fields.Integer("Start Range")
	end_qty = fields.Integer("End Range")
	ratio = fields.Float("Commission(%)", digits='Commission',)
	revenue_setting_id = fields.Many2one('commission.revenue',string="Revenue setting ")

class RevenueCommission(models.Model):
	_name = 'commission.revenue'
	_description = 'Commission Revenue'

	@api.model 
	def default_get(self, fields): 
		result = super(RevenueCommission, self).default_get(fields)

		config_id = self.sudo().search([],order='id desc', limit=1)
		result.update({ 
			'name': config_id.name or "Sales Revenue Commission",
			'company_id': config_id.company_id.id, 
			'commission_ids': [(6,0,config_id.commission_ids.ids)] ,
			'profit_rules_ids': [(6,0,config_id.profit_rules_ids.ids)] ,
		}) 
		return result

	name = fields.Char(string="Name", default='Sales Revenue Commission Configuration')
	company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
	commission_ids = fields.One2many('commission.details', 'revenue_setting_id', string='Sales Rules')
	profit_rules_ids = fields.One2many('commission.profit.rules', 'revenue_setting_id', string='Profit Rules')

	