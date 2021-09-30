# -*- coding: utf-8 -*-


from odoo import api, fields, models,tools, _



class ProductPricelistInherit(models.Model):
	_inherit = "product.pricelist"

	commission_for = fields.Selection([('products','Products'),('wholesale','Wholesaller')],"Commission for")
	commission_ids = fields.One2many('commission.details','pricelist_id','Commission Details')

