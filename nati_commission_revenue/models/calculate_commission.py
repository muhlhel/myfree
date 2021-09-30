# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime
from odoo import api, fields, models, tools, _
import calendar
from odoo.exceptions import UserError, ValidationError
from collections import Counter


class CalculateCommissionRevenue(models.TransientModel):
    _inherit = 'create.commission.wiz'

    def generate_commission(self, commission_datain):

        revenue = self.generate_revenue_commission()
        commission_data = Counter(revenue) + commission_datain
        super(CalculateCommissionRevenue, self).generate_commission(commission_data)


    def generate_revenue_commission(self):
        start, end = self.get_start_end_date()
        user_data = {}
        user_total = {}
        is_commisson_created = False

        comm_cal_on = self.env.user.company_id.comm_cal_on

        config_id = self.env['commission.revenue'].search([], order='id desc', limit=1)

        if not config_id:
            raise ValidationError(
                _("Please Do Sales Revenue Commission Configuration under  Sales -> Configuration -> Sales Revenue Configuration."))
        pos_orders = []

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
            user = so_order.user_id.partner_id
            if user:
                uid = user.id
                #By Muhlhel
                #comm_total = so_order.amount_total
                comm_total = so_order.amount_untaxed

                #if comm_cal_on == 'untaxed':
                    #comm_total = so_order.amount_untaxed
                cost = 0

                for line in so_order.order_line:
                    if line.product_id:
                        cost += (line.product_id.standard_price * line.product_uom_qty)

                if uid in user_data.keys():
                    user_data[uid].update({
                        'name': user.name,
                        'partner': user,
                        'comm_total': user_data[uid].get('comm_total') + comm_total,
                        'cost': user_data[uid].get('cost') + cost,
                        'config_id': config_id if config_id else user_data[uid].get('config_id'),
                    })
                else:
                    user_data.update({
                        uid: {
                            'name': user.name,
                            'partner': user,
                            'comm_total': comm_total,
                            'config_id': config_id,
                            'cost': cost,
                        }
                    })

        for pos_order in pos_orders:
            user = pos_order.user_id.partner_id
            if user:
                uid = user.id
                comm_total = pos_order.amount_total
                if comm_cal_on == 'untaxed':
                    comm_total = pos_order.amount_total - pos_order.amount_tax

                cost = 0
                for line in pos_order.lines:
                    if line.product_id:
                        cost += (line.product_id.standard_price * line.qty)

                if uid in user_data.keys():
                    user_data[uid].update({
                        'name': user.name,
                        'partner': user,
                        'comm_total': user_data[uid].get('comm_total') + comm_total,
                        'cost': user_data[uid].get('cost') + cost,
                        'config_id': config_id if config_id else user_data[uid].get('config_id'),
                    })
                else:
                    user_data.update({
                        uid: {
                            'name': user.name,
                            'partner': user,
                            'comm_total': comm_total,
                            'config_id': config_id,
                            'cost': cost,
                        }
                    })

        for usr in user_data:
            line = user_data[usr]
            partner = line.get('partner')
            comm_total = line.get('comm_total')
            config_id = line.get('config_id')
            cost = line.get('cost')
            cmnsn = 0

            div = cost if cost > 0 else 100
            profit = round(((comm_total - cost) * 100) / div, 2)

            prev_comm = self.env['commission.base'].search([
                ('commission_date', '>=', start), ('commission_type', 'in', ['profit_revenue', 'sales_revenue']),
                ('commission_date', '<=', end), ('sales_partner', '=', partner.id)])

            if prev_comm:
                prev_comm.unlink()

            if config_id:
                for c_line in config_id.commission_ids:
                    if comm_total >= c_line.start_qty and comm_total <= c_line.end_qty:
                        commission = comm_total * c_line.ratio / 100
                        cmnsn = commission
                        if commission > 0:
                            self.env['commission.base'].create({
                                'commission_date': datetime.today().date(),
                                'sales_partner': partner.id,
                                'amount': commission,
                                'state': 'draft',
                                'comm_rate': c_line.ratio,
                                'commission_type': 'sales_revenue',
                                'comm_total': comm_total,
                            })
                            is_commisson_created = True
                            user_total[uid] = comm_total

                for pr_line in config_id.profit_rules_ids:
                    if profit >= pr_line.start_qty and profit <= pr_line.end_qty:
                        commission = cmnsn * pr_line.ratio / 100
                        if commission > 0:
                            self.env['commission.base'].create({
                                'commission_date': datetime.today().date(),
                                'sales_partner': partner.id,
                                'amount': commission,
                                'state': 'draft',
                                'comm_rate': pr_line.ratio,
                                'commission_type': 'profit_revenue',
                                'comm_total': comm_total,
                            })

        if is_commisson_created:
            return user_total
        else:
            return {}
