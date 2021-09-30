# -*- coding: utf-8 -*-

from datetime import datetime, timedelta ,date
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)


class ProductsQtyPrice(models.Model):
	_name = 'commission.details'
	_description = 'commission details'
	_order = "sequence"

	sequence = fields.Integer('Sequence', default=10)
	start_qty = fields.Integer("From")
	end_qty = fields.Integer("To")
	ratio = fields.Float("(%)", digits='Commission', )
	pricelist_id = fields.Many2one("product.pricelist", 'pricelist')
	based_on = fields.Selection([('product', 'Product'), ('categ', 'Category')],
								string='Based On')
	comm_product_categ_ids = fields.Many2many('product.category', string="Products Category")
	comm_product_ids = fields.Many2many('product.product', string="Products")
	sales_team_id = fields.Many2one("crm.team", 'Sales Team')



