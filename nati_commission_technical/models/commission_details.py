from datetime import datetime, timedelta ,date
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from collections import Counter

class CommissionDetails(models.Model):
	_inherit = 'commission.details'

	company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.company)
	tech_setting_id = fields.Many2one('tech.person.commission',string="Tech Person setting ")
