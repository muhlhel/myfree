# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime
from odoo import api, fields, models, tools, _
import calendar
from odoo.exceptions import UserError, ValidationError
from collections import Counter


class CalculateCommissionMarketing(models.TransientModel):
    _inherit = 'create.commission.wiz'

    def generate_commission(self, commission_datain):
        #raise ValidationError(_("commission Marketing"))

        market = self.generate_marketing_person_commission()
        commission_data = Counter(market) + commission_datain
        super(CalculateCommissionMarketing, self).generate_commission(commission_data)

    def generate_marketing_person_commission(self):
        start, end = self.get_start_end_date()
        user_data = {}
        user_total = {}
        is_commisson_created = False

        comm_cal_on = self.env.user.company_id.comm_cal_on

        config_id = self.env['market.person.commission'].search([], order='id desc', limit=1)

        if not config_id:
            raise ValidationError(
                _("Please Do Marketing Person Commission Configuration under  Commission -> Configuration -> Marketing Commission."))
        pos_orders =[]
        '''
        pos_orders = self.env['pos.order'].search([
            ('date_order', '>=', str(start) + ' 00:00:00'),
            ('date_order', '<=', str(end) + ' 23:59:59'),
            ('state', 'in', ['paid', 'invoiced', 'done']),
        ])
        '''
        so = self.env['sale.order'].search([
            ('invoice_ids', 'not in', []),
            ('date_order', '>=', str(start) + ' 00:00:00'),
            ('date_order', '<=', str(end) + ' 23:59:59'),
            ('state', 'in', ['sale', 'done']),
        ])
        sale_orders = []
        for sale in so:
            for inv in sale.invoice_ids:
                if inv.state == 'posted' and sale not in sale_orders:
                    sale_orders.append(sale)

        for so_order in sale_orders:
            if so_order.marketing_per_id:
                user = so_order.marketing_per_id
            else:
                user = so_order.partner_id.marketing_per_id

            if user:
                uid = user.id
                comm_total = so_order.amount_total
                if comm_cal_on == 'untaxed':
                    comm_total = so_order.amount_untaxed

                if uid in user_data.keys():
                    user_total[uid] += comm_total

                    user_data[uid].update({
                        'name': user.name,
                        'partner': user,
                        'comm_total': user_data[uid].get('comm_total') + comm_total,
                        'config_id': config_id if config_id else user_data[uid].get('config_id'),
                    })
                else:
                    user_total.update({
                        uid: comm_total
                    })
                    user_data.update({
                        uid: {
                            'name': user.name,
                            'partner': user,
                            'comm_total': comm_total,
                            'config_id': config_id,
                        }
                    })

        for pos_order in pos_orders:
            if pos_order.marketing_per_id:
                user = pos_order.marketing_per_id
            else:
                user = pos_order.partner_id.marketing_per_id

            if user:
                uid = user.id
                comm_total = pos_order.amount_total
                if comm_cal_on == 'untaxed':
                    comm_total = pos_order.amount_total - pos_order.amount_tax

                if uid in user_data.keys():
                    user_total[uid] += comm_total

                    user_data[uid].update({
                        'name': user.name,
                        'partner': user,
                        'comm_total': user_data[uid].get('comm_total') + comm_total,
                        'config_id': config_id if config_id else user_data[uid].get('config_id'),
                    })
                else:
                    user_total.update({
                        uid: comm_total
                    })
                    user_data.update({
                        uid: {
                            'name': user.name,
                            'partner': user,
                            'comm_total': comm_total,
                            'config_id': config_id,
                        }
                    })

        for usr in user_data:
            line = user_data[usr]
            partner = line.get('partner')
            comm_total = line.get('comm_total')
            config_id = line.get('config_id')

            tp_amt = comm_total
            prev_comm = self.env['commission.base'].search([
                ('commission_date', '>=', start), ('commission_type', '=', 'market_person'),
                ('commission_date', '<=', end), ('sales_partner', '=', partner.id)])

            if prev_comm:
                prev_comm.unlink()

            if config_id:
                for c_line in config_id.commission_ids:
                    commission = 0.0
                    if (c_line.start_qty <= tp_amt and tp_amt <= c_line.end_qty) and (
                            c_line.start_qty <= comm_total and comm_total <= c_line.end_qty):
                        commission = tp_amt * c_line.ratio / 100
                        tp_amt = 0

                    elif c_line.end_qty <= comm_total and c_line.end_qty <= tp_amt:
                        gap = c_line.end_qty - c_line.start_qty + 1
                        commission = gap * c_line.ratio / 100
                        tp_amt = tp_amt - gap

                    elif (c_line.start_qty <= tp_amt and tp_amt <= c_line.end_qty) and c_line.end_qty <= comm_total:
                        gap = c_line.end_qty - c_line.start_qty + 1
                        commission = gap * c_line.ratio / 100
                        tp_amt = tp_amt - gap

                    elif tp_amt < c_line.start_qty and tp_amt < c_line.end_qty and c_line.end_qty <= comm_total:
                        gap = c_line.end_qty - c_line.start_qty + 1
                        commission = gap * c_line.ratio / 100
                        tp_amt = tp_amt - gap

                    elif tp_amt < c_line.start_qty and tp_amt < c_line.end_qty and (
                            c_line.start_qty <= comm_total and comm_total <= c_line.end_qty):
                        commission = tp_amt * c_line.ratio / 100
                        tp_amt = 0

                    else:
                        pass

                    if commission > 0:
                        self.env['commission.base'].create({
                            'commission_date': datetime.today().date(),
                            'sales_partner': partner.id,
                            'amount': commission,
                            'state': 'draft',
                            'comm_rate': c_line.ratio,
                            'commission_type': 'market_person',
                            'comm_total': comm_total,
                        })
                        is_commisson_created = True

        if is_commisson_created:
            return user_total
        else:
            return {}