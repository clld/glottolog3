#Pre-development Notes:
#scan through identifier for all iso639-3 code
#make the csv to a hashtable then for glottolog data only needs o(1) retrieval time, if error, means not exist
#arr1 = what wikitounge has and glottolog doesnt, save the iso code
#for special iso code wikitounge make, see if name exists in db, if yes find corresponding glottolog code, else indicate that as new lang
#arr2 = what glottolog has and wikitounge doesnt then save those iso code and find corresponding glottolog code by saving that identifier id

from sqlalchemy import create_engine  
from sqlalchemy import Column, String  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
import csv, sqlite3

#change this db_string to the actual postgres db containing the data
db_string = "postgres://postgres:@127.0.0.1:5432/glottolog-3.2";
db = create_engine(db_string);  
base = declarative_base();

class Identifier(base):
	__tablename__ = 'identifier';
	pk = Column(String, primary_key=True);
	jsondata = Column(String);
	name = Column(String);
	description = Column(String);
	markup_description = Column(String);
	id = Column(String);
	type = Column(String);
	lang = Column(String);

#The two classes below are for further queries if needed (such as glottocode)
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

Session = sessionmaker(db);  
session = Session();
base.metadata.create_all(db);

def getIdentifier():
	identifiers = session.query(Identifier); 
	tempArr = [];
	for identifier in identifiers:
		if (identifier.type == 'iso639-3'):
			tempArr.append((identifier.pk,identifier.name));
	return tempArr;

def populateISODictictionary():
	#potential problem: multiple #NAME entries for ISO639-3 column, resulting is deleting duplicate when using dictionary
	with open('lang.csv') as langread:
		tempDict = {};
		csv_reader = csv.reader(langread, delimiter=',');
		for lang_line in csv_reader:
			tempDict[lang_line[0]] = (0,lang_line[1]) ;
		return tempDict;

def getDifference():
	lang_dict = populateISODictictionary();
	Glottolog_only = [];
	Wikitounge_only = [];
	idenArr = getIdentifier();
	for identifier in idenArr:
		try:
			get = lang_dict[identifier[1]];
			lang_dict[identifier[1]] = (1, lang_dict[identifier[1]][1]);
		except:
			Glottolog_only.append((identifier[0],identifier[1]));
	for ld in lang_dict:
		if lang_dict[ld][0] == 0:
			Wikitounge_only.append((ld, lang_dict[ld][1]));
	return (Glottolog_only,Wikitounge_only);

def developmentOutput(d):
	print("\nGlottolog Only: \n");
	for i in d[0]:
		print(i);
	print("\nWikitounge Only: \n");
	for i in d[1]:
		print(i);

diff = getDifference();
developmentOutput(diff);

