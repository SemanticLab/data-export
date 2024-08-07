import requests
import json

def to_camel_case(text):
    s = text.replace("-", " ").replace("_", " ")
    s = s.split()
    if len(text) == 0:
        return text
    return s[0] + ''.join(i.capitalize() for i in s[1:])


# load the template

context_data = json.load(open('../context/dev-context.jsonld'))
context_data_strict = json.load(open('../context/dev-context.jsonld'))
context_reverse_lookup = {}



sparql = """
SELECT ?property ?propertyLabel ?exportAlias ?propertyDescription (GROUP_CONCAT(DISTINCT(?altLabel); separator = ", ") AS ?altLabel_list) (GROUP_CONCAT(DISTINCT(?equalProp); separator = ", ") AS ?equalProp_list) WHERE {
    ?property a wikibase:Property .
    OPTIONAL { ?property skos:altLabel ?altLabel . FILTER (lang(?altLabel) = "en") }
    OPTIONAL { ?property wdt:P41 ?equalProp .}
    OPTIONAL { ?property wdt:P204 ?exportAlias .}
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" .}
 }
GROUP BY ?property ?propertyLabel ?exportAlias ?propertyDescription
LIMIT 5000

"""
headers = {
    'Accept': 'application/sparql-results+json',
}
params = {
	'query' : sparql
}
response = requests.get(
    'https://query.semlab.io/proxy/wdqs/bigdata/namespace/wdq/sparql',
    params=params,
    headers=headers,
)

data = response.json()
for result in data['results']['bindings']:

	try:
		alias = result['exportAlias']['value']
	except:
		print(" No exprot alias set for:",result)

		alias = to_camel_case(result['propertyLabel']['value'])

	uri = result['property']['value']
	toadd = {
		'@id' : uri,
		'skos:prefLabel': result['propertyLabel']['value']
	}

	if 'altLabel_list' in result:	
		altLabels = [x.strip() for x in result['altLabel_list']['value'].split(",")]
		while("" in altLabels):
			altLabels.remove("")		
		if len(altLabels) >0:
			toadd['skos:altLabel'] = altLabels

	if 'equalProp_list' in result:
		equalProp_list =  [x.strip() for x in result['equalProp_list']['value'].split(",")]  
		while("" in equalProp_list):
			equalProp_list.remove("")

		if len(equalProp_list) >0:
			toadd['owl:equivalentClass'] = equalProp_list


	if 'propertyDescription' in result:
		desc = result['propertyDescription']['value']

		toadd['skos:note'] = desc

	context_data['@context'][alias] = toadd
	
	context_data_strict['@context'][alias] = {
		'@id' : uri.replace("http://base.semlab.io/entity/",'semlab:'),
		"@type": "@id",
		"@container": "@set"
	}
	# '@type': 'rdf:Property'
	
	context_reverse_lookup[uri] = alias




# --------




sparql = """
	SELECT ?instanceOf ?instanceOfLabel ?instanceOfDescription (GROUP_CONCAT(DISTINCT(?altLabel); separator = ", ") AS ?altLabel_list) (GROUP_CONCAT(DISTINCT(?equalClass); separator = ", ") AS ?equalClass_list) WHERE {
	    
	    ?item wdt:P1 ?instanceOf
	    OPTIONAL { ?instanceOf skos:altLabel ?altLabel . FILTER (lang(?altLabel) = "en") }
	    OPTIONAL { ?instanceOf wdt:P54 ?equalClass .}

	  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" .}
	 }
	GROUP BY ?instanceOf ?instanceOfLabel ?instanceOfDescription
	ORDER BY LCASE(?instanceOfLabel)
	LIMIT 5000
"""
headers = {
    'Accept': 'application/sparql-results+json',
}
params = {
	'query' : sparql
}
response = requests.get(
    'https://query.semlab.io/proxy/wdqs/bigdata/namespace/wdq/sparql',
    params=params,
    headers=headers,
)

data = response.json()
for result in data['results']['bindings']:



	alias = result['instanceOfLabel']['value'].lower().title().replace(" ",'')
	uri = result['instanceOf']['value']

	toadd = {
		'@type': 'rdfs:Class',
		'@id' : uri,
		'skos:prefLabel': result['instanceOfLabel']['value']
	}

	if 'altLabel_list' in result:	
		altLabels = [x.strip() for x in result['altLabel_list']['value'].split(",")]
		while("" in altLabels):
			altLabels.remove("")		
		if len(altLabels) >0:
			toadd['skos:altLabel'] = altLabels

	if 'equalClass_list' in result:
		equalClass_list =  [x.strip() for x in result['equalClass_list']['value'].split(",")]  
		while("" in equalClass_list):
			equalClass_list.remove("")

		if len(equalClass_list) >0:
			toadd['owl:equivalentClass'] = equalClass_list


	if 'instanceOfDescription' in result:
		desc = result['instanceOfDescription']['value']

		toadd['skos:note'] = desc

	
	context_data['@context'][alias] = toadd
	
	context_data_strict['@context'][alias] = {
		'@id' : uri.replace("http://base.semlab.io/entity/",'semlab:'),
		"@type": "@id",
	}

	# 	"@type": "@id",


	context_reverse_lookup[uri] = alias






