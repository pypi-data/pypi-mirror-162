from odoo import models, api, fields
from odoo.tools.translate import _

class CmPlaceLandingPresenterMetadata(models.Model):
  _name = 'cm.place.landing.presenter.metadata'
  _inherit = 'cm.metadata'

  place_id = fields.Many2one('crm.team',string=_("Place"),ondelete='cascade')