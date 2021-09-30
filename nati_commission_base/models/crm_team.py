# -*- coding: utf-8 -*-


from odoo import api, fields, models,tools, _


class SalesTeamInherit(models.Model):
	_inherit = "crm.team"

	commission_ids = fields.One2many('commission.details', 'sales_team_id',' Commission Details')