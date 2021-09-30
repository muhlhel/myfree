# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date, datetime
from odoo import api, fields, models, tools, _
import calendar
from odoo.exceptions import UserError, ValidationError
from collections import Counter


class CalculateCommissionBase(models.TransientModel):
    _name = 'create.commission.wiz'
    _description = 'calculate commission wiz'

    start_dt = fields.Date('Start Date', required=True)
    end_dt = fields.Date('End Date', required=True)

    @api.model
    def default_get(self, fields):
        res = super(CalculateCommissionBase, self).default_get(fields)
        start, end = self.get_default_start_end_date()
        res.update({
            'start_dt': start,
            'end_dt': end
        })
        return res

    def get_default_start_end_date(self):
        commission_sheet_type = self.env.user.company_id.commission_sheet_type
        comm_cal_on = self.env.user.company_id.comm_cal_on
        worksheet_account_id = self.env.user.company_id.worksheet_account_id

        today = datetime.now().date()
        if (not worksheet_account_id) or (not commission_sheet_type) or (not comm_cal_on):
            raise ValidationError(
                _("Please Do Commission Configuration under Commission -> Configuration -> Settings."))

        start = False
        end = False
        if commission_sheet_type == 'weekly':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)

        if commission_sheet_type == 'month':
            last_day_of_month = calendar.monthrange(today.year, today.month)[1]
            start = str(today.year) + "-" + str(today.month) + "-1"
            end = str(today.year) + "-" + str(today.month) + "-" + str(last_day_of_month)

        return [start, end]

    def get_start_end_date(self):
        return [self.start_dt, self.end_dt]


    def generate_products_commission(self):
        start, end = self.get_start_end_date()
        comm_cal_on = self.env.user.company_id.comm_cal_on
        user_data = {}
        user_total = {}
        is_commisson_created = False
        '''
        pos_orders = self.env['pos.order'].search([
            ('date_order', '>=', str(start) + ' 00:00:00'),
            ('date_order', '<=', str(end) + ' 23:59:59'),
            ('state', 'in', ['paid', 'invoiced', 'done']),
        ])
        '''
        pos_orders = []
        so = self.env['sale.order'].search([
            ('invoice_ids', 'not in', []),
            ('cashier_id', '!=', False),
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
            if so_order.cashier_id:
                for line in so_order.order_line:
                    user = so_order.cashier_id.partner_id.id
                    products_qty = 0
                    products_total = 0
                    products_pricelist = so_order.pricelist_id
                    for c_line in products_pricelist.commission_ids:
                        if c_line.based_on and c_line.based_on == 'product':
                            if line.product_id.id in c_line.comm_product_ids.ids:
                                products_qty = line.product_uom_qty
                                if comm_cal_on == 'untaxed':
                                    products_total = line.price_subtotal
                                else:
                                    products_total = line.price_total

                        elif c_line.based_on and c_line.based_on == 'categ':
                            if line.product_id.categ_id.id in c_line.comm_product_categ_ids.ids:
                                products_qty = line.product_uom_qty
                                if comm_cal_on == 'untaxed':
                                    products_total = line.price_subtotal
                                else:
                                    products_total = line.price_total

                    prod = line.product_id.display_name
                    if products_total > 0:
                        if user in user_data.keys():
                            user_total[user] += products_total

                            for i in user_data[user]:
                                if i == prod:
                                    old_prod = user_data[user][i]
                                    user_data[user][i].update({
                                        'product_id': line.product_id,
                                        'name': so_order.cashier_id.name,
                                        'partner': so_order.cashier_id.partner_id,
                                        'products_qty': products_qty + old_prod.get('products_qty'),
                                        'products_total': products_total + old_prod.get('products_total'),
                                        'products_pricelist': products_pricelist,
                                    })
                            if not any(prod in d for d in user_data[user]):
                                user_data[user][prod] = {
                                    'product_id': line.product_id,
                                    'name': so_order.cashier_id.name,
                                    'partner': so_order.cashier_id.partner_id,
                                    'products_qty': products_qty,
                                    'products_total': products_total,
                                    'products_pricelist': products_pricelist,
                                }
                        else:
                            user_total.update({
                                user: products_total
                            })
                            user_data.update({
                                user: {
                                    prod: {
                                        'product_id': line.product_id,
                                        'name': so_order.cashier_id.name,
                                        'partner': so_order.cashier_id.partner_id,
                                        'products_qty': products_qty,
                                        'products_total': products_total,
                                        'products_pricelist': products_pricelist,
                                    }
                                }
                            })

        for pos_order in pos_orders:
            for line in pos_order.lines:
                user = pos_order.user_id.partner_id.id
                products_qty = 0
                products_total = 0
                products_pricelist = pos_order.pricelist_id

                for c_line in products_pricelist.commission_ids:
                    if c_line.based_on and c_line.based_on == 'product':
                        if line.product_id.id in c_line.comm_product_ids.ids:
                            products_qty = line.qty
                            if comm_cal_on == 'untaxed':
                                products_total = line.price_subtotal
                            else:
                                products_total = line.price_subtotal_incl

                    elif c_line.based_on and c_line.based_on == 'categ':
                        if line.product_id.categ_id.id in c_line.comm_product_categ_ids.ids:
                            products_qty = line.qty
                            if comm_cal_on == 'untaxed':
                                products_total = line.price_subtotal
                            else:
                                products_total = line.price_subtotal_incl

                prod = line.product_id.display_name
                if products_total > 0:
                    if user in user_data.keys():
                        user_total[user] += products_total
                        for i in user_data[user]:
                            if i == prod:
                                old_prod = user_data[user][i]
                                user_data[user][i].update({
                                    'product_id': line.product_id,
                                    'name': pos_order.user_id.name,
                                    'partner': pos_order.user_id.partner_id,
                                    'products_qty': products_qty + old_prod.get('products_qty'),
                                    'products_total': products_total + old_prod.get('products_total'),
                                    'products_pricelist': products_pricelist,
                                })
                        if not any(prod in d for d in user_data[user]):
                            user_data[user][prod] = {
                                'product_id': line.product_id,
                                'name': pos_order.user_id.name,
                                'partner': pos_order.user_id.partner_id,
                                'products_qty': products_qty,
                                'products_total': products_total,
                                'products_pricelist': products_pricelist,
                            }
                    else:
                        user_total.update({
                            user: products_total
                        })
                        user_data.update({
                            user: {
                                prod: {
                                    'product_id': line.product_id,
                                    'name': pos_order.user_id.name,
                                    'partner': pos_order.user_id.partner_id,
                                    'products_qty': products_qty,
                                    'products_total': products_total,
                                    'products_pricelist': products_pricelist,
                                }
                            }
                        })

        for usr in user_data:
            lines = user_data[usr]
            prev_comm = self.env['commission.base'].search([
                ('commission_date', '>=', start), ('commission_type', '=', 'products'),
                ('commission_date', '<=', end), ('sales_partner', '=', usr)])

            if prev_comm:
                prev_comm.unlink()

            for prd in lines:
                partner = lines[prd].get('partner')
                products_qty = lines[prd].get('products_qty')
                products_total = lines[prd].get('products_total')
                products_pricelist = lines[prd].get('products_pricelist')
                product = lines[prd].get('product_id')

                r_qty = products_qty
                r_amt = products_total

                used_qty = 0
                single_prod_price = 0
                if products_qty > 0 and products_total > 0:
                    single_prod_price = products_total / products_qty

                if products_pricelist:
                    for c_line in products_pricelist.commission_ids:
                        commission = 0.0
                        if c_line.based_on and c_line.based_on == 'product':
                            if product.id in c_line.comm_product_ids.ids:
                                if (c_line.start_qty <= r_qty and r_qty <= c_line.end_qty) and (
                                        c_line.start_qty <= products_qty and products_qty <= c_line.end_qty):
                                    total_amount_per_qty = r_qty * single_prod_price
                                    commission = total_amount_per_qty * c_line.ratio / 100
                                    used_qty = r_qty
                                    r_qty = 0

                                elif c_line.end_qty <= products_qty and c_line.end_qty <= r_qty:
                                    gap = c_line.end_qty - c_line.start_qty + 1
                                    total_amount_per_qty = gap * single_prod_price
                                    commission = total_amount_per_qty * c_line.ratio / 100
                                    r_qty = r_qty - gap
                                    used_qty = gap

                                elif (
                                        c_line.start_qty <= r_qty and r_qty <= c_line.end_qty) and c_line.end_qty <= products_qty:
                                    gap = c_line.end_qty - c_line.start_qty + 1
                                    total_amount_per_qty = gap * single_prod_price
                                    commission = total_amount_per_qty * c_line.ratio / 100
                                    r_qty = r_qty - gap
                                    used_qty = gap

                                elif r_qty < c_line.start_qty and r_qty < c_line.end_qty and c_line.end_qty <= products_qty:
                                    gap = c_line.end_qty - c_line.start_qty + 1
                                    total_amount_per_qty = gap * single_prod_price
                                    commission = total_amount_per_qty * c_line.ratio / 100
                                    r_qty = r_qty - gap
                                    used_qty = gap

                                elif r_qty < c_line.start_qty and r_qty < c_line.end_qty and (
                                        c_line.start_qty <= products_qty and products_qty <= c_line.end_qty):
                                    total_amount_per_qty = r_qty * single_prod_price
                                    commission = total_amount_per_qty * c_line.ratio / 100
                                    used_qty = r_qty
                                    r_qty = 0

                                else:
                                    pass

                        elif c_line.based_on and c_line.based_on == 'categ':
                            if product.categ_id.id in c_line.comm_product_categ_ids.ids:
                                if (c_line.start_qty <= r_qty and r_qty <= c_line.end_qty) and (
                                        c_line.start_qty <= products_qty and products_qty <= c_line.end_qty):
                                    total_amount_per_qty = r_qty * single_prod_price
                                    commission = total_amount_per_qty * c_line.ratio / 100
                                    used_qty = r_qty
                                    r_qty = 0

                                elif c_line.end_qty <= products_qty and c_line.end_qty <= r_qty:
                                    gap = c_line.end_qty - c_line.start_qty + 1
                                    total_amount_per_qty = gap * single_prod_price
                                    commission = total_amount_per_qty * c_line.ratio / 100
                                    r_qty = r_qty - gap
                                    used_qty = gap

                                elif (
                                        c_line.start_qty <= r_qty and r_qty <= c_line.end_qty) and c_line.end_qty <= products_qty:
                                    gap = c_line.end_qty - c_line.start_qty + 1
                                    total_amount_per_qty = gap * single_prod_price
                                    commission = total_amount_per_qty * c_line.ratio / 100
                                    r_qty = r_qty - gap
                                    used_qty = gap

                                elif r_qty < c_line.start_qty and r_qty < c_line.end_qty and c_line.end_qty <= products_qty:
                                    gap = c_line.end_qty - c_line.start_qty + 1
                                    total_amount_per_qty = gap * single_prod_price
                                    commission = total_amount_per_qty * c_line.ratio / 100
                                    r_qty = r_qty - gap
                                    used_qty = gap

                                elif r_qty < c_line.start_qty and r_qty < c_line.end_qty and (
                                        c_line.start_qty <= products_qty and products_qty <= c_line.end_qty):
                                    total_amount_per_qty = r_qty * single_prod_price
                                    commission = total_amount_per_qty * c_line.ratio / 100
                                    used_qty = r_qty
                                    r_qty = 0
                                else:
                                    pass
                        else:
                            pass

                        if commission > 0:
                            self.env['commission.base'].create({
                                'commission_date': datetime.today().date(),
                                'sales_partner': partner.id,
                                'amount': commission,
                                'state': 'draft',
                                'qty': used_qty,
                                'pricelist_id': products_pricelist.id,
                                'comm_rate': c_line.ratio,
                                'commission_type': 'products',
                                'product_id': product.id,
                                'comm_total': products_total,
                            })
                            is_commisson_created = True

        if is_commisson_created:
            return user_total
        else:
            return {}

    def generate_team_manager_commission(self, commission_data):
        start, end = self.get_start_end_date()

        new_data = commission_data
        new_data = dict(new_data)

        user_data = {}
        comm_obj = self.env['commission.base']
        sales_teams = self.env['crm.team'].search([])

        for tm in sales_teams:
            if tm.user_id:
                user = tm.user_id.id
                total = 0
                for member in tm.member_ids:
                    if member.partner_id.id in new_data:
                        total += new_data[member.partner_id.id]

                if user in user_data.keys():
                    user_data[user].update({
                        'name': tm.user_id.name,
                        'partner': tm.user_id.partner_id,
                        'total': user_data[user].get('total') + total,
                        'sales_team': tm,
                    })
                else:
                    user_data.update({
                        user: {
                            'name': tm.user_id.name,
                            'partner': tm.user_id.partner_id,
                            'total': total,
                            'sales_team': tm,
                        }
                    })

        for usr in user_data:
            line = user_data[usr]
            partner = line.get('partner')
            leader_total = line.get('total')
            name = line.get('name')
            sales_team = line.get('sales_team', False)

            w_amt = leader_total

            prev_comm = self.env['commission.base'].search([
                ('commission_date', '>=', start), ('commission_type', '=', 'team_leader'),
                ('commission_date', '<=', end), ('sales_partner', '=', partner.id)])
            if prev_comm:
                prev_comm.unlink()

            if sales_team:
                for c_line in sales_team.commission_ids:
                    commission = 0.0
                    if (c_line.start_qty <= w_amt and w_amt <= c_line.end_qty) and (
                            c_line.start_qty <= leader_total and leader_total <= c_line.end_qty):
                        commission = w_amt * c_line.ratio / 100
                        w_amt = 0

                    elif c_line.end_qty <= leader_total and c_line.end_qty <= w_amt:
                        gap = c_line.end_qty - c_line.start_qty + 1
                        commission = gap * c_line.ratio / 100
                        w_amt = w_amt - gap

                    elif (c_line.start_qty <= w_amt and w_amt <= c_line.end_qty) and c_line.end_qty <= leader_total:
                        gap = c_line.end_qty - c_line.start_qty + 1
                        commission = gap * c_line.ratio / 100
                        w_amt = w_amt - gap


                    elif w_amt < c_line.start_qty and w_amt < c_line.end_qty and c_line.end_qty <= leader_total:
                        gap = c_line.end_qty - c_line.start_qty + 1
                        commission = gap * c_line.ratio / 100
                        w_amt = w_amt - gap

                    elif w_amt < c_line.start_qty and w_amt < c_line.end_qty and (
                            c_line.start_qty <= leader_total and leader_total <= c_line.end_qty):
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
                            'sales_team_id': sales_team.id,
                            'comm_rate': c_line.ratio,
                            'commission_type': 'team_leader',
                        })

    def generate_commission_and_sheet(self):

        cashier = self.generate_products_commission()
        commission_data = Counter(cashier)
        self.generate_commission(commission_data)
        self.create_commission_worksheet()

    def generate_commission(self, commission_data):
        #raise ValidationError( _("commission base"))
        self.generate_team_manager_commission(commission_data)

    def create_commission_worksheet(self):
        start, end = self.get_start_end_date()
        today_date = datetime.now().date()

        commission_line_obj = self.env['commission.base'].search([])
        commission_sheet_obj = self.env['commission.sheet']
        partner_obj = self.env['res.partner'].search([])

        for p in partner_obj:
            if len(p.commission_line_ids) != 0:
                comm_line = p.commission_line_ids.search([('state', '=', 'draft'),
                                                          ('sales_partner', '=', p.id),
                                                          ('commission_date', '>=', start),
                                                          ('commission_date', '<=', end)])
                for m in comm_line:
                    sheet_id = commission_sheet_obj.search([('sales_partner', '=', p.id),
                                                            ('start_date', '=', str(start))])
                    if not sheet_id:
                        sheet_id = commission_sheet_obj.create({'sales_partner': p.id,
                                                                'start_date': str(start),
                                                                'end_date': str(end)})
                    m.update({'commission_id': sheet_id.id,
                              'state': 'waiting'})