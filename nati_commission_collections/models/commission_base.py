from datetime import datetime, timedelta ,date
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from collections import Counter


class CommissionBaseCollections(models.Model):
    _inherit = 'commission.base'

    commission_type = fields.Selection(selection_add=[('collections', 'Collections')])






