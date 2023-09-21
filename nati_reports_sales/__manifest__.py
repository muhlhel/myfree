 # -*- coding: utf-8 -*-
{
    'name': "Nati Reports Sales",

    'summary': """
        Redesign of the Quotation and Order, keeping the official and modern look """,

    'description': """
Many modern designs and shapes, with additional features, 
for example: line numbers, numbers in words, compatibility with different printing options,
english and arabic lable,for both LTR and RTL
    """,
    'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'license': 'AGPL-3',
    'category': 'Sales',
    'version': '1.16',
    'depends': ['sale_management','nati_reports_base_style'],
    'qweb': [],
    'data': ['views/main_inherit.xml',
             'views/report_SO_modern.xml',
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'live_test_url': 'https://youtu.be/Ayy81m38QP8',

}