json.dump(context_data_strict, open('../context/context.jsonld','w'), indent=2)
json.dump(context_data,open('../context/context-doc.jsonld','w'), indent=2)
json.dump(context_reverse_lookup,open('../context/context-lookup.json','w'),indent=2)














#         "MusicVenue" : "https://base.semlab.io/entity/Q18806",
#         "Block" : "https://base.semlab.io/entity/Q2013",

#         "instanceOf":{
#             "@id": "https://base.semlab.io/entity/P01",
#             "skos:note": "that class of which this subject is a particular example and member",
#             "owl:equivalentProperty": ['http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'https://www.wikidata.org/wiki/Property:P31']
#         }







# instance_of_mapping = {
# 	"Q1" : "foaf:Person",
# 	"Q18805": "mo:MusicGroup",
# 	"Q2013" : "Block",
# 	"Q18806" : "MusicVenue"
# }

# attribute_mappings = {
	
# 	"P42" : "demographica",
# 	"P8" : "wikidataQId",
# 	"P3" : "schema:image",
# 	"P69" : "residentOf",
# 	"P44" : "occupation",
# 	"P43" : "countryOfCitizenship",
# 	"P152" : "streetAddress",
# }


# relationship_mappings = {
	

# 	"P29" : "lj:knowsOf",
# 	"P39" : "lj:influencedBy",
# 	"P36" : "lj:playedTogether",
# 	"P32" : "rel:acquaintanceOf",
# 	"P31" : "mo:collaborated_with",
# 	"P33" : "rel:hasMet",
# 	"P34" : "rel:friendOf",
# 	"P30" : "rel:mentorOf",
# 	"P35" : "lj:inBandTogether",
# 	"P38" : "lj:touredWith",
# 	"P68" : "performedAt",
# 	"P37" : "playedUnder",
# 	"P160" : "lj:bandLeaderOf",
# 	"P65" : "memberOf",
# 	"P110" : "schema:worksFor",
# 	"P70" : "grewUpWith",
# 	"P67" : "visitedPlace",
# 	"P113" : "relativeOf",
# 	"P71" : "recordedWith",
# 	"P172" : "photographedBy",
# 	"P72" : "lj:bandLeaderOf",
# 	"P123" : "lifePartner",
# 	"P168" : "attendedPerformanceAt",
# 	"P63" : "attendedPerformanceOf",
# 	"P144" : "booked",
# 	"P66" : "knowsOfPlace",
# 	"P143" : "frequentedPlace",
# 	"P161" : "rel:mentorOf",
# 	"P159" : "recordedAtPlace",
# 	"P196" : "contributedTo",
# 	"P111" : "wasInvitedTo",
# 	"P158" : "supervisorOf",
# 	"P154" : "supervisedBy",
# 	"P162" : "studentOf"

# }


# ref_qual_mapping = {
	
# 	'P25': "semlab:relationshipGeneration",
# 	"P26" : "semlab:referenceBlock",
# 	"P40" : "semlab:crowdSourceConsensus",
# 	"xxxxx" : "xxxxxxxxx",
# 	"xxxxx" : "xxxxxxxxx",
# }





# all_agents = []
# blockToUrl = {}
# labelLookup = {}
# typeLookup = {}
# blankNodeCounter = 0

# def blankNodeID():
# 	global blankNodeCounter
# 	blankNodeCounter+=1
# 	return f"_bn{blankNodeCounter}"

# def getLabel(qid):
# 	global labelLookup

# 	if qid in labelLookup:
# 		return(labelLookup[qid])
# 	else:
# 		return(f"semlab:{qid}")

# def getType(qid):
# 	global typeLookup

# 	if qid in typeLookup:
# 		return(typeLookup[qid])
# 	else:
# 		return(f"semlab:NoType")



# def returnValues(claims):

# 	values = {
# 		'items': [],
# 		'literals': []
# 	}

# 	for claim in claims:


		
# 		if 'entity-type' in claim['mainsnak']['datavalue']['value']:

