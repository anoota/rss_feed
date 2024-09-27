import requests
import xml.etree.ElementTree as ET
from flask import Flask, jsonify
from flask_caching import Cache
from flask_cors import CORS

config = {
    "DEBUG": True,          
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 900
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

# Enable CORS for all routes
CORS(app)

RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"


class GeneRisk:
    def __init__(self, gene, risk):
        self.gene = gene
        self.risk = risk

    def count_risk(self, category):

        return sum(1 for risk_level in self.risk if risk_level['risk'] == category)

    
    def high_risk(self):
        #  genes with high risk (same level, count the number of high risk conditions from high to low)
        return self.count_risk('high') 
    
    def inconclusive_risk(self):
        return self.count_risk('inconclusive')

    def low_risk(self):
         return self.count_risk('low')


def sort_genes(genes):
    high = [gene for gene in genes if gene.high_risk() and not gene.inconclusive_risk()] 
    high_inconclusive = [gene for gene in genes if  gene.high_risk() and gene.inconclusive_risk()]
    inconclusive = [ gene for gene in genes if gene.inconclusive_risk() and not gene.high_risk()  ]
    low  = [gene for gene in genes if gene.low_risk() and not gene.high_risk() and not gene.inconclusive_risk()]

    high.sort(key=lambda c: c.count_risk('high'), reverse=True)
    high_inconclusive.sort(key=lambda c: c.count_risk('high'), reverse=True)
    inconclusive.sort(key=lambda c: c.count_risk('inconclusive'), reverse=True)
    low.sort(key=lambda c: c.count_risk('low'), reverse=True)

    return high + high_inconclusive + inconclusive + low


# Fetch and cache RSS feed
@cache.cached(timeout=900)
def fetch_rss():
    # Fetches the RSS feed from the NYT Technology section.
    response = requests.get(RSS_URL)
    if response.status_code == 200:
        return response.content
    else:
        return None

# Parse the RSS feed using ElementTree
def parse_rss(xml_data):
    root = ET.fromstring(xml_data)

    articles = []

    # know all the elements in the entire tree.
    #print ([elem.tag for elem in root.iter()])

    # Find all articles in the RSS feed
    for item in root.findall(".//item"):
        title = item.find("title").text
        description = item.find("description").text
        link = item.find("link").text
        pub_date = item.find("pubDate").text
        image = None

        # Search for the media:content tag 
        media_content = item.find("{http://search.yahoo.com/mrss/}content")
        if media_content is not None:
            image = media_content.attrib.get("url")

        # Search for the creator of the article
        creator = item.find("{http://purl.org/dc/elements/1.1/}creator")
        if creator is not None:
            author = creator.text
        else:
            author = "By Unknown"
     
        articles.append({
            'title': title,
            'description': description,
            'link': link,
            'published': pub_date,
            'image': image,
            'author': author
        })
    return articles

# Endpoint for accesing the rss feed data
@app.route('/get/rss', methods=['GET'])
def index():
    rss_data = fetch_rss()
    if rss_data:
        articles = parse_rss(rss_data)
        return jsonify(articles)
    else:
        return jsonify({"error": "Failed to fetch RSS feed"}), 500

gene_data = [
    GeneRisk("gene1", [{"condition": "disease1", "risk": "high"}, {"condition": "disease2", "risk": "low"}]),
    GeneRisk("gene2", [{"condition": "disease3", "risk": "inconclusive"}, {"condition": "disease4", "risk": "low"}]),
    GeneRisk("gene3", [{"condition": "disease3", "risk": "high"}, {"condition": "disease2", "risk": "high"}]),
    GeneRisk("gene4", [{"condition": "disease3", "risk": "high"}, {"condition": "disease5", "risk": "inconclusive"}]),
    GeneRisk("gene5", [{"condition": "disease1", "risk": "inconclusive"}]),
    GeneRisk("gene6", [{"condition": "disease2", "risk": "low"}])
]
# Endpoint for accesing the gene soritng feed data
# fwang@natera.com
@app.route('/genes', methods=['GET'])
def get_sorted_genes():
    sorted_genes = sort_genes(gene_data)   
    
    # Building the JSON response
    result = [
        {
            "gene": gene.gene,
            "high_risk_count": gene.high_risk(),
            "inconclusive_count": gene.inconclusive_risk(),
            "low_risk_count": gene.low_risk()
        }
        for gene in sorted_genes
    ]

    return result

if __name__ == '__main__':
    app.run()
