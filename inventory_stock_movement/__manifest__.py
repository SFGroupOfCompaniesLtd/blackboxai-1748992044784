{
    "name": "Inventory Stock Movement",
    "version": "18.0.1.0.0",
    "summary": "Analyze and track internal inventory stock movements with detailed reports",
    "description": """
        Enable users to analyze and track internal inventory stock movements,
        showing opening balance, incoming and outgoing quantities, and closing balances
        for any date range, filtered by location and product.
    """,
    "category": "Inventory/Reporting",
    "author": "Relution",
    "website": "https://www.relution.com",
    "license": "LGPL-3",
    "depends": ["stock", "base", "product", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_movement_report_views.xml",
        "reports/stock_movement_pdf_template.xml",
        "wizard/stock_movement_filter_wizard.xml"
    ],
    "installable": True,
    "application": False,
    "auto_install": False
}