# 			c = {
# 				'qid': claim['mainsnak']['datavalue']['value']['id'],
# 				'label' : getLabel(claim['mainsnak']['datavalue']['value']['id']),
# 				'quals': [],
# 				'refs': [],
# 			}

# 			t = getType(c['qid'])
# 			if t in instance_of_mapping:
# 				c['@type'] = instance_of_mapping[t]
# 			else:
# 				c['@type'] = f"semlab:{t}"

# 			if 'qualifiers' in claim:
				
# 				for qual_property in claim['qualifiers']:

# 					for qual_claim in claim['qualifiers'][qual_property]:
# 						if 'entity-type' in qual_claim['datavalue']['value']:
# 							q = {
# 								'qid': qual_claim['datavalue']['value']['id'],
# 								'label' : getLabel(qual_claim['datavalue']['value']['id'])
# 							}	
# 							if qual_property in ref_qual_mapping:
# 								q['prop'] = ref_qual_mapping[qual_property]
# 							else:
# 								q['prop'] = f"semlab:{qual_property}"

# 							c['quals'].append(q)						
# 						else:
# 							q = {
# 								'value': qual_claim['datavalue']['value']
# 							}	
# 							if qual_property in ref_qual_mapping:
# 								q['prop'] = ref_qual_mapping[qual_property]
# 							else:
# 								q['prop'] = f"semlab:{qual_property}"

# 							c['quals'].append(q)						


# 			if 'references' in claim:
# 				for ref_claims in claim['references']:

# 					for ref_property in ref_claims['snaks']:

# 						for ref_claim in ref_claims['snaks'][ref_property]:

# 							if 'entity-type' in ref_claim['datavalue']['value']:
# 								q = {
# 									'qid': ref_claim['datavalue']['value']['id'],
# 									'label' : getLabel(ref_claim['datavalue']['value']['id'])
# 								}	
# 								if ref_property in ref_qual_mapping:
# 									q['prop'] = ref_qual_mapping[ref_property]
# 								else:
# 									q['prop'] = f"semlab:{ref_property}"

# 								t = getType(q['qid'])
# 								if t in instance_of_mapping:
# 									q['@type'] = instance_of_mapping[t]
# 								else:
# 									q['@type'] = f"semlab:{t}"


# 								c['refs'].append(q)						
# 							else:
# 								q = {
# 									'value': ref_claim['datavalue']['value']
# 								}	
# 								if ref_property in ref_qual_mapping:
# 									q['prop'] = ref_qual_mapping[ref_property]
# 								else:
# 									q['prop'] = f"semlab:{ref_property}"

# 								c['refs'].append(q)	
				



# 			values['items'].append(c)

# 		elif 'entity-type' not in claim['mainsnak']['datavalue']['value']:

# 			c = {
# 				'value': claim['mainsnak']['datavalue']['value'],
# 			}



# 			values['literals'].append(c)





# 	return values




# # get the labels for everything
# sparql = """
# 	SELECT ?item ?itemLabel 
# 	WHERE 
# 	{
# 	  ?item wdt:P1 ?type. 
# 	  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } # Helps get the label in your language, if not, then en language
# 	}
# """
# headers = {
#     'Accept': 'application/sparql-results+json',
# }
# params = {
# 	'query' : sparql
# }
# response = requests.get(
#     'https://query.semlab.io/proxy/wdqs/bigdata/namespace/wdq/sparql',
#     params=params,
#     headers=headers,
# )
# data = response.json()
# for result in data['results']['bindings']:
# 	labelLookup[result['item']['value'].split('/')[-1]] = result['itemLabel']['value']


# # get the types for everything
# sparql = """
# 	SELECT ?item ?type
# 	WHERE 
# 	{
# 	  ?item wdt:P1 ?type. 
# 	  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } # Helps get the label in your language, if not, then en language
# 	}
# """
# headers = {
#     'Accept': 'application/sparql-results+json',
# }
# params = {
# 	'query' : sparql
# }
# response = requests.get(
#     'https://query.semlab.io/proxy/wdqs/bigdata/namespace/wdq/sparql',
#     params=params,
#     headers=headers,
# )
# data = response.json()
# for result in data['results']['bindings']:
	
# 	typeLookup[result['item']['value'].split('/')[-1]] = result['type']['value'].split('/')[-1]









# # get all the agents for this project
# sparql = """
# 	SELECT ?item
# 	WHERE 
# 	{
	  
# 	  VALUES ?instaceOfTypes {wd:Q1 wd:Q18805} .
	  
# 	  ?item wdt:P1 ?instaceOfTypes .
# 	  ?item wdt:P11 wd:Q21217 .
	  
