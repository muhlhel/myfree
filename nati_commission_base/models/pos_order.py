# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class PosOrderInherit(models.Model):
	_inherit = 'pos.order'

	is_commissioned = fields.Boolean("Is Commission Calculated")
