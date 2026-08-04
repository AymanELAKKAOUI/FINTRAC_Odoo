from odoo import http


class MyIntegrationController(http.Controller):
    @http.route("/my_integration/health", auth="public", type="json", csrf=False)
    def health(self):
        return {"status": "ok", "module": "my_integration"}
