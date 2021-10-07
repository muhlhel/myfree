 # -*- coding: utf-8 -*-
{
    'name': "Nati arabic font",

    'summary': """
        change defult font to nice arabic font""",

    'description': """
        Change the defult arabic font of the all interfaces with a beautiful one preferred by the Arabic user
 ,
    """,
    'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'category': 'Localization',
    'version': '15.0.0.0',
    'depends': ['web'],
    'qweb': [],

    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'auto_install': True,
    'installable': True,
    'assets': {
        'web.assets_common': [
            'nati_arabic_font/static/src/scss/almaraifont.scss',
            'nati_arabic_font/static/src/scss/cairofont.scss',
            'nati_arabic_font/static/src/scss/droidfont.scss',
            'nati_arabic_font/static/src/css/web_style.css',
        ],
        'report_assets_common': [
            'nati_arabic_font/static/src/scss/almaraifont.scss',
            'nati_arabic_font/static/src/scss/cairofont.scss',
            'nati_arabic_font/static/src/scss/droidfont.scss',
        ],


    },
}