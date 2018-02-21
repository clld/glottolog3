#Overview of the script:
#1 - Retrieve all ISO codes from Wikitongues' database and store them in a dictionary
#2 - Retrieve all ISO codes in the identifier table from Glottolog's database
#3 - Compare each ISO code from Glottolog to the one from Wikitongues
#4 - Return the difference between them in 2 arrays: one with all Iso codes only exist in Glottolog, and one with all Iso codes only exist in Wikitongues

#from glottolog3.models import Languoid
from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base  
import csv

#change this db_string to the actual postgres db containing the data
db_string = "postgres://postgres:@127.0.0.1:5432/glottolog-3.2";
db = create_engine(db_string);
base = declarative_base();

class Identifier(base):
	__tablename__ = 'identifier';
	pk = Column(Numeric, primary_key=True);
	name = Column(String);
	type = Column(String);

class LanguageIdentifier(base):
	__tablename__ = 'languageidentifier';
	pk = Column(Numeric, primary_key=True);
	language_pk = Column(Numeric, ForeignKey("language.pk"));
	identifier_pk = Column(Numeric, ForeignKey("identifier.pk"));

class Language(base):
	__tablename__ = 'language';
	pk = Column(Numeric, primary_key=True);
	id = Column(String);
	name = Column(String);

class LanguageObject:
	name = '';
	isoCode = '';
	def __init__(self, languageName, languageIsoCode):	
		self.name = languageName;
		self.isoCode = languageIsoCode;

#Using Glottolog's Model
#def getIdentifier():
#	counter = 0;
#	langs = session.query(Languoid);
#	tempArr = [];
#	for lang in langs:
#		counter += 1;
#		print(counter);
#		if counter == -1:
#			break;
#		tempIdent = lang.get_identifier_objs('iso639-3');
#		if (len(tempIdent)!=0):
#			identifierName = tempIdent[0].name;
#			tempArr.append(LanguageObject(lang.name, identifierName));
#	return tempArr;
#print(getIdentifier());

def getIdentifier():
	print("Generating LanguageObject Array with Glottolog's Database");
	identifiers = session.query(Identifier, LanguageIdentifier, Language).join(LanguageIdentifier).join(Language).filter(Identifier.type == 'iso639-3').all(); 
	tempDict = {};
	for identifier in identifiers:
		tempDict[identifier[0].name] = LanguageObject(identifier[2].name, identifier[0].name);
	return tempDict;

def populateISODictionary():
	print("Generating Dictionary with Wikitongues' Database");
	tempDict = {};
	with open('lang.csv') as langread:
		next(langread); #To get rid of column header
		csv_reader = csv.reader(langread, delimiter=',');
		#element[0] is the Iso639-3 code of each language in Wikitongues' database
		#element[1] is the name of the language of element[0]
		for element in csv_reader:
			tempDict[element[0]] = LanguageObject(element[1], element[0]);
	return tempDict;

def getDifference():
	glottolog_only = [];
	wikitongues_only = [];
	lang_dict = populateISODictionary(); #Iso639-3 codes from Wikitongues' database
	idenDict = getIdentifier(); #Iso639-3 codes from Glottolog's database
	print("Checking Which Language is in Glottolog Only.");
	glottolog_only = sorted([langObj for langObj in idenDict.values() if (True if langObj.isoCode not in lang_dict else not(lang_dict.pop(langObj.isoCode)))], key=lambda langObject: langObject.isoCode);
	print("Checking Which Language is in Wikitongues Only.");
	wikitongues_only = sorted(lang_dict.values(), key=lambda langObject: langObject.isoCode);
	return glottolog_only, wikitongues_only;

def developmentOutput(resultArray):
	print("\nGlottolog Only (" + str(len(resultArray[0])) + " entries):");
	for i in resultArray[0]:
		print(i.isoCode + "    " + i.name);
	print("\nWikitongues Only (" + str(len(resultArray[1])) + " entries):");
	for i in resultArray[1]:
		print(i.isoCode + "    " + i.name);

Session = sessionmaker(db);  
session = Session();
base.metadata.create_all(db);
developmentOutput(getDifference());

