# -*- coding: utf-8 -*-
{
    'name': "Nati Commission Base",

    'summary': """
    this is module base for many modules which use in calcutation commission""",

    'description': """
    this is module base for many modules which use in calcutation commission
    """,

    'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'license': 'LGPL-3',
    'version': '14.0.0.0',
    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Accounting/Accounting',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'views/commission_view.xml',
        'views/commission_sheet_view.xml',
        'views/res_config_settings_views.xml',
        'views/commission_menu.xml',
        'views/product_pricelist_view.xml',
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/crm_team_view.xml',
        'wizard/calculate_commission_view.xml',
        'data/data.xml',


    ],
    'application': True,
    'images': ['static/description/banner.png'],
    'installable': True,
}
