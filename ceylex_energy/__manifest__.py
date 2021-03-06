{
    'name': 'Ceylex Energy calculations',
    'version': '1.0',
    'sequence': 1,
    'author': "Centrics Business Solutions (Pvt) Ltd",
    'website': 'http://www.centrics.cloud/',
    'summary': 'Ceylex calculations',
    'description': """changes in calculations""",
    'depends': [
        'base',
        'uom',
    ],
    'data': [
        'data/uom_data.xml',
        'data/input_rules.xml',
        'data/input_results.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_company_view.xml',
        'views/menuitem.xml',
        'views/energy_input_views.xml',
        'views/power_source_views.xml',
        'views/energy_calculations_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}