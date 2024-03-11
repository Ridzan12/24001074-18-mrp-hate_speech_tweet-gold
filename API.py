import re
import pandas as pd
from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from

app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

# Swagger 
swagger_template = {
    "info": {
        "title":  "API Documentation for Data Processing and Modeling",
        "version": "1.0.0",
        "description": "API Documentation"
    },
    "host": "127.0.0.1:5000"
}
swagger_config = {
    'headers': [],
    'specs': [{
        'endpoint': 'docs',
        'route': '/docs.json',
    }],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/docs/'
}
swagger = Swagger(app, template=swagger_template, config=swagger_config)


def lowercase_text_with_regex(text):
    return re.sub(r'.', lambda match: match.group(0).lower(), text)

def clean_tweet_text(df):
    pattern = r"\buser\b|\brt\b|\n|;|\(--!\)|-|:|\\|:\)|:\(|ð|\'|'\s|,\s*,|\"n\"|\d+\.\s|URL|"
    df['Tweet'] = df['Tweet'].apply(lambda x: re.sub(pattern, '', x))
    pattern_unicode_hex = r'(x[a-f0-9]{2})+'
    df['Tweet'] = df['Tweet'].apply(lambda x: re.sub(pattern_unicode_hex, '', x))
    return df

# Text Processing endpoint
@swag_from("docs/textProcessing.yaml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():
    text = request.form.get('text')
    cleaned_text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    # new function 
    cleaned_text = lowercase_text_with_regex(cleaned_text)
    json_response = {
        'status_code': 200,
        'description': "Processed text",
        'data': cleaned_text,
    }
    return jsonify(json_response)

# Text Processing from File endpoint
@swag_from("docs/fileTextProcessing.yaml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():
    try:
        file = request.files.getlist('file')[0]
        df = pd.read_csv(file)
        texts = df.text.tolist()
        cleaned_texts = [re.sub(r'[^a-zA-Z0-9]', ' ', text) for text in texts]
        # cleaning functions 
        df = pd.DataFrame(cleaned_texts, columns=['text'])
        df = clean_tweet_text(df)
        cleaned_texts = df.text.tolist()
        json_response = {
            'status_code': 200,
            'description': "Processed text",
            'data': cleaned_texts,
        }
    except Exception as e:
        json_response = {
            'status_code': 500,
            'description': "An error occurred while processing the file",
            'error': str(e)
        }
    return jsonify(json_response)

if __name__ == '__main__':
    app.run()