from lsst.obs.subaru.ingest import PfsParseTask
config.parse.retarget(PfsParseTask)
config.register.columns = {'field': 'text',
                           'visit': 'int',
                           'ccd': 'int',
                           'arm': 'text',
                           'dateObs': 'text',
                           'expTime': 'double',
                           'dataType': 'text',
                           #'src': 'text' #this is new
                          }
config.register.unique = ['visit', 'arm', 'ccd',]
config.register.visit = ['visit', 'field', 'dateObs']

config.parse.translation = {'dataType': 'IMAGETYP',
                          'expTime': 'EXPTIME',
                          #'ccd': 'DET-ID',
                          #'pa': 'INST-PA',
                          #'autoguider': 'T_AG',
                          #'ccdTemp': 'T_CCDTV',
                          #'config': 'T_CFGFIL',
                          #'frameId': 'FRAMEID',
                          #'expId': 'EXP-ID',
                          'dateObs': 'DATE-OBS',
                          #'taiObs': 'DATE-OBS',
}
config.parse.defaults = {'ccdTemp': "0", # Added in commissioning run 3
                       }
config.parse.translators = {'field': 'translate_field',
                            'dateObs': 'translate_date',
                          #'visit': 'translate_visit',
                          #'pointing': 'translate_pointing',
                          #'filter': 'translate_filter',
}

