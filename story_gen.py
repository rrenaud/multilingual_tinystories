import random
import pickle
import google.generativeai as genai
import hashlib
import json
import threading
import os
import time


class StoryParams:
    def __init__(self, verb, noun, adjective, story_features):
        self.verb = verb
        self.noun = noun
        self.adjective = adjective

        self.story_features = story_features


class StoryParamsGenerator:
    def __init__(self, accepted_verbs, accepted_nouns, accepted_adjectives, story_features_list, story_features_cum_weights):
        self.accepted_verbs = accepted_verbs
        self.accepted_nouns = accepted_nouns
        self.accepted_adjectives = accepted_adjectives

        self.story_features_list = story_features_list
        self.story_features_cum_weights = story_features_cum_weights

    def generate(self) -> StoryParams:
        verb = random.choice(self.accepted_verbs)
        noun = random.choice(self.accepted_nouns)
        adjective = random.choice(self.accepted_adjectives)

        story_features = random.choices(self.story_features_list, cum_weights=self.story_features_cum_weights)[0]

        return StoryParams(verb, noun, adjective, story_features)
    

feature_translations = {'Dialogue': 'la historia debe contener al menos un diálogo',
                'Twist': 'a historia debe contener un giro en la trama',
                'Conflict': 'la historia debe contener un conflicto',
                'BadEnding': 'la historia debe tener un final malo',
                'Foreshadowing': 'la historia debe contener una premonición',
                'MoralValue': 'la historia debe contener un valor moral',
                }

def create_tiny_story_prompt(params: StoryParams):
    noun, verb, adjective = params.noun, params.verb, params.adjective

    story_features_combined = [feature_translations[f] for f in params.story_features]
    if len(story_features_combined) == 1:
        story_features_combined = story_features_combined[0]
    else:
        story_features_combined = ', '.join(story_features_combined[:-1]) + ' y ' + story_features_combined[-1]
    prompt_template = (
        """Escriba una historia corta (de 3 a 5 párrafos) """
        """que utilice únicamente palabras muy simples que un niño de 3 años probablemente entendería. """
        """En el cuento se debe utilizar el verbo “{verb}”, el sustantivo “{noun}” y el adjetivo “{adjective}”. """
        """La historia debe tener las siguientes características: {story_features_combined}. """
        """¡Recuerde usar solo palabras simples!""")
    prompt = prompt_template.format(**locals())
    return prompt

    
def generate_tiny_story(gen_model, params_generator: StoryParamsGenerator):
    params = params_generator.generate()
    prompt = create_tiny_story_prompt(params)    
    story = gen_model.generate_content(prompt)
    
    try:
        story_text = story.text
    except ValueError as e:
        print('Error:', e)
        return None
    json_struct = {'instruction': {
        'features': list(params.story_features), 
        'prompt': prompt,
        'words': [params.verb, params.noun, params.adjective]
        },
        'story': story_text,
        'source': 'gemini-1.5-flash'}
    return json_struct


def generate_and_log_tiny_stories(gen_model, params_generator: StoryParamsGenerator, num_stories: int, thread_id: int = 0):    
    for i in range(0, num_stories):
        try:
            story = generate_tiny_story(gen_model, params_generator)
            if story:
                md5 = hashlib.md5(story['story'].encode()).hexdigest()
                with open(f'spanish_stories/generated_story_{thread_id}_{i}_{md5}.json', 'w') as fp:
                    json.dump(story, fp)
            else:
                print('Error generating story', i)
        except Exception as e:
            print('Error generating story', i, e)
            print('sleeping for 10 seconds at index', i, 'on thread', thread_id)
            time.sleep(10)
        if i % 1000 == 0:
            print('At index', i, 'on thread', thread_id)



def main():
    GEMINI_API_KEY = open(os.path.expanduser('~/.gemini_api_key'), 'r').read().strip()
    genai.configure(api_key=GEMINI_API_KEY)
    safety_settings = [{'category': c, 'threshold': 'BLOCK_NONE'} for c in
                    ['HARM_CATEGORY_DANGEROUS', 'HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH',
                     'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT']]
    flash = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)

    story_params_generator = pickle.load(open('story_params_generator.pkl', 'rb'))
    threads = []
    NUM_DESIRED_STORIES = 2500000
    NUM_THREADS = 40
    for i in range(NUM_THREADS):
        thread = threading.Thread(target=generate_and_log_tiny_stories, args=(flash, story_params_generator, NUM_DESIRED_STORIES // NUM_THREADS, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()
    
