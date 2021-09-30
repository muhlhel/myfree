# -*- coding: utf-8 -*-

from datetime import datetime, timedelta ,date
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)

class PosSalesCommission(models.Model):
	_name = 'commission.sheet'
	_order = "id desc"
	_description = 'Commission Sheet'

	def calc_total_sheet_amt(self):
		total = 0.0
		for am in self.commission_line_ids:
			total += am.amount
		self.update({'total_commission_amt': total})

	name = fields.Char('Name', default='New')
	sales_partner = fields.Many2one('res.partner', 'Sales Partner')
	start_date = fields.Date('Start Date')
	end_date = fields.Date('End Date', readonly='1')  # , compute='calc_commission_end_date' %H:%M:%S
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
	total_commission_amt = fields.Float('Total Commission Amount', compute='calc_total_sheet_amt')
	commission_paid = fields.Boolean('Commission Paid')
	commission_line_ids = fields.One2many('commission.base', 'commission_id', 'Commission Lines')
	state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('waiting', 'Waiting'), ('paid', 'Paid')],
							 default='draft', string='Commission Line Paid')
	invoice_id = fields.Many2one('account.move', 'Invoice')

	def action_view_invoice(self):
		return {
			'name': _('Invoice'),
			'view_mode': 'tree,form',
			'res_model': 'account.move',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', '=', self.invoice_id.id)],

		}

	def create_invoice_commission(self):

		invoice_obj = self.env['account.move']
		account = self.env.user.company_id.worksheet_account_id
		if not account:
			raise ValidationError(
				_("Please Do Account Configuration under Commission -> Configuration -> Settings."))

		for u in self:
			inv_create_obj = invoice_obj.create({
				'partner_id': u.sales_partner.id,
				'move_type': 'in_invoice',
				'commission_id': u.id,
				'invoice_line_ids': [(0, 0, {
					'name': 'Commission',
					'quantity': 1,
					'price_unit': u.total_commission_amt,
					'account_id': account.id,
				})]
			})

			u.update({'invoice_id': inv_create_obj.id, 'state': 'open'})

			return {
				'name': 'account.move.form',
				'res_model': 'account.move',
				'view_mode': 'form',
				'res_id': inv_create_obj.id,
				'target': 'current',
				'type': 'ir.actions.act_window'
			}

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('commission.sheet') or _('New')
		res = super(PosSalesCommission, self).create(vals)
		return res

