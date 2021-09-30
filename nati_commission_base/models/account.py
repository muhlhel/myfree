# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta ,date
import base64
import codecs
import urllib
import psycopg2
from dateutil.relativedelta import relativedelta
import calendar
from urllib.request import Request, urlopen
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class AccountMoveInherite(models.Model):
	_inherit = "account.move"

	commission_id = fields.Many2one('commission.sheet' , string = "Commission Invoice")

	def post(self):
		for move in self:
			if not move.line_ids.filtered(lambda line: not line.display_type):
				raise UserError(_('You need to add a line before posting.'))
			if move.auto_post and move.date > fields.Date.today():
				date_msg = move.date.strftime(self.env['res.lang']._lang_get(self.env.user.lang).date_format)
				raise UserError(_("This move is configured to be auto-posted on %s" % date_msg))

			if not move.partner_id:
				if move.is_sale_document():
					raise UserError(_("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
				elif move.is_purchase_document():
					raise UserError(_("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

			if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0, precision_rounding=move.currency_id.rounding) < 0:
				raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

			# Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
			# lines are recomputed accordingly.
			# /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
			# environment.
			if not move.invoice_date and move.is_invoice(include_receipts=True):
				move.invoice_date = fields.Date.context_today(self)
				move.with_context(check_move_validity=False)._onchange_invoice_date()

			# When the accounting date is prior to the tax lock date, move it automatically to the next available date.
			# /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
			# environment.
			if move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date:
				move.date = move.company_id.tax_lock_date + timedelta(days=1)
				move.with_context(check_move_validity=False)._onchange_currency()

		# Create the analytic lines in batch is faster as it leads to less cache invalidation.
		self.mapped('line_ids').create_analytic_lines()
		for move in self:
			if move.auto_post and move.date > fields.Date.today():
				raise UserError(_("This move is configured to be auto-posted on {}".format(move.date.strftime(self.env['res.lang']._lang_get(self.env.user.lang).date_format))))

			move.message_subscribe([p.id for p in [move.partner_id, move.commercial_partner_id] if p not in move.sudo().message_partner_ids])

			to_write = {'state': 'posted'}

			if move.name == '/':
				# Get the journal's sequence.
				sequence = move._get_sequence()
				if not sequence:
					raise UserError(_('Please define a sequence on your journal.'))

				# Consume a new number.
				to_write['name'] = sequence.next_by_id(sequence_date=move.date)

			move.write(to_write)

			if move:
				move.commission_id.update({
					'state':'waiting'
					})


			# Compute 'ref' for 'out_invoice'.
			if move.type == 'out_invoice' and not move.invoice_payment_ref:
				to_write = {
					'invoice_payment_ref': move._get_invoice_computed_reference(),
					'line_ids': []
				}
				for line in move.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
					to_write['line_ids'].append((1, line.id, {'name': to_write['invoice_payment_ref']}))
				move.write(to_write)


			if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
				# For opening moves, we set the reconciliation date threshold
				# to the move's date if it wasn't already set (we don't want
				# to have to reconcile all the older payments -made before
				# installing Accounting- with bank statements)
				move.company_id.account_bank_reconciliation_start = move.date

		for move in self:
			if not move.partner_id: continue
			if move.type.startswith('out_'):
				field='customer_rank'
			elif move.type.startswith('in_'):
				field='supplier_rank'
			else:
				continue
			try:
				with self.env.cr.savepoint():
					self.env.cr.execute("SELECT "+field+" FROM res_partner WHERE ID=%s FOR UPDATE NOWAIT", (move.partner_id.id,))
					self.env.cr.execute("UPDATE res_partner SET "+field+"="+field+"+1 WHERE ID=%s", (move.partner_id.id,))
					self.env.cache.remove(move.partner_id, move.partner_id._fields[field])
			except psycopg2.DatabaseError as e:
				if e.pgcode == '55P03':
					_logger.debug('Another transaction already locked partner rows. Cannot update partner ranks.')
					continue
				else:
					raise e

class AccountPaymentInherit(models.Model):
	_inherit = "account.payment"

	sale_ref = fields.Many2many('sale.order','Sale Ref',compute='_get_sale_ref')

	def _get_sale_ref(self):
		for pmnt in self:
			pmnt.sale_ref = [(6,0,[])]
			#by muhlhel from invoice_ids to reconciled_invoice_ids
			for inv in pmnt.reconciled_invoice_ids :
				if inv.invoice_origin :
					sale = self.env['sale.order'].search([('name','=',inv.invoice_origin)])
					if sale:
						pmnt.sale_ref = [(6,0,sale.ids)]
			
	def post(self):
		""" Create the journal items for the payment and update the payment's state to 'posted'.
			A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
			and another in the destination reconcilable account (see _compute_destination_account_id).
			If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
			If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
		"""
		AccountMove = self.env['account.move'].with_context(default_type='entry')
		for rec in self:

			if rec.state != 'draft':
				raise UserError(_("Only a draft payment can be posted."))

			if any(inv.state != 'posted' for inv in rec.invoice_ids):
				raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

			# keep the name in case of a payment reset to draft
			if not rec.name:
				# Use the right sequence to set the name
				if rec.payment_type == 'transfer':
					sequence_code = 'account.payment.transfer'
				else:
					if rec.partner_type == 'customer':
						if rec.payment_type == 'inbound':
							sequence_code = 'account.payment.customer.invoice'
						if rec.payment_type == 'outbound':
							sequence_code = 'account.payment.customer.refund'
					if rec.partner_type == 'supplier':
						if rec.payment_type == 'inbound':
							sequence_code = 'account.payment.supplier.refund'
						if rec.payment_type == 'outbound':
							sequence_code = 'account.payment.supplier.invoice'
				rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
				if not rec.name and rec.payment_type != 'transfer':
					raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

			moves = AccountMove.create(rec._prepare_payment_moves())
			moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

			# Update the state / move before performing any reconciliation.
			move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
			rec.write({'state': 'posted', 'move_name': move_name})

			if rec.payment_type in ('inbound', 'outbound'):
				# ==== 'inbound' / 'outbound' ====
				if rec.invoice_ids:
					(moves[0] + rec.invoice_ids).line_ids \
						.filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id)\
						.reconcile()
			elif rec.payment_type == 'transfer':
				# ==== 'transfer' ====
				moves.mapped('line_ids')\
					.filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
					.reconcile()

			for i in rec.invoice_ids:
				if i.invoice_payment_state == "paid":
					i.commission_id.update({
						'commission_paid':True,
						'state' : 'paid'
						})
					for j in i.commission_id.commission_line_ids:
						j.update({
							'state':'paid'
							})

		return True	


