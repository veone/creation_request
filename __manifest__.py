{
    'name': 'Product Validation',
    'version': '16.0.0.1',
    'summary': '',
    'description': 'Creation Request',
    'category': 'Request',
    'author': 'Lagoh Kouadio Jean Rodrigue, DIBI Bi Kavola Augustin',
    'website': 'veone.net',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'hr',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizard/product_refused_validation_views.xml',
        'views/product_request_views.xml',
        'views/res_config_setting.xml',
        'views/department_view.xml',
        'views/menu_views.xml',
    ],

    'installable': True,
    'auto_install': False
}
