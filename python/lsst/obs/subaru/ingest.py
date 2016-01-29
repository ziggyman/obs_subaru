import re
import datetime

from lsst.pipe.tasks.ingest import IngestTask, ParseTask, IngestArgumentParser, ParseConfig
import lsst.afw.image as afwImage

class SubaruIngestArgumentParser(IngestArgumentParser):
    def _parseDirectories(self, namespace):
        """Don't do any 'rerun' hacking: we want the raw data to end up in the root directory"""
        namespace.input = namespace.rawInput
        namespace.output = namespace.rawOutput
        namespace.calib = None
        del namespace.rawInput
        del namespace.rawCalib
        del namespace.rawOutput
        del namespace.rawRerun

class SubaruIngestTask(IngestTask):
    ArgumentParser = SubaruIngestArgumentParser


def datetime2mjd(date_time):

    YY = date_time.year
    MO = date_time.month
    DD = date_time.day
    HH = date_time.hour
    MI = date_time.minute
    SS = date_time.second

    if MO == 1 or MO == 2:
        mm = MO + 12
        yy = YY - 1
    else:
        mm = MO
        yy = YY

    dd = DD + (HH/24.0 + MI/24.0/60.0 + SS/24.0/3600.0)

    A = int(365.25*yy);
    B = int(yy/400.0);
    C = int(yy/100.0);
    D = int(30.59*(mm-2));

    mjd = A + B -C + D  + dd - 678912;

    return mjd

class HscParseTask(ParseTask):
    DAY0 = 55927  # Zero point for  2012-01-01  51544 -> 2000-01-01

    def translate_field(self, md):
        #field = md.get("OBJECT").strip()
        #if field == "#":
        #    field = "UNKNOWN"
        #field = re.sub(r'\W', '_', field).upper() # replacing inappropriate characters for file path and upper()
        field = "UNKONWN" # for now
        return field

    def translate_visit(self, md):
        expId = md.get("EXP-ID").strip()
        m = re.search("^HSC([A-Z])(\d{6})00$", expId)
        if not m:
            raise RuntimeError("Unable to interpret EXP-ID: %s" % expId)
        letter, visit = m.groups()
        visit = int(visit)
        if int(visit) == 0:
            # Don't believe it
            frameId = md.get("FRAMEID").strip()
            m = re.search("^HSC([A-Z])(\d{6})\d{2}$", frameId)
            if not m:
                raise RuntimeError("Unable to interpret FRAMEID: %s" % frameId)
            letter, visit = m.groups()
            visit = int(visit)
            if visit % 2: # Odd?
                visit -= 1
        return visit + 1000000*(ord(letter) - ord("A"))

    def getTjd(self, md):
        """Return truncated (modified) Julian Date"""
        return int(md.get('MJD')) - self.DAY0

    def translate_pointing(self, md):
        """This value was originally called 'pointing', and intended to be used
        to identify a logical group of exposures.  It has evolved to simply be
        a form of truncated Modified Julian Date, and is called 'visitID' in
        some versions of the code.  However, we retain the name 'pointing' for
        backward compatibility.
        """
        try:
            return self.getTjd(md)
        except:
            pass

        try:
            dateobs = md.get("DATE-OBS")
            m = re.search(r'(\d{4})-(\d{2})-(\d{2})', dateobs)
            year, month, day = m.groups()
            obsday = datetime.datetime(int(year), int(month), int(day), 0, 0, 0)
            mjd = datetime2mjd(obsday)
            return int(mjd) - day0
        except:
            pass

        self.log.warn("Unable to determine suitable 'pointing' value; using 0")
        return 0

    # CCD index mapping for commissioning run 2
    CCD_MAP_COMMISSIONING_2 = {112: 106,
                               107: 105,
                               113: 107,
                               115: 109,
                               108: 110,
                               114: 108,
                               }
    def translate_ccd(self, md):
        """Focus CCDs were numbered incorrectly in the readout software during
        commissioning run 2.  We need to map to the correct ones.
        """
        ccd = int(md.get("DET-ID"))
        try:
            tjd = self.getTjd(md)
        except:
            return ccd

        if tjd > 390 and tjd < 405:
            ccd = self.CCD_MAP_COMMISSIONING_2.get(ccd, ccd)

        return ccd

    def translate_filter(self, md):
        """Want upper-case filter names"""
        try:
            return md.get('FILTER01').strip().upper()
        except:
            return "Unrecognized"


class PfsParseConfig(ParseConfig):
    def setDefaults(self):
        ParseConfig.setDefaults(self)
#        self.translators["date"] = "translate_date"
        self.translators["field"] = "translate_field"
#        self.defaults["filter"] = "NONE"

class PfsParseTask(ParseTask):
    ConfigClass = PfsParseConfig

    def getInfo(self, filename):
        """Get information about the image from the filename and its contents

        @param filename    Name of file to inspect
        @return File properties; list of file properties for each extension
        """
        #matches = re.search("^PFSA(\d{6})(\d)(\d).fits", filename)
        matches = re.search("PF([JLXIASPF])([ABCDS])(\d{6})(\d)(\d).fits", filename)
        if not matches:
            raise RuntimeError("Unable to interpret filename: %s" % filename)
        site, category, visit, filterInt, spectrograph = matches.groups()
        self.log.info('site = %s: %s' % type(site), site)
        self.log.info('category = %s: %s' % type(category),category)
        self.log.info('visit = %s: %s' % type(visit),visit)
        self.log.info('filterInt = %s: %d' % type(filterInt),filterInt)
        self.log.info('spectrograph = %s: %s' % type(spectrograph),spectrograph)
        if int(spectrograph) > 4:
            spectrograph = '4'
        ccd = int(spectrograph)-1
        filter = ''
        if filterInt == '0':
            filter = 'PFS-B'
        elif filterInt == '1':
            filter = 'PFS-R'
            ccd += 4
        elif filterInt == '2':
            filter = 'PFS-N'
            ccd += 8
        else:
            filter = 'PFS-M'
            ccd += 4
        self.log.info('PfsParseTask.getInfo: filename = <%s>: site = <%s>: %s, category = <%s>: %s, visit = <%d>: %s, filter = <%s>: %s, ccd = <%d>: %s, spectrograph = <%s>: ',% fileName, site, type(site),category, type(category),visit, type(visit), filter, type(filter), ccd, type(ccd), spectrograph, type(spectrograph))

        header = afwImage.readMetadata(filename)
        info = dict(site=site, category=category, visit=int(visit), filter=filter, spectrograph=int(spectrograph), ccd=int(ccd))
        info = self.getInfoFromMetadata(header, info=info)
        return info, [info]

    def translate_field(self, md):
        """Get 'field' from IMAGETYP

        This is temporary, until an OBJECT (or similar) header can be provided,
        but it's better than setting everything to the same thing.
        """
        field = md.get("IMAGETYP").strip()
        if field in ("#", ""):
            field = "UNKNOWN"
        self.log.info('PfsParseTask.translate_field: field = %s' % field)
        return re.sub(r'\W', '_', field).upper()
