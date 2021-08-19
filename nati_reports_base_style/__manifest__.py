 # -*- coding: utf-8 -*-
{
    'name': "Nati Reports Base Style",

    'summary': """
        Redesign of all report, keeping the official and modern look """,

    'description': """
Many modern designs and shapes, with additional features, 
for example: line numbers, numbers in words, compatibility with different printing options,
english and arabic lable,for both LTR and RTL
    """,
    'author': "Mali, MuhlhelITS",
    'website': "http://natigroup.biz",
    'license': 'AGPL-3',
    'category': 'Extra Tools',
    'version': '14.0.0.0',
    'depends': ['base','nati_arabic_font'],
    'qweb': [],
    'data': ['views/main_inherit.xml',
             'views/styleslink.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
}