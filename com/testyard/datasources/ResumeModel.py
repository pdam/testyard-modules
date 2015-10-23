'''
Created on Oct 24, 2015

@author: pratikdam
'''
import ResumeExtractor
class ResumeModel(object):
    
    
    class Basics(dict):
        def __init__(self):
            self.resumeText=self.getResumeText()
            self.extractor =  ResumeExtractor()
            self.name = self.extractor.extract_name(self.resumeText)
            self.label= self.extractor.extract_label(self.resumeText)
            self.picture = self.extractor.extract_picture(self.resumeText)
            self.email = self.extractor.extract_email(self.resumeText)
            self.phone = self.extractor.extract_phoneno(self.resumeText)
            self.website = self.extractor.extract_website(self.resumeText)
            self.summary = self.extractor.extract_summary(self.resumeText)
            self.hashid= hash(self.email , self.first_name, self.phone )
            
    
    
    def getResumeText(self):
        pass
    
    
    class Profiles(list):
        pass
    
    class Emplayments(list):
        pass
    
    
    class Work(Emplayments):
        pass
    
    
    class Education(list):
        pass
    
    
    class Volunteer(list):
        pass
    
    
    class Awards(list):
        pass
    
    
    class Skills(list):
        pass
    
    
    class Publications(list):
        pass
    
    
    class Languages(list):
        pass
    
    
    
    
    class References(list):
        pass
    
    
    class Interests(list):
        pass
    
    
    
    
    '''
    {

  "basics": {
    "name": "John Doe",
    "label": "Programmer",
    "picture": "",
    "email": "john@gmail.com",
    "phone": "(912) 555-4321",
    "website": "http://johndoe.com",
    "summary": "A summary of John Doe...",
    "location": {
      "address": "2712 Broadway St",
      "postalCode": "CA 94115",
      "city": "San Francisco",
      "countryCode": "US",
      "region": "California"
    },
    "profiles": [{
      "network": "Twitter",
      "username": "john",
      "url": "http://twitter.com/john"
    }]
  },
  "work": [{
    "company": "Company",
    "position": "President",
    "website": "http://company.com",
    "startDate": "2013-01-01",
    "endDate": "2014-01-01",
    "summary": "Description...",
    "highlights": [
      "Started the company"
    ]
  }],
  "volunteer": [{
    "organization": "Organization",
    "position": "Volunteer",
    "website": "http://organization.com/",
    "startDate": "2012-01-01",
    "endDate": "2013-01-01",
    "summary": "Description...",
    "highlights": [
      "Awarded 'Volunteer of the Month'"
    ]
  }],
  "education": [{
    "institution": "University",
    "area": "Software Development",
    "studyType": "Bachelor",
    "startDate": "2011-01-01",
    "endDate": "2013-01-01",
    "gpa": "4.0",
    "courses": [
      "DB1101 - Basic SQL"
    ]
  }],
  "awards": [{
    "title": "Award",
    "date": "2014-11-01",
    "awarder": "Company",
    "summary": "There is no spoon."
  }],
  "publications": [{
    "name": "Publication",
    "publisher": "Company",
    "releaseDate": "2014-10-01",
    "website": "http://publication.com",
    "summary": "Description..."
  }],
  "skills": [{
    "name": "Web Development",
    "level": "Master",
    "keywords": [
      "HTML",
      "CSS",
      "Javascript"
    ]
  }],
  "languages": [{
    "language": "English",
    "fluency": "Native speaker"
  }],
  "interests": [{
    "name": "Wildlife",
    "keywords": [
      "Ferrets",
      "Unicorns"
    ]
  }],
  "references": [{
    "name": "Jane Doe",
    "reference": "Reference..."
  }]

}



    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        