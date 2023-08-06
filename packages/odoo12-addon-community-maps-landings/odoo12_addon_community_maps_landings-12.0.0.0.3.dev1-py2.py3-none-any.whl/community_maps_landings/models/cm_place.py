from odoo import models, api, fields
from odoo.tools.translate import _

class CmPlace(models.Model):
  _name = 'crm.team'

  _inherit = ["crm.team"]

  landing_presenter_model_id = fields.Many2one(
    'cm.landing.presenter.model',
    string=_("Landing Presenter")
  )
  place_landing_presenter_metadata_ids = fields.One2many(
    'cm.place.landing.presenter.metadata',
    'place_id',
    string=_("Landing presenter metadata"))

  @api.onchange('map_id')
  def _get_config_relations_attrs(self):
    self.ensure_one()
    return_dict = super(CmPlace, self)._get_config_relations_attrs()
    allowed_landing_presenter_model_ids = self.map_id.allowed_landing_presenter_model_mids
    return_dict['domain']['landing_presenter_model_id'] = [
      ('id', 'in',allowed_landing_presenter_model_ids.mapped('id'))
    ]
    return return_dict

  def get_datamodel_dict(self,single_view=False):
    place_dict = super(CmPlace, self).get_datamodel_dict(single_view)
    place_dict['landingCtaLabel'] = False
    if self.landing_presenter_model_id:
      if self.landing_presenter_model_id.cta_label:
        place_dict['landingCtaLabel'] = self.landing_presenter_model_id.cta_label
    place_dict['landingSchemaData'] = self._build_presenter_schemadata_json(
      'landing_presenter_model_id','place_landing_presenter_metadata_ids')
    place_dict['landingJsonSchema'] = self._build_presenter_schema_json('landing_presenter_model_id')
    return place_dict

  # PRESENTER
  def _get_create_place_meta(self,key,type,format,sort_order,place_id,dataschema,uischema):
    return self._get_create_place_meta_dmodel(
      'cm.place.landing.presenter.metadata',
      key,type,format,sort_order,place_id,dataschema,uischema)

  # presenter metadata
  @api.onchange('landing_presenter_model_id')
  def _build_landing_presenter_metadata_ids(self):
    self.ensure_one()
    self._build_presenter_metadata_ids(
      'landing_presenter_model_id','place_landing_presenter_metadata_ids')