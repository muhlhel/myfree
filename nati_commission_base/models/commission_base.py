# -*- coding: utf-8 -*-

from datetime import datetime, timedelta ,date
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)



class CommissionBase(models.Model):
	_name = 'commission.base'
	_description = 'Commission Base Data'

	commission_date = fields.Date('Commission Date')
	sales_partner = fields.Many2one('res.partner', 'Sales Partner')
	source = fields.Char('Source Document')
	amount = fields.Float('Amount', digits='Product Price')
	state = fields.Selection([('draft','Draft'),('waiting','Waiting'),('paid','Paid')], default='draft', string='Commission Line Paid')
	qty = fields.Float('Quantity')
	pricelist_id = fields.Many2one('product.pricelist',string="Pricelist")
	comm_rate = fields.Float('Commission Rate (%)', digits='Commission')
	commission_type = fields.Selection([('products','Sales Products'),('team_leader','Sales Teams Leader')],string='Commission Line For')
	product_id = fields.Many2one('product.product',string="Product")
	sales_team_id = fields.Many2one("crm.team",'Sales Team')
	comm_total = fields.Float("Total Amount")
	commission_id = fields.Many2one('commission.sheet', 'Commission Sheet')
