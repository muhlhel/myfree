# -*- coding: utf-8 -*-


from odoo import api, fields, models,tools, _


class ResCompanyInherit(models.Model):
	_inherit = 'res.company'

	commission_sheet_type = fields.Selection([('weekly','Weekly'),('month','Monthly')],string = 'Commission Type')
	comm_cal_on = fields.Selection([('taxed','Taxed Amount'),('untaxed','Untaxed Amount')],string = 'Commission Calculation On')
	worksheet_account_id = fields.Many2one('account.account',domain=[('internal_type','not in',['payable','receivable']),('deprecated', '=', False)],string='Expense Account for Worksheet')
