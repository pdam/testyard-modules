'''
Created on Oct 24, 2015

@author: pratikdam
'''





import sys, os, time, re
import unittest
# For PDF to text conversion:
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfparser import  PDFParser
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams

# To identify file type:
import magic # Needs libmagic1 installed.

# For parsing CV using a grammar definition:
import pyparsing

# For RTF to text conversion:
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter

# For doc, docx and odt to text conversions:
import subprocess
import zipfile


class ResumeParser(dict):
    _VALID_ATTRIB_NAMES = [ 'candidate_name', 'postal_address', 'email_address', 'landline_number', 'mobile_number_01', 'mobile_number_02', 'sex', 'date_of_birth', 'age', 'highest_qualification', 'qualification_02', 'qualification_03', 'qualification_04', 'more_qualifications', 'skills', 'industries', 'work_experiences', 'specializations', 'hobbies_and_interests', 'citations', 'honours', 'other_attributes' ]
    def __init__(self, attribs={}):
        self = dict()
        for attribName in ResumeParser._VALID_ATTRIB_NAMES:
            if attribs.has_key(attribName):
                self[attribName] = attribs[attribName]
            else:
                self[attribName] = ""

    """
    Handle all illegal and undefined attribute accesses gracefully.
    """
    def __getattr__(self, attrname):
        if attrname not in ResumeParser._VALID_ATTRIB_NAMES:
            print "'%s' is not defined as yet. You may extend the class you are using and add the attribute if you want to use it."%attrname
        else:
            return(self[attrname])
        return(None)


    """
    Handle all illegal and undefined attribute write accesses gracefully
    """
    def __setattr__(self, attrname, attrval):
        lastValue = None
        if attrname not in ResumeParser._VALID_ATTRIB_NAMES:
            print "Adding attribute '%s' with '%s' as value."%(attrname, attrval)
            if not self.has_key(attrname):
                lastValue = self[attrname]
                self[attrname] = attrval
            else:
                self[attrname] = attrval
                return(lastValue)
        else:
            lastValue = self[attrname]
            self[attrname] = attrval
            return(lastValue)
        return(None)
    



    class FormatError(object):
        '''
        classdocs
        '''
        def __init__(self, params):          '''
            Constructor
            '''
        


