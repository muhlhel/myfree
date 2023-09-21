 # -*- coding: utf-8 -*-
{
    'name': "Nati Reports Invoice",

    'summary': """
        Redesign of the Invoice, keeping the official and modern look """,

    'description': """
Many modern designs and shapes, with additional features, 
for example: line numbers, numbers in words, compatibility with different printing options,
english and arabic lable,for both LTR and RTL
    """,
    'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'license': 'AGPL-3',
    'category': 'Accounting',
    'version': '1.16',
    'depends': ['account','nati_reports_base_style'],
    'qweb': [],
    'data': ['views/main_inherit.xml',
             'views/report_invoice_modern.xml',
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'live_test_url': 'https://youtu.be/Ayy81m38QP8',

}