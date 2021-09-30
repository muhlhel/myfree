# -*- coding: utf-8 -*-

{
	"name" : "Nati Commission Marketing",
	'summary': 'Nati Commission Marketing',
	"description": """
	Nati Commission Marketing
	""",
	'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'version': '14.0.0.0',
	'category': 'Accounting/Accounting',
	'license': 'LGPL-3',
	"depends" : ['base','sale','nati_commission_base'],
	"data": [
		'security/ir.model.access.csv',
		'views/commission_marketing_view.xml',
		'views/res_partner_view.xml',
		'views/res_partner_marketing.xml',
		'views/sale_order_view.xml',
	],

	'images': ['static/description/banner.png'],
	'installable': True,
}
