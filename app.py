from flask import Flask, render_template, request
import pysolr

app = Flask(__name__)

# Setup a Solr instance
solr = pysolr.Solr('http://localhost:8983/solr/airbnb', timeout=10)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        results = search(query)
        return render_template('results.html', query=query, results=results)
    return render_template('index.html')



def search(query):
    # Execute the query in Solr
    results = solr.search(query, **{
        'rows': 10,
        'fl': 'id,score,NAME,neighbourhood,neighbourhood_group,country,instant_bookable,cancellation_policy,price,'
              'house_rules,room_type,host_identity_verified,review_rate_number',
        'hl': 'true',
        'hl.fl': '*',
        'hl.fragsize': 99999,
    })

    # Retrieve the highlighting information from the results
    highlighting = results.highlighting

    # Convert results to a list of dictionaries and include highlighting
    processed_results = []
    for result in results:
        doc = dict(result)

        # Retrieve the highlighted snippets for each field
        highlighted_fields = {}
        for field in highlighting.get(result['id'], {}):
            snippets = highlighting[result['id']][field]
            highlighted_fields[field] = snippets[0] if snippets else ''

        doc['highlighted_fields'] = highlighted_fields
        processed_results.append(doc)
    return processed_results


if __name__ == '__main__':
    app.run(debug=True)
