# -*- coding: utf-8 -*-

{
	"name" : "Nati Commission Revenue",
	"version" : "14.0.0.2",
	"category" : "",
	'summary': 'Nati Commission Revenue',
	"description": """
	Nati Commission Revenue	
	""",
	'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'version': '14.0.0.0',
	'license': 'LGPL-3',
	'category': 'Accounting/Accounting',

	# any module necessary for this one to work correctly
	'depends': ['base', 'sale', 'nati_commission_base'],
	"data": [
		'security/ir.model.access.csv',
		'views/commission_revenue_view.xml',
	],

    'images': ['static/description/banner.png'],
    'installable': True,
	'live_test_url': 'https://youtu.be/QlGb2BCWmu4',

}