class CVParser(object):
    # Some commonly used regex patterns:
    newlinePattern = re.compile(r"\n")
    _common_words_list = ['address', 'mobile', 'qualification', 'name', 'brief', 'about', 'education', 'academic', 'course', 'graduate', 'masters', 'manager', 'appl.' 'application', 'post', ' of ', ' the ', ' and ', ' or ', ' for ', 'position', 'open', 'university', 'univ.', 'college', 'class', 'school', 'career', 'work', 'with', 'they', 'these', 'them', 'objective', 'aim', 'learn', ' can ', 'could', ' be ', 'organize', 'science', 'engineer', 'arts', ' art ', 'object', 'when', 'then', 'good', 'bad', 'file'] # These are the words that we will try to ignore when we are looking for proper nouns (like candidate's name, address, job location, etc)
    def __init__(self, cvfile, password=None):
        self.errorMsg = None
        self.cvFile = cvfile # Input CV file - can be in any of the following formats: pdf, doc, docx, rtf, txt, odt.
        if not os.path.exists(self.cvFile) or not os.path.isfile(self.cvFile):
            self.errorMsg = "The input file '%s' doesn't exist\n"%self.cvFile
            return None
        self.cvFormat = None # Can be any of the following: pdf, doc, docx, rtf, txt, odt.
        self.cvObject = ResumeParser() # This is the object that will be populated by the parser.
        self.cvFilePasswd = password # password for the input CV file (if one exists).
        self.scratchDir = os.getcwd() + os.path.sep + "temp_files" # Directory where the intermediate output files will be created (like, while parsing a pdf file, we need to convert it to a text file first, and then parse the text file. This is the location where the text file will be created.
        if not os.path.exists(self.scratchDir):
            os.makedirs(self.scratchDir)
        self.cvTextFile = None
        randomStr = int(time.time())
        self.userTempDir = self.scratchDir + os.path.sep + "tmp_" + randomStr.__str__()


        """
        Identify the format of the input file.
        """
        def _checkFormat(self):
            mime = magic.Magic(mime=True)
            filetype = mime.from_file(self.cvFile)
            fileparts = self.cvFile.split(".")
            ext = fileparts.pop()
            primaryEnc, secondaryEnc = filetype.split("/")
            if secondaryEnc.lower() == 'msword' or secondaryEnc.lower() == 'pdf' or secondaryEnc.lower() == 'rtf':
                self.cvFormat = ext.lower()
                return(True)
            elif primaryEnc.lower() == 'text' and secondaryEnc.lower() == 'plain':
                self.cvFormat = 'txt'
                return(True)
            elif primaryEnc.lower() == 'application' and secondaryEnc.lower() == 'zip' and ext.lower() == 'docx':
                self.cvFormat = 'docx'
                return(True)
            elif primaryEnc.lower() == 'application' and secondaryEnc.lower() == 'vnd.oasis.opendocument.text' and ext.lower() == 'odt':
                self.cvFormat = 'odt'
                return(True)
            else:
                self.errorMsg = "Unsupported file format - %s"%filetype
            return(False)
        

    """
    This method will identify the type of the input file and dispatch the file to the appropriate convertor method.
    """
    def preprocess(self):
        self._checkFormat()
        if self.errorMsg is not None:
            print self.errorMsg
            sys.exit(0)
        if self.cvFormat == 'pdf':
            self._convert_pdf_to_text()
        elif self.cvFormat == 'doc':
            self._convert_doc_to_text()
        elif self.cvFormat == 'docx':
            self._convert_docx_to_text()
        elif self.cvFormat == 'rtf':
            self._convert_rtf_to_text()
        elif self.cvFormat == 'odt':
            self._convert_odt_to_text()
        elif self.cvFormat == 'txt':
            pass
        else:
            raise self.FormatError()
        return(self.cvTextFile)


    def _convert_pdf_to_text(self, password=None):
        input_pdf = self.cvFile
        if password is not None:
            self.cvFilePasswd = password
        pagenos = range(0, 30)
        maxpages = pagenos.__len__()
        layoutmode = 'normal'
        codec = 'utf-8'
        scale = 1
        outtype = 'txt'
        laparams = LAParams()
        laparams.all_texts = True
        laparams.showpageno = True
        outputPath = self.scratchDir
        inputPath = os.getcwd()
        if os.path.exists(input_pdf):
            inputPath = os.path.dirname(input_pdf)
        input_filename = os.path.basename(input_pdf)
        input_parts = input_filename.split(".")
        input_parts.pop()
        randomStr = int(time.time())
        output_filename = outputPath + os.path.sep + ".".join(input_parts) + randomStr.__str__() + r".txt"
        self.cvTextFile = output_filename
        outfp = file(output_filename, 'w')
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams)
        fp = file(input_pdf, 'rb')
        self.process_pdf(rsrcmgr, device, fp, pagenos, maxpages=maxpages, password=self.cvFilePasswd, check_extractable=True)
        fp.close()
        device.close()
        outfp.close()
        return (0)

    def process_pdf(self, rsrcmgr, device, fp, pagenos, maxpages, password, check_extractable):
        pass

    def _convert_doc_to_text(self, password=None):
        input_doc = self.cvFile
        outputPath = self.scratchDir
        inputPath = os.getcwd()
        if os.path.exists(input_doc):
            inputPath = os.path.dirname(input_doc)
        input_filename = os.path.basename(input_doc)
        input_parts = input_filename.split(".")
        input_parts.pop()
        randomStr = int(time.time())
        output_filename = outputPath + os.path.sep + ".".join(input_parts) + randomStr.__str__() + r".txt"
        self.cvTextFile = output_filename
        cmd = "catdoc %s >%s"%(self.cvFile, self.cvTextFile) # Dangerous!!! Why not use 'subprocess'?
        os.system(cmd)
        return(0)


    def _convert_docx_to_text(self, password=None):
        input_docx = self.cvFile
        outputPath = self.scratchDir
        inputPath = os.getcwd()
        if os.path.exists(input_docx):
            inputPath = os.path.dirname(input_docx)
        input_filename = os.path.basename(input_docx)
        input_parts = input_filename.split(".")
        input_parts.pop()
        randomStr = int(time.time())
        output_filename = outputPath + os.path.sep + ".".join(input_parts) + randomStr.__str__() + r".txt"
        self.cvTextFile = output_filename
        docx = zipfile.ZipFile(input_docx)
        content = docx.read('word/document.xml')
        content = re.sub("</w:t>", "\n", content)
        cleaned = re.sub('<.*?>','',content)
        fw = file(self.cvTextFile, "w")
        fw.write(cleaned)
        fw.close()
        return(0)


    def _convert_odt_to_text(self, password=None):
        input_odt = self.cvFile
        outputPath = self.scratchDir
        inputPath = os.getcwd()
        if os.path.exists(input_odt):
            inputPath = os.path.dirname(input_odt)
        input_filename = os.path.basename(input_odt)
        input_parts = input_filename.split(".")
        input_parts.pop()
        randomStr = int(time.time())
        output_filename = outputPath + os.path.sep + ".".join(input_parts) + randomStr.__str__() + r".txt"
        self.cvTextFile = output_filename
        odt = zipfile.ZipFile(input_odt)
        extractedContentFile = odt.extract('content.xml', self.userTempDir)
        fxml = open(extractedContentFile)
        content = fxml.read()
        fxml.close()
        os.unlink(extractedContentFile) # Remove this temporary file...
        os.rmdir(self.userTempDir) #...  and the temporary user directory
        # Now split content on '<office:body>'. This should result in 2 parts. We need the second part only.
        contentParts = content.split('<office:body>')
        if contentParts.__len__() > 1:
            content = contentParts[1]
        content = re.sub("</text:p>", "\n", content)
        cleaned = re.sub('<.*?>','',content)
        fw = file(self.cvTextFile, "w")
        fw.write(cleaned)
        fw.close()
        return(0)


    def _convert_rtf_to_text(self, password=None):
        input_rtf = self.cvFile
        rtf = Rtf15Reader.read(open(input_rtf))
        outputPath = self.scratchDir
        inputPath = os.getcwd()
        if os.path.exists(input_rtf):
            inputPath = os.path.dirname(input_rtf)
        input_filename = os.path.basename(input_rtf)
        input_parts = input_filename.split(".")
        input_parts.pop()
        randomStr = int(time.time())
        output_filename = outputPath + os.path.sep + ".".join(input_parts) + randomStr.__str__() + r".txt"
        self.cvTextFile = output_filename
        fw = open(self.cvTextFile, "w")
        fw.write(PlaintextWriter.write(rtf).getvalue())
        fw.close()
        return (0)


    def parseCvDocument(self, cvTextFile=None):
        if not cvTextFile: # Check if the cvTextFile argument has been passed or not.
            cvTextFile = self.cvTextFile
        cvData = {} # Initialize the data structure for holding information collected from the CV.
        cvContents = None
        if not os.path.exists(cvTextFile): # Check if the file exists or not.
            print "The intermediate text file ('%s') could not be found."
            self.errorMsg = "The intermediate text file ('%s') could not be found."
            return(cvData) # returns {} here.
        fc = open(cvTextFile)
        cvContents = fc.read()
        fc.close()
        # Parser implementation starts here. Start with stripping empty lines at the start of the file.
        startEmptyLinesPattern = re.compile(r"^\n+", re.MULTILINE | re.DOTALL)
        cvContents = re.sub(startEmptyLinesPattern, "", cvContents)
        cvHeaderPattern = re.compile(r"^(\s*Curriculum\s+Vitae\s+|\s*Resume\s+|\s+CV\s+|\s+Biodata\s+)?\s*[\-:]{0,}\s*(\w+[\.\,]{0,}[\.\,\-\sa-zA-Z]*$)", re.IGNORECASE | re.MULTILINE | re.DOTALL)
        cvHeaderSearch = cvHeaderPattern.search(cvContents)
        candidateName = ""
        if cvHeaderSearch:
            candidateName = cvHeaderSearch.groups()[1]
        if self.__class__.newlinePattern.search(candidateName):
            nameParts = candidateName.split("\n")
            candidateName = nameParts[0]
        print "Candidate Name: %s\n"%candidateName



if __name__ == '__main__':
    cvfile = sys.argv[1]
    cvparser = CVParser(cvfile)
    if cvparser.errorMsg:
        print cvparser.errorMsg
        sys.exit(0)
    try:
        cvparser.preprocess()
    except:
        print "Unsupported file format."
        sys.exit(1)
    print cvparser.cvTextFile
    cvparser.parseCvDocument()







if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()