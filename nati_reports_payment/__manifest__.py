 # -*- coding: utf-8 -*-
{
    'name': "Nati Reports Payment",

    'summary': """
        Redesign of the Payment slip, keeping the official and modern look """,

    'description': """
Many modern designs and shapes, with additional features, 
for example: line numbers, numbers in words, compatibility with different printing options,
english and arabic lable,for both LTR and RTL
    """,
    'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'license': 'AGPL-3',
    'category': 'Accounting',
    'version': '15.0.0.0',
    'depends': ['account','nati_reports_base_style'],
    'qweb': [],
    'data': ['views/main_inherit.xml',
             'views/report_payment_receipt_modern.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'live_test_url': 'https://youtu.be/Ayy81m38QP8',

}