# -*- coding: utf-8 -*-

{
	"name" : "Nati Commission Technical",
	'summary': 'Nati Commission Technical',
	"description": """
	Nati Commission Technical
	""",
	'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'version': '14.0.0.0',
	'category': 'Accounting/Accounting',
	'license': 'LGPL-3',
	"depends" : ['nati_commission_base'],
	"data": [
		'security/ir.model.access.csv',
		'views/commission_technical_view.xml',
		'views/res_partner_view.xml',
		'views/res_partner_technical.xml',
		'views/sale_order_view.xml',
	],

	'images': ['static/description/banner.png'],
	'installable': True,
	'live_test_url': 'https://youtu.be/icYPLz2FbR8',

}
