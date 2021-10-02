# -*- coding: utf-8 -*-

from datetime import datetime, timedelta ,date
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from collections import Counter 



class AccountantPersionCom(models.Model):
	_name = 'accountant.person.commission'
	_description = 'Accountant Commission'

	@api.model 
	def default_get(self, fields): 
		result = super(AccountantPersionCom, self).default_get(fields)

		config_id = self.sudo().search([],order='id desc', limit=1)
		result.update({ 
			'name': config_id.name or "Accountant Commission",
			'company_id': config_id.company_id.id, 
			'commission_ids': [(6,0,config_id.commission_ids.ids)] ,
		}) 
		return result

	name = fields.Char(string="Name",default='Accountant Commission Configuration')
	company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company)
	commission_ids = fields.One2many('commission.details','accountant_setting_id',string='Commission Details')
