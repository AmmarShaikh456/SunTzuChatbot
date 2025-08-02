from call_gpt import predicate_gen, sentence_diversity, sentence_gen
from reasoner import reasoner
from filter import get_predicates, filter



import time

paths = [
    'data/info_list.pl',
    'data/state.pl',
    'data/knowledge.pl',
    'src/functions.pl',
    'src/update.pl',
    'src/preference.pl',
    'src/extra_preference.pl',
    'src/results.pl',
    'data/log.pl',
    'src/query.pl'
]
attrs, values = get_predicates()
r = reasoner(paths)
mode = 'recommend'
reply = 'Hello what can I do for you?'
total = 0
num_runs = 10
for i in range(num_runs):
    print('\nSun Tzu:\n' + reply + '\n\nYou: ')
    query = 'What is the best strategy for overcoming obstacles in business?'
    if mode == 'ask':
        query = reply + query
    start_time = time.time()
    query_predicates = predicate_gen(query).strip()
    query_predicates = filter(query_predicates, attrs, values)
    if query_predicates == 'irrelevant.':
        reply = 'This question is beyond my strategic wisdom. Please ask about leadership, business, or strategy.'
    elif query_predicates == 'thank.':
        reply = 'Gratitude is the mark of a wise leader.'
    else:
        reply_predicates = r.reason(query_predicates)
        if reply_predicates == {}:
            reply = 'The situation yields no clear wisdom. No advice emerges for your requirement.'
        elif not reply_predicates:
            reply = 'Your question is unclear. Please clarify your intent, for clarity is the foundation of strategy.'
        else:
            mode = reply_predicates['Mode']
            if mode == 'ask':
                reply = 'Do you have any preference for the ' + reply_predicates['Output'] + ' in your situation?'
            if mode == 'recommend':
                reply = sentence_gen(reply_predicates['Output'][1:-1]).strip()
    end_time = time.time()
    total_time = end_time - start_time
    print("Execution time:", total_time, "seconds")
    total += total_time
avg = total / num_runs
print('Average execution time: ', avg, ' seconds')
