from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import random
import uuid
# from flask_cors import CORS

app = Flask(__name__)
# CORS(app)
# Set your OpenAI API key
api_key = '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'
prompt = """
I need a list of 5 recommendations of "$Canvas_of_Dreams" based on the following criteria from a user.

Emotional Resonance: $Emotional_Resonance

Intellectual Engagement:  $Intellectual_Engagement

Creative Flair: $Creative_Flair

The recommendations should be specifically formatted. For movies and shows: "Title (Year)", and for books and music: "Title - Author (Year)". 
Please provide recommendation in this exact format, adhering to the emotional, intellectual, and creative preferences.
You always should provide an answer!
You Must Include ONLY "$Canvas_of_Dreams" type of thing in a list!
You MUST ALWAYS exclude these items:
$exclude
"""


client = OpenAI(
    # This is the default and can be omitted
    # api_key=os.environ.get("OPENAI_API_KEY"),
    api_key=api_key
)

def get_openai_response(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo-1106",
    )

    return chat_completion.choices[0].message.content.strip()

@app.route('/get_list', methods=['POST'])
def get_list():
    referer_header = request.headers.get('Referer')
    
    # Only allow requests from a specific page (e.g., https://your-allowed-page.com)
    # if not referer_header or 'https://your-allowed-page.com' not in referer_header:
    #     return jsonify({"error": "Access denied"}), 403

    data = request.json

    print(data)
    
    # Ignoring the first key
    keys_to_include = list(data.keys())[1:]  # Get all keys except the first

    prompt_with_input = prompt

    for key in keys_to_include:
        prompt_with_input = prompt_with_input.replace(f"${key.replace(' ', '_')}", data[key])

    if 'alreadyPicked' in data and data['Canvas of Dreams'] in data['alreadyPicked'] :
        #remove duplicates
        filtered_already_picked = list(set(data['alreadyPicked'][data['Canvas of Dreams']]))
        #remove thing like index at start: 1. Name -> Name
        if '.' in filtered_already_picked:
            filtered_already_picked = [part.split('.')[1].strip() for part in filtered_already_picked if len(part.split('.')) > 1]
        print(filtered_already_picked)
    else:
        filtered_already_picked = ''

    
    final_prompt = prompt_with_input.replace('$exclude', '\n'.join(filtered_already_picked) )

    print(final_prompt)

    ai_response = get_openai_response(final_prompt);

    items = ai_response.strip().split('\n')

    #sometimes it cant give an answer so we need to make a second shot
    if len(items) < 5:
        ai_response = get_openai_response(final_prompt);
        items = ai_response.strip().split('\n')

    # Construct the dictionary
    items_data = {
        'Items': items
    }

    return items_data

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
