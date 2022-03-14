{
    'name': 'Ceylex Reports and dashboard',
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
        'account',
        'hr',
        'utm',
        'account_accountant',
        'account_budget',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/ir_corn_job.xml',

        'reports/paper_format.xml',
        'reports/purchase_report.xml',
        'reports/invoice_management.xml',
        'reports/supplier_evaluation.xml',
        'reports/budget_report.xml',

        'views/purchase_order_view.xml',
        'views/res_company_view.xml',
        'views/supplier_rating_views.xml',
        'views/res_partner_view.xml',
        'views/account_budget.xml',
    ],
    'assets': {
        'web.assets_common': [
            ('prepend', 'ceylex_reports/static/src/css/report_style.css'),
        ],
        'web.assets_backend': [
            ('prepend', 'ceylex_reports/static/src/css/report_style.css'),
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}