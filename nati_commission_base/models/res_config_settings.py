# -*- coding: utf-8 -*-


from odoo import models, fields, api


class ResConfigSettingInherited(models.TransientModel):
	_inherit = 'res.config.settings'

	commission_sheet_type = fields.Selection([('weekly','Weekly'),('month','Monthly')],string = 'Commission Type',related="company_id.commission_sheet_type",readonly=False)
	comm_cal_on = fields.Selection([('taxed','Taxed Amount'),('untaxed','Untaxed Amount')],string = 'Commission Calculation On',related="company_id.comm_cal_on",readonly=False)
	worksheet_account_id = fields.Many2one('account.account',string='Expense Account for Worksheet',related="company_id.worksheet_account_id",readonly=False,domain=[('internal_type','not in',['payable','receivable']),('deprecated', '=', False)])
