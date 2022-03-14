{
    'name': 'Ceylex Changes',
    'version': '1.0',
    'sequence': 1,
    'author': "Centrics Business Solutions (Pvt) Ltd",
    'website': 'http://www.centrics.cloud/',
    'summary': 'Ceylex company changes',
    'description': """changes in company profile""",
    'depends': [
        'base',
        'account',
        'purchase',
        'account_budget',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/purchase_order_view.xml',
        'views/res_partner_view.xml',
        'views/meter_reading_views.xml',
        'views/account_move_view.xml',
        'views/account_budget_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}