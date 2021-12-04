import os
import openai
import sys
from flask import Flask
from flask import request, render_template

def fetch_explanation(regex, openai_key):
    openai.api_key = openai_key
    # TODO ADD CONTEXT
    incipit_explanation = 'import re\nregex = r"' + regex + '"\n"""\nHere will be the step-by-step explanation of what types of patterns the regex is searching for:\n1.'
    response = openai.Completion.create(engine="davinci-codex", prompt=incipit_explanation, max_tokens=512, temperature=0.15)

    answer = "1." + response['choices'][0].text.split('"""')[0]

    lines = answer.split("\n")

    answer_non_rep = ""
    previous = ""
    
    for line in lines:
        # Checking after the numerotation
        if line[2:] != previous[2:]:
            answer_non_rep += "\n" + line
            previous = line
        else:
            break

    explanation =  answer_non_rep
    
    return explanation

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        regex = request.form.get('regex')
        if  regex:
            explanation = fetch_explanation(regex, openai_key = app.config['OPENAI_KEY'])
            return render_template("index.html", regex=regex, explanation = explanation) 

        return render_template("index.html") 

    @app.route('/regex', methods=['POST'])
    def return_explanation():
        regex = request.form['regex']
        if  'regex':
            return fetch_explanation(regex)
        return 'Regex not found'


    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
