 # -*- coding: utf-8 -*-
{
    'name': "Nati Reports Purchase",

    'summary': """
        Redesign of the Purchase order, keeping the official and modern look """,

    'description': """
Many modern designs and shapes, with additional features, 
for example: line numbers, numbers in words, compatibility with different printing options,
english and arabic lable,for both LTR and RTL
    """,
    'author': "Mali, MuhlhelITS",
    'website': "http://natigroup.biz",
    'license': 'AGPL-3',
    'category': 'Purchase',
    'version': '14.0.0.0',
    'depends': ['purchase','nati_reports_base_style'],
    'qweb': [],
    'data': ['views/main_inherit.xml',
             'views/report_purchaseorder_modern.xml',
             'views/report_purchasequotation_modern.xml',

             ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
}