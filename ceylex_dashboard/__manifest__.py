{
    'name': 'Ceylex dashboard',
    'version': '1.0',
    'sequence': 1,
    'author': "Centrics Business Solutions (Pvt) Ltd",
    'website': 'http://www.centrics.cloud/',
    'summary': 'Ceylex reports and dashboard',
    'description': """ reports and dashboard""",
    'depends': [
        'base',
        'purchase',
        'ceylex_changes',
        'ceylex_energy',
        'account',
    ],
    'data': [
        'views/dashboard.xml',
    ],
    'assets': {
        'web.assets_backend': [

            'ceylex_dashboard/static/src/js/dashboard.js',
            'ceylex_dashboard/static/src/css/dashboard.css',

        ],
        'web.assets_qweb': [
            'ceylex_dashboard/static/src/xml/dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}