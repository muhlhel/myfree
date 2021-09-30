# -*- coding: utf-8 -*-

{
	"name" : "Nati Commission Accountant",
	'summary': 'Nati Commission Acountant',
	"description": """
	Nati Commission Acountant
	""",
	'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'version': '14.0.0.0',
	'category': 'Accounting/Accounting',
	'license': 'LGPL-3',
	"depends" : ['base','sale','nati_commission_base'],
	"data": [
		'security/ir.model.access.csv',
		'views/commission_accountant_view.xml',
		'views/res_partner_view.xml',
		'views/res_partner_accountant.xml',
		'views/sale_order_view.xml',
	],

	'images': ['static/description/banner.png'],
	'installable': True,
}
