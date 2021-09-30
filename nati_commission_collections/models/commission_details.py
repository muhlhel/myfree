from datetime import datetime, timedelta ,date
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from collections import Counter

class CommissionDetails(models.Model):
	_inherit = 'commission.details'

	based_on = fields.Selection(selection_add=[('collections', 'Collections')])
