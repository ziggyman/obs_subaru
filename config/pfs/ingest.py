from lsst.obs.subaru.ingest import PfsParseTask
root.parse.retarget(PfsParseTask)
config.register.columns = {'field': 'text',
                           'visit': 'int',
                           'ccd': 'int',
                           'arm': 'int',
                           'dateObs': 'text',
                          }
config.register.unique = ['visit', 'arm', 'ccd',]
config.register.visit = ['visit', 'field', 'dateObs']

