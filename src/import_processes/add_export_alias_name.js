import * as fs from 'fs';
import WBEdit from 'wikibase-edit';

var camalize = function camalize(str) {
    return str.toLowerCase().replace(/[^a-zA-Z0-9]+(.)/g, (m, chr) => chr.toUpperCase());
}



let generalConfig = JSON.parse(fs.readFileSync('config.json', 'utf8'));
const wbEdit = WBEdit(generalConfig);






(async() => {

	// get the labels of all the properties

	// https://tinyurl.com/ywjwobrg
    const options = {
        method: 'GET',
        headers: new Headers({'Api-User-Agent': 'username: MattTest export process 0.1', 'User-Agent': 'username: MattTest export process 0.1', 'Accept': 'application/sparql-results+json'}),
        mode: 'no-cors'
    };	
	let response = await fetch('https://query.semlab.io/proxy/wdqs/bigdata/namespace/wdq/sparql?query=SELECT%20%3Fproperty%20%3FpropertyLabel%20%3FexportAlias%20%3FpropertyDescription%20(GROUP_CONCAT(DISTINCT(%3FaltLabel)%3B%20separator%20%3D%20%22%2C%20%22)%20AS%20%3FaltLabel_list)%20(GROUP_CONCAT(DISTINCT(%3FequalProp)%3B%20separator%20%3D%20%22%2C%20%22)%20AS%20%3FequalProp_list)%20WHERE%20%7B%0A%20%20%20%20%3Fproperty%20a%20wikibase%3AProperty%20.%0A%20%20%20%20OPTIONAL%20%7B%20%3Fproperty%20skos%3AaltLabel%20%3FaltLabel%20.%20FILTER%20(lang(%3FaltLabel)%20%3D%20%22en%22)%20%7D%0A%20%20%20%20OPTIONAL%20%7B%20%3Fproperty%20wdt%3AP41%20%3FequalProp%20.%7D%0A%20%20%20%20OPTIONAL%20%7B%20%3Fproperty%20wdt%3AP204%20%3FexportAlias%20.%7D%0A%0A%20%20%0A%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20.%7D%0A%20%7D%0AGROUP%20BY%20%3Fproperty%20%3FpropertyLabel%20%3FexportAlias%20%3FpropertyDescription%0ALIMIT%205000%0A%0A%0A%0A',options);
	// only proceed once promise is resolved
	// console.log(await response.text())


	let data = await response.json();
	// only proceed once second promise is resolved

	console.log(data)

	for (let p of data.results.bindings){
		let label = p.propertyLabel.value
		let labelCamel = camalize(label)
		let uri = p.property.value
		let similar = (p.equalProp_list.value != '') ? p.equalProp_list.value.split(",") : []

		if (!p.exportAlias){
			console.log(labelCamel, label,uri,similar)

			await wbEdit.claim.create({
			  id: uri.replace("http://base.semlab.io/entity/",''),
			  property: 'P204',
			  value: labelCamel
			})


		}

	}

	// // let json = csvToJson.getJsonFromCsv("source_data.csv");
	// let json = csvToJson.fieldDelimiter(',').getJsonFromCsv('wikibase_naf_elements.csv');

	// for(let i=0; i<json.length;i++){

	// 	if (lookup[json[i].Elementname]){
	// 		console.log("Skipping ",json[i].Elementname)
	// 		continue
	// 	}

	// 	console.log('doing ', i)
	// 	let d = {
	// 		type: 'property',
	// 		datatype: json[i].Datatypeforproperty,
	// 		labels: {
	// 			// Set a label
	// 			en: json[i].Elementname,
	// 		},
	// 		descriptions: {
	// 			// Set a description
	// 			en: 'RDA ' + json[i].RelationshiporAttribute,
	// 		},  

	// 	  claims: {
	// 	  	P8: 'Q12',
	// 	  	P9: rangeMap[json[i].Range]
	// 	  },
		  
	// 	}

	//     console.log(json[i]);
	//     console.log(d)


	// 	const { entity } = await wbEdit.entity.create(d)
	// 	console.log('created item id', entity.id)

	//     lookup[json[i].Elementname] = entity.id


	//     fs.writeFileSync('mapping.json', JSON.stringify(lookup));

	//     await new Promise(r => setTimeout(r, 1000));

	//     // break


	// }








})();