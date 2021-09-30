# -*- coding: utf-8 -*-

{
	"name" : "Nati Commission Collections",
	"version" : "14.0.0.2",
	"category" : "",
	'summary': 'Nati Commission Collections',
	"description": """
	Nati Commission Collections	
	""",
	'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'version': '14.0.0.0',
	'license': 'LGPL-3',
	'category': 'Accounting/Accounting',

	# any module necessary for this one to work correctly
	'depends': ['base', 'sale', 'nati_commission_base',],
	"data": [
		'security/ir.model.access.csv',
		'views/commission_collections_view.xml',
	],

    'images': ['static/description/banner.png'],
    'installable': True,
}
