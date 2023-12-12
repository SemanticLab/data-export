import requests
import json
from datetime import date



lookup = json.load(open('../context/context-lookup.json'))
lookup_abbr = {}

for key in lookup:
	lookup_abbr[key.split("/")[-1]] = lookup[key]

lookup = lookup_abbr

exclude_instance_ofs = ['Q20664','Q22531','Q23571','Q23572','Q2013','Q19063', 'Q21151','Q26025']

projects = ['Q21217','Q18807','Q20655','Q20613','Q20719','Q19104','Q20517','Q24831']


	# 'Q21217': 'Linked Jazz Project',
	# 'Q20655': 'The International Sweethearts of Rhythm Project',
	# 'Q20613': 'Women of Jazz',
	# 'Q19104' : 'E.A.T. + LOD Project',
	# 'Q20517' : 'E.A.T. + LOD Bibliography Project',
	# 'Q18807' : 'Linking Lost Jazz Shrines',
	# 'Q20719': 'Local 496'
	# 'Q24831': 'Asian American Arts Centre Exhibition History'



blockToUrl = {}
labelLookup = {}
typeLookup = {}
blankNodeCounter = 0

def blankNodeID():
	global blankNodeCounter
	blankNodeCounter+=1
	return f"_:bn{blankNodeCounter}"

def getLabel(qid):
	global labelLookup

	if qid in labelLookup:
		return(labelLookup[qid])
	else:
		return(f"semlab:{qid}")

def getType(qid):
	global typeLookup

	if qid in typeLookup:
		return(typeLookup[qid])
	else:
		return(f"semlab:NoType")




def returnValues(claims):

	values = {
		'items': [],
		'literals': []
	}

	for claim in claims:

		if 'datavalue' not in claim['mainsnak']:
			continue
		
		if 'entity-type' in claim['mainsnak']['datavalue']['value']:

			c = {
				'qid': claim['mainsnak']['datavalue']['value']['id'],
				'label' : getLabel(claim['mainsnak']['datavalue']['value']['id']),
				'quals': [],
				'refs': [],
			}

			t = getType(c['qid'])
			if t in lookup:
				c['@type'] = lookup[t]
			else:
				c['@type'] = f"semlab:{t}"

			if 'qualifiers' in claim:
				
				for qual_property in claim['qualifiers']:

					for qual_claim in claim['qualifiers'][qual_property]:

						if 'datavalue' not in qual_claim:
							print("\n\n\n\n\n\n NO datavalue",qual_claim)
							continue

						if 'entity-type' in qual_claim['datavalue']['value']:
							q = {
								'qid': qual_claim['datavalue']['value']['id'],
								'label' : getLabel(qual_claim['datavalue']['value']['id'])
							}	
							if qual_property in lookup:
								q['prop'] = lookup[qual_property]
							else:
								q['prop'] = f"semlab:{qual_property}"

							c['quals'].append(q)						
						else:
							q = {
								'value': qual_claim['datavalue']['value']
							}	
							if qual_property in lookup:
								q['prop'] = lookup[qual_property]
							else:
								q['prop'] = f"semlab:{qual_property}"

							c['quals'].append(q)						


			if 'references' in claim:
				for ref_claims in claim['references']:

					for ref_property in ref_claims['snaks']:

						for ref_claim in ref_claims['snaks'][ref_property]:

							if 'entity-type' in ref_claim['datavalue']['value']:
								q = {
									'qid': ref_claim['datavalue']['value']['id'],
									'label' : getLabel(ref_claim['datavalue']['value']['id'])
								}	
								if ref_property in lookup:
									q['prop'] = lookup[ref_property]
								else:
									q['prop'] = f"semlab:{ref_property}"

								t = getType(q['qid'])
								if t in lookup:
									q['@type'] = lookup[t]
								else:
									q['@type'] = f"semlab:{t}"


								c['refs'].append(q)						
							else:
								q = {
									'value': ref_claim['datavalue']['value']
								}	
								if ref_property in lookup:
									q['prop'] = lookup[ref_property]
								else:
									q['prop'] = f"semlab:{ref_property}"

								c['refs'].append(q)	
				



			values['items'].append(c)

		elif 'entity-type' not in claim['mainsnak']['datavalue']['value']:

			c = {
				'value': claim['mainsnak']['datavalue']['value'],
			}



			values['literals'].append(c)





	return values


# build some lookups first of all the blocks
sparql = """
	SELECT *
	WHERE 
	{
	  
	  ?item wdt:P1 wd:Q2013.
      ?item wdt:P20 ?textUrl.
	}
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
	blockToUrl[result['item']['value'].split('/')[-1]] = result['textUrl']['value']



# get the labels for everything
sparql = """
	SELECT ?item ?itemLabel 
	WHERE 
	{
	  ?item wdt:P1 ?type. 
	  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } # Helps get the label in your language, if not, then en language
	}
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
	labelLookup[result['item']['value'].split('/')[-1]] = result['itemLabel']['value']


