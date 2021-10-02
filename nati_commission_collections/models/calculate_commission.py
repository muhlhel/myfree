# -*- coding: utf-8 -*-
from datetime import timedelta, date, datetime
from odoo import api, fields, models, tools, _
import calendar
from odoo.exceptions import UserError, ValidationError
from collections import Counter


class CalculateCommissionCollections(models.TransientModel):
    _inherit = 'create.commission.wiz'

    def generate_commission(self, commission_datain):

        collections = self.generate_colletions_commission()
        commission_data = Counter(collections) + commission_datain
        super(CalculateCommissionCollections, self).generate_commission(commission_data)


    def generate_colletions_commission(self):
        start, end = self.get_start_end_date()
        user_data = {}
        user_total = {}
        is_commisson_created = False
        comm_cal_on = self.env.user.company_id.comm_cal_on

        payments = self.env['account.payment'].search([
            ('date', '>=', str(start)),
            ('date', '<=', str(end)),
            ('partner_type', '=', 'customer'),
            ('state', 'not in', ['draft', 'cancelled']),
        ])

        for pymt in payments:
            if pymt.partner_id:
                if pymt.partner_id.user_id and pymt.sale_ref:
                    user = pymt.partner_id.user_id.name
                    uid = pymt.partner_id.user_id.partner_id.id

                    collections_total = pymt.amount
                    # if pymt.sale_ref:
                    collections_pricelist = pymt.sale_ref[0].pricelist_id
                    #by muhlhel
                    if comm_cal_on == 'untaxed':
                        collections_total = pymt.amount /1.15


                    if uid in user_data.keys():
                        user_total[uid] += collections_total
                        user_data[uid].update({
                            'name': user,
                            'partner': pymt.partner_id.user_id.partner_id,
                            'collections_total': user_data[uid].get('collections_total') + collections_total,
                            'collections_pricelist': collections_pricelist if collections_pricelist else user_data[uid].get(
                            'collections_pricelist'),
                        })
                    else:
                        user_total.update({
                            uid: collections_total
                        })
                        user_data.update({
                            uid: {
                                'name': user,
                                'partner': pymt.partner_id.user_id.partner_id,
                                'collections_total': collections_total,
                                'collections_pricelist': collections_pricelist,
                            }
                        })

        for usr in user_data:
            line = user_data[usr]
            partner = line.get('partner')
            collections_total = line.get('collections_total')
            collections_pricelist = line.get('collections_pricelist')
            is_cashier = line.get('is_cashier')

            w_amt = collections_total

            prev_comm = self.env['commission.base'].search([
                ('commission_date', '>=', start), ('commission_type', '=', 'collections'),
                ('commission_date', '<=', end), ('sales_partner', '=', partner.id)])

            if prev_comm:
                prev_comm.unlink()

            if collections_pricelist:
                for c_line in collections_pricelist.commission_ids:
                    commission = 0.0
                    if c_line.based_on and c_line.based_on == 'collections':
                        if (c_line.start_qty <= w_amt and w_amt <= c_line.end_qty) and (
                                c_line.start_qty <= collections_total and collections_total <= c_line.end_qty):
                            commission = w_amt * c_line.ratio / 100
                            w_amt = 0

                        elif c_line.end_qty <= collections_total and c_line.end_qty <= w_amt:
                            gap = c_line.end_qty - c_line.start_qty + 1
                            commission = gap * c_line.ratio / 100
                            w_amt = w_amt - gap

                        elif (
                                c_line.start_qty <= w_amt and w_amt <= c_line.end_qty) and c_line.end_qty <= collections_total:
                            gap = c_line.end_qty - c_line.start_qty + 1
                            commission = gap * c_line.ratio / 100
                            w_amt = w_amt - gap

                        elif w_amt < c_line.start_qty and w_amt < c_line.end_qty and c_line.end_qty <= collections_total:
                            gap = c_line.end_qty - c_line.start_qty + 1
                            commission = gap * c_line.ratio / 100
                            w_amt = w_amt - gap

                        elif w_amt < c_line.start_qty and w_amt < c_line.end_qty and (
                                c_line.start_qty <= collections_total and collections_total <= c_line.end_qty):
                            commission = w_amt * c_line.ratio / 100
                            w_amt = 0

                        else:
                            pass

                    if commission > 0:
                        self.env['commission.base'].create({
                            'commission_date': datetime.today().date(),
                            'sales_partner': partner.id,
                            'amount': commission,
                            'state': 'draft',
                            'pricelist_id': collections_pricelist.id,
                            'comm_rate': c_line.ratio,
                            'commission_type': 'collections',
                            'comm_total': collections_total,
                        })
                        is_commisson_created = True

        if is_commisson_created:
            return user_total
        else:
            return {}

