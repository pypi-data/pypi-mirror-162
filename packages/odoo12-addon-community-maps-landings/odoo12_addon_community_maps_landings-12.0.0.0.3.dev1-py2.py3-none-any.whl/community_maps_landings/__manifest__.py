# -*- coding: utf-8 -*-
{
  'name': "community_maps_landings",

  'summary': """
    Redirect map places to website pages into your web.""",

  'author': "Coopdevs Treball SCCL",
  'website': "https://gitlab.com/coopdevs/community-maps-builder-backend",

  # Categories can be used to filter modules in modules listing
  # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
  # for the full list
  'category': 'community-maps',
  'version': '12.0.0.0.3',

  # any module necessary for this one to work correctly
  'depends': [
    'community_maps'
  ],

  # always loaded
  'data': [
    'security/ir.model.access.csv',
    'views/cm_map.xml',
    'views/cm_place.xml',
    'views/cm_landing_presenter_model.xml'
  ]
}