# 	}
# """

# headers = {
#     'Accept': 'application/sparql-results+json',
# }

# params = {
# 	'query' : sparql
# }

# response = requests.get(
#     'https://query.semlab.io/proxy/wdqs/bigdata/namespace/wdq/sparql',
#     params=params,
#     headers=headers,
# )

# data = response.json()
# all_agents = []

# counter = 0
# for result in data['results']['bindings']:



# 	qid = result['item']['value'].split('/')[-1]

# 	# qid = 'Q16'

# 	url = f"https://base.semlab.io/wiki/Special:EntityData/{qid}.json"

# 	special_data_page = requests.get(url,headers=headers)

# 	agent_data = special_data_page.json()


# 	agent_data = agent_data['entities'][qid]

# 	label = "No Label"
# 	if 'labels' in agent_data:
# 		if 'en' in agent_data['labels']:
# 			label = agent_data['labels']['en']['value']



# 	# build the main agent first

# 	agent = {
# 		"@context": "https://raw.githubusercontent.com/SemanticLab/data-export/main/context/dev-context.jsonld",
# 		"@id" : f"semlab:{qid}",
# 		"rdfs:label" : label,
# 	}

# 	for claim in agent_data['claims']:

# 		if claim == 'P1':

# 			values = returnValues(agent_data['claims'][claim])
# 			if len(values['items']) > 0:
# 				agent['@type'] = []
# 				for item in values['items']:
# 					t = f"semlab:{item['qid']}"
# 					if item['qid'] in instance_of_mapping:
# 						t = instance_of_mapping[item['qid']]

# 					agent['@type'].append(t)

			
# 			# agent['@type'] = instance_of_mapping[claim]



# 		if claim in attribute_mappings:

# 			values = returnValues(agent_data['claims'][claim])

# 			p = attribute_mappings[claim]

# 			agent[p] = []

# 			if len(values['literals']) > 0:
# 				for l in values['literals']:
# 					agent[p].append(l['value'])

# 			if len(values['items']) > 0:
# 				for i in values['items']:
					
# 					agent[p].append({
# 						'@id': f"semlab:{i['qid']}",
# 						'rdfs:label': i['label']
# 					})





# 		if claim in relationship_mappings:

# 			values = returnValues(agent_data['claims'][claim])


# 			p = relationship_mappings[claim]

# 			if len(values['items']) > 0:
# 				agent[p] = []
# 				for i in values['items']:
					
# 					event = {
# 						"@id" : blankNodeID(),
# 						"@type" : "semlab:RelEvent",
# 						"semlab:agentObj" : [],												
# 					}

# 					event_agent = {
# 						"@id" : f"semlab:{i['qid']}",
# 						"rdfs:label" : i['label']
# 					}
# 					if '@type' in i:
# 						event_agent['@type'] = i['@type']

# 					if len(i['quals']) > 0:

# 						event_agent_quals = {}

# 						for qual in i['quals']:

# 							if qual['prop'] not in event_agent_quals:
# 								event_agent_quals[qual['prop']] = []

# 							if 'qid' in qual:
# 								tmpq = {
# 									'@id' : f"semlab:{qual['qid']}",
# 									"rdfs:label" : qual['label']
# 								}
# 								event_agent_quals[qual['prop']].append(tmpq)
# 							else:
# 								tmpq = qual['value']
# 								event_agent_quals[qual['prop']].append(tmpq)


# 						for key in event_agent_quals:
# 							event_agent[key] = event_agent_quals[key]

# 					event['semlab:agentObj'] = event_agent

# 					if len(i['refs']) > 0:

# 						event_refs = {}	

# 						for ref in i['refs']:

							

# 							if ref['prop'] not in event_refs:
# 								event_refs[ref['prop']] = []


# 							if 'qid' in ref:

# 								r = {
# 									'@id': f"semlab:{ref['qid']}",
# 									"rdfs:label" : ref['label'],								
# 								}

# 								if ref['qid'] in blockToUrl:
# 									r['semlab:blockTextURL'] = blockToUrl[ref['qid']]

# 								event_refs[ref['prop']].append(r)
# 							else:

# 								event_refs[ref['prop']].append(ref['value'])

							
# 						for key in event_refs:
# 							event[key] = event_refs[key]
						

# 				agent[p].append(event)





# 	counter+=1 
# 	# print(json.dumps(agent,indent=2))
# 	all_agents.append(agent)
# 	print (f"{counter}/{len(data['results']['bindings'])}")
# 	# if counter>10:
# 	# break
	
# 	json.dump(all_agents,open('../data/lj_all_agents.json','w'),indent=2)












