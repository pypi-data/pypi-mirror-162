from distutils.core import setup
setup(
  name = 'srb_api',
  packages = ['srb_api', "srb_api.application", "srb_api.devices", "srb_api.general", "srb_api.server"], # this must be the same as the name above
  version = '0.1',
  description = 'A tutorial lib',
  author = 'Khannasu',
  author_email = 'sukratk@gmail.com',
  url = 'https://github.com/sajorn-warrior/srb_api',
  download_url = 'https://github.com/sajorn-warrior/srb_api/tarball/0.1',
  keywords = ['api'], 
  classifiers = [],
)