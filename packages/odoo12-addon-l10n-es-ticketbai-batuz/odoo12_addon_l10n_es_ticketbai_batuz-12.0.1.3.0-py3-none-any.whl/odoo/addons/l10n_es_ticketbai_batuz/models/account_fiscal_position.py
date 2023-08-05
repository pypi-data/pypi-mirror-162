# Copyright 2021 Digital5, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    tbai_vat_regime_purchase_key = fields.Many2one(
        comodel_name="tbai.vat.regime.key",
        string="VAT Regime Key for purchases",
        domain=[("type", "=", "purchase")],
        copy=False,
    )
    tbai_vat_regime_purchase_key2 = fields.Many2one(
        comodel_name="tbai.vat.regime.key",
        string="VAT Regime 2nd Key for purchases",
        domain=[("type", "=", "purchase")],
        copy=False,
    )
    tbai_vat_regime_purchase_key3 = fields.Many2one(
        comodel_name="tbai.vat.regime.key",
        string="VAT Regime 3rd Key for purchases",
        domain=[("type", "=", "purchase")],
        copy=False,
    )
    tbai_vat_regime_key = fields.Many2one(domain=[("type", "=", "sale")])
    tbai_vat_regime_key2 = fields.Many2one(domain=[("type", "=", "sale")])
    tbai_vat_regime_key3 = fields.Many2one(domain=[("type", "=", "sale")])
