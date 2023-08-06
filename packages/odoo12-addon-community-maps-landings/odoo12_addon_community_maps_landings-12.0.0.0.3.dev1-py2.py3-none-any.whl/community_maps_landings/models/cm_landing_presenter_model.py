from odoo import models, api, fields
from odoo.tools.translate import _

class CmLandingPresenterModel(models.Model):
  _name = 'cm.landing.presenter.model'

  _inherit = ["cm.presenter.model"]

  allowed_in_map_mids = fields.Many2many('cm.map', 'cm_maps_landing_presenter_models', 'landing_presenter_model_id', 'map_id',
    string=_("Allowed in maps"))

  cta_label = fields.Char(string=_("Landing link button label"),translate=True)

  json_uischema = fields.Text(string=_("UiSchema"),default="{}",translate=True)