# -*- coding: utf-8 -*-

from odoo import api, fields, models,_



class ResUsersInherited(models.Model):
	_inherit = "res.users"

	commission = fields.Float("Commission",related="partner_id.commission")
