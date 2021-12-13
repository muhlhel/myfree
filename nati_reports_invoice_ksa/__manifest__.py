 # -*- coding: utf-8 -*-
{
    'name': "K.S.A - E-Invoice",

    'summary': """
        الفاتورة الالكترونية """,

    'description': """
Many modern designs and shapes, with additional features, 
for example: line numbers, numbers in words, compatibility with different printing options,
english and arabic lable,for both LTR and RTL
    """,
    'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'license': 'AGPL-3',
    'version': '15.0.0.0',
    'depends': ['account','nati_reports_base_style'],
    'qweb': [],
    'data': ['views/main_inherit.xml',
             'views/report_invoice_modern.xml',
             'views/view_move_form.xml',
             ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'live_test_url': 'https://youtu.be/nApyIVAg7kc',


}