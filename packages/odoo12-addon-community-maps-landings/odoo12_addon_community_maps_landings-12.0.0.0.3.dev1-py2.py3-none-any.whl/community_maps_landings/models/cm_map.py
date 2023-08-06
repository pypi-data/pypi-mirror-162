from odoo import models, api, fields
from odoo.tools.translate import _

class CmMap(models.Model):
  _name = 'cm.map'

  _inherit = ["cm.map"]

  allowed_landing_presenter_model_mids = fields.Many2many('cm.landing.presenter.model', 
    'cm_maps_landing_presenter_models', 'map_id', 'landing_presenter_model_id',string=_("Allowed landing presenters"))

  landing_base_url = fields.Char(string=_("Landing: Base url"),translate=True)

  def get_config_datamodel_dict(self):
    config_dict = super(CmMap, self).get_config_datamodel_dict()
    config_dict['landingBaseUrl'] = self.landing_base_url
    return config_dict