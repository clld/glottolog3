#Pre-development Notes:
#1 - Retrieve all ISO codes from Wikitounges' database and store them in a dictionary
#2 - Retrieve all ISO codes in the identifier table from Glottolog's database
#3 - Compare each ISO code from Glottolog to the one from Wikitounges
#4 - Return the difference between them in 2 arrays: one with all Iso codes only exist in Glottolog, and one with all Iso codes only exist in Wikitounges

#from glottolog3.models import Languoid
from sqlalchemy import create_engine  
from sqlalchemy import Column, String 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base  
import csv

#change this db_string to the actual postgres db containing the data
db_string = "postgres://postgres:@127.0.0.1:5432/glottolog-3.2";
db = create_engine(db_string);  
base = declarative_base();

class Identifier(base):
	__tablename__ = 'identifier';
	pk = Column(String, primary_key=True);
	name = Column(String);
	type = Column(String);

class languageidentifier(base):
	__tablename__ = 'languageidentifier';
	pk = Column(String, primary_key=True);
	language_pk = Column(String);
	identifier_pk = Column(String);

class language(base):
	__tablename__ = 'language';
	pk = Column(String, primary_key=True);
	id = Column(String);
	name = Column(String);

class WikitoungesIsoObject:
	name = '';
	checked= '';
	def __init__(self, languageName, isChecked):
		self.name = languageName;
		self.checked = isChecked;

class languageObject:
	name = '';
	isoCode = '';
	def __init__(self, languageName, languageIsoCode):	
		self.name = languageName;
		self.isoCode = languageIsoCode;

Session = sessionmaker(db);  
session = Session();
base.metadata.create_all(db);

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
#			tempArr.append(languageObject(lang.name, identifierName));
#	return tempArr;
#print(getIdentifier());

def getNameFromIdentifierKey(identifier_key):
	language_identifier_link = session.query(languageidentifier).filter(languageidentifier.identifier_pk == identifier_key).all()[0];
	language_entity = session.query(language).filter(language.pk ==language_identifier_link.language_pk).all()[0];
	return language_entity;

def getIdentifier():
	print("Generating languageObject Array with Glottolog's Database");
	identifiers = session.query(Identifier).filter(Identifier.type == 'iso639-3').all(); 
	tempArr = [];
	for identifier in identifiers:
		iso_code = identifier.name;
		language_entity = getNameFromIdentifierKey(identifier.pk);
		tempArr.append(languageObject(language_entity.name, iso_code));
	return tempArr;

def populateISODictionary():
	print("Generating Dictionary with Wikitounges' Database");
	with open('lang.csv') as langread:
		tempDict = {};
		csv_reader = csv.reader(langread, delimiter=',');
		#element[0] is the Iso639-3 code of each language in Wikitounges' database
		#element[1] is the name of the language of element[0]
		for element in csv_reader:
			tempDict[element[0]] = WikitoungesIsoObject(element[1], False);
		return tempDict;

def getDifference():
	Glottolog_only = [];
	Wikitounges_only = [];
	lang_dict = populateISODictionary(); #Iso639-3 codes from Wikitounges' database
	idenArr = getIdentifier(); #Iso639-3 codes from Glottolog's database
	print("Checking Which Language is in Glottolog Only.");
	for identifier in idenArr:
		try:
			get = lang_dict[identifier.isoCode];
			lang_dict[identifier.isoCode] = WikitoungesIsoObject(lang_dict[identifier.isoCode].name, True);
		except:
			Glottolog_only.append(identifier);
	print("Checking Which Language is in Wikitounges Only.");
	for isoCode, wikitoungesIsoObj in lang_dict.items():
		if not(wikitoungesIsoObj.checked):
			Wikitounges_only.append(languageObject(wikitoungesIsoObj.name, isoCode));
	return {"Glottolog_only": sorted(Glottolog_only, key=lambda langObject: langObject.isoCode), "Wikitounges_only": sorted(Wikitounges_only, key=lambda langObject: langObject.isoCode)};

def developmentOutput(val):
	print("\nGlottolog Only: \n");
	for i in val["Glottolog_only"]:
		print(i.isoCode + "    " + i.name);
	print("\nWikitounges Only: \n");
	for i in val["Wikitounges_only"]:
		print(i.isoCode + "    " + i.name);

diff = getDifference();
developmentOutput(diff);

