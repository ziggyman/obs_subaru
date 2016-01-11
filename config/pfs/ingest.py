from lsst.obs.subaru.ingest import PfsParseTask
config.parse.retarget(PfsParseTask)
config.register.columns = {'site': 'text', #J: JHU, L: LAM, X: Subaru offline, I: IPMU, A: ASIAA, S: Summit, P: Princeton, F: simulation (fake)
                           'category': 'text', #A: science, B: NTR, C: Meterology, D: HG
                           'field': 'text', # IMAGETYP
                           'visit': 'int',
                           'ccd': 'int', #[0-11]
                           'filter': 'text', #PFS-B: blue, PFS-R: red, PFS-N: nir, PFS-M: medium resolution red
                           'det': 'int', #1-4
                           'dateObs': 'text',
                           'expTime': 'double',
                           'dataType': 'text', #IMAGETYP, same as field
                           #'src': 'text' #this is new
                          }
config.register.unique = ['site', 'category', 'visit', 'filter', 'det']
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