# get the types for everything
sparql = """
	SELECT ?item ?type
	WHERE 
	{
	  ?item wdt:P1 ?type. 
	  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } # Helps get the label in your language, if not, then en language
	}
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
	
	typeLookup[result['item']['value'].split('/')[-1]] = result['type']['value'].split('/')[-1]
















# get the title for all the projects

project_qids = 'wd:' + " wd:".join(projects)

sparql = f"""
	SELECT ?project ?projectLabel
	WHERE 
	{{
	  
	  VALUES ?project {{ {project_qids} }} .
	  
	  ?project wdt:P1 ?instaceOfTypes .

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}

	}}
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
projects_labels = {}

for result in data['results']['bindings']:	
	projects_labels[result['project']['value'].split("/")[-1]] = result['projectLabel']['value']

today = str(date.today())


toc_markdown = ""

markdown = f"""


# Semantic Lab Data Export
---
Generated: {today}

<TOC_HERE>

"""



for project_qid in projects:


	#exclude_instance_ofs

	project_label = projects_labels[project_qid]
	project_filename_base = project_label.lower().replace(" ","_").replace('.','').replace('+','').replace(' ','-') + "__"


	markdown = markdown + f"""
## {project_label}

| Entity | Link                       | Count |
|--------|----------------------------|-------|"""


	
	toc_markdown = toc_markdown + f"- [{project_label}](#{project_label.lower().replace('.','').replace('+','').replace(' ','-')})\n"




	wdId = f"wd:{project_qid}"

	# get all the instance ofs for this project
	sparql = f"""
		SELECT DISTINCT ?type ?typeLabel 
		WHERE 
		{{
		  

			  ?item wdt:P11 {wdId}. 
			  ?item wdt:P1 ?type.
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}

		  
		}}
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
	todo_instances_ofs = []
	todo_instances_ofs_all = []
	todo_instances_ofs_lookup = {}
	counter = 0
	for result in data['results']['bindings']:

		i = result['type']['value'].split("/")[-1]
		i_label = result['typeLabel']['value']
		if i not in exclude_instance_ofs:
			todo_instances_ofs.append(i)
			todo_instances_ofs_all.append(i)

			todo_instances_ofs_lookup[i] = i_label


	print(project_filename_base)
	print(todo_instances_ofs)
	print(todo_instances_ofs_lookup)

	todo_instances_ofs = sorted(todo_instances_ofs)
	todo_instances_ofs.insert(0, "all") 

	for todo_instance in todo_instances_ofs:


		all_agents = []

		if todo_instance == 'all':
			use_filename = project_filename_base + 'all.jsonld'
			table_name = "All"
			todo_instance = 'wd:' + " wd:".join(todo_instances_ofs_all) 
		else:
			use_filename = project_filename_base + todo_instances_ofs_lookup[todo_instance].lower().replace(" ","_") + '.jsonld'
			table_name = todo_instances_ofs_lookup[todo_instance].title()
			todo_instance = 'wd:' + todo_instance

		# get all the agents for this project
		sparql = f"""
			SELECT ?item
			WHERE 
			{{
			  
			  VALUES ?instaceOfTypes {{ {todo_instance} }} .
			  
			  ?item wdt:P1 ?instaceOfTypes .
			  ?item wdt:P11 wd:{project_qid} .
			  
			}}
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
		

		counter = 0

		total_agents = len(data['results']['bindings'])

		for result in data['results']['bindings']:



			qid = result['item']['value'].split('/')[-1]

			# qid = 'Q16'

			# if qid != 'Q314':
			# 	continue

			url = f"https://base.semlab.io/wiki/Special:EntityData/{qid}.json"

			special_data_page = requests.get(url,headers=headers)

			agent_data = special_data_page.json()


			agent_data = agent_data['entities'][qid]

			label = "No Label"
			if 'labels' in agent_data:
				if 'en' in agent_data['labels']:
					label = agent_data['labels']['en']['value']



			# build the main agent first

			agent = {
				"@context": "https://raw.githubusercontent.com/SemanticLab/data-export/main/context/context.jsonld",
				"@id" : f"semlab:{qid}",
				"rdfs:label" : label,
			}

			for claim in agent_data['claims']:

				if claim == 'P1':

					values = returnValues(agent_data['claims'][claim])
					if len(values['items']) > 0:
						agent['@type'] = []
						for item in values['items']:
							t = f"semlab:{item['qid']}"
							if item['qid'] in lookup:
								t = lookup[item['qid']]

							agent['@type'].append(t)

					
					# agent['@type'] = instance_of_mapping[claim]



				# if claim in attribute_mappings:

				# 	values = returnValues(agent_data['claims'][claim])

				# 	p = attribute_mappings[claim]

				# 	agent[p] = []

				# 	if len(values['literals']) > 0:
				# 		for l in values['literals']:
				# 			agent[p].append(l['value'])

				# 	if len(values['items']) > 0:
				# 		for i in values['items']:
							
				# 			agent[p].append({
				# 				'@id': f"semlab:{i['qid']}",
				# 				'rdfs:label': i['label']
				# 			})



				

				if claim in lookup:


					
					values = returnValues(agent_data['claims'][claim])

					

					p = lookup[claim]

					if len(values['items']) > 0:
						agent[p] = []


						for i in values['items']:
							
							event = {
								"@id" : blankNodeID(),
								"@type" : "RelEvent",
								"agentObj" : [],												
							}

							event_agent = {
								"@id" : f"semlab:{i['qid']}",
								"rdfs:label" : i['label']
							}
							if '@type' in i:
								event_agent['@type'] = i['@type']

							if len(i['quals']) > 0:

								event_agent_quals = {}

								for qual in i['quals']:

									if qual['prop'] not in event_agent_quals:
										event_agent_quals[qual['prop']] = []

									if 'qid' in qual:
										tmpq = {
											'@id' : f"semlab:{qual['qid']}",
											"rdfs:label" : qual['label']
										}
										event_agent_quals[qual['prop']].append(tmpq)
									else:
										tmpq = qual['value']

										if isinstance(tmpq, str):
											if tmpq.isnumeric():
												tmpq = int(tmpq)
										else:
											if 'time' in tmpq:
												tmpq = tmpq['time']

										event_agent_quals[qual['prop']].append(tmpq)


								for key in event_agent_quals:
									event[key] = event_agent_quals[key]

							event['agentObj'] = event_agent

							if len(i['refs']) > 0:

								event_refs = {}	

								for ref in i['refs']:

									

									if ref['prop'] not in event_refs:
										event_refs[ref['prop']] = []


									if 'qid' in ref:

										r = {
											'@id': f"semlab:{ref['qid']}",
											"rdfs:label" : ref['label'],								
										}

										if ref['qid'] in blockToUrl:
											r['blockTextURL'] = blockToUrl[ref['qid']]

										event_refs[ref['prop']].append(r)
									else:

										event_refs[ref['prop']].append(ref['value'])

									
								for key in event_refs:
									event[key] = event_refs[key]
								

							agent[p].append(event)

					if len(values['literals']) > 0:
						agent[p] = []
						for i in values['literals']:


							event = {
								# "@id" : blankNodeID(),
								# "@type" : "RelEvent",
								"@value" : i['value'],												
							}

							# if len(i['quals']) > 0:

							# 	event_agent_quals = {}

							# 	for qual in i['quals']:

							# 		if qual['prop'] not in event_agent_quals:
							# 			event_agent_quals[qual['prop']] = []

							# 		if 'qid' in qual:
							# 			tmpq = {
							# 				'@id' : f"semlab:{qual['qid']}",
							# 				"rdfs:label" : qual['label']
							# 			}
							# 			event_agent_quals[qual['prop']].append(tmpq)
							# 		else:
							# 			tmpq = qual['value']
							# 			if tmpq.isnumeric():
							# 				tmpq = int(tmpq)

							# 			event_agent_quals[qual['prop']].append(tmpq)


							# 	for key in event_agent_quals:
							# 		event[key] = event_agent_quals[key]


							# if len(i['refs']) > 0:

							# 	event_refs = {}	

							# 	for ref in i['refs']:

									

							# 		if ref['prop'] not in event_refs:
							# 			event_refs[ref['prop']] = []


							# 		if 'qid' in ref:

							# 			r = {
							# 				'@id': f"semlab:{ref['qid']}",
							# 				"rdfs:label" : ref['label'],								
							# 			}

							# 			if ref['qid'] in blockToUrl:
							# 				r['semlab:blockTextURL'] = blockToUrl[ref['qid']]

							# 			event_refs[ref['prop']].append(r)
							# 		else:

							# 			event_refs[ref['prop']].append(ref['value'])

									
							# 	for key in event_refs:
							# 		event[key] = event_refs[key]








							agent[p].append(event)


			counter+=1 
			# print(json.dumps(agent,indent=2))
			all_agents.append(agent)
			print (f"{counter}/{len(data['results']['bindings'])}")
			# if counter>2:
			# 	break
		

		json.dump(all_agents,open(f'../data/{use_filename}','w'),indent=2)

		markdown = markdown + f"""\n| {table_name}    | [{use_filename}](https://github.com/SemanticLab/data-export/blob/main/data/{use_filename}) | {total_agents}  |"""




		markdown_with_toc = markdown.replace("<TOC_HERE>",toc_markdown)
		print(markdown_with_toc)

		with open('../README.md','w') as mkout:
			mkout.write(markdown_with_toc)









