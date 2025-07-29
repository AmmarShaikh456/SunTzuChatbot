from call_gpt import predicate_gen, sentence_diversity, sentence_gen
from reasoner import reasoner
from filter import get_predicates, filter

import time

paths = ['data/info_list.pl', 'data/state.pl', 'data/knowledge.pl', 'src/functions.pl', 'src/results.pl', 'src/query.pl']

attrs, values = get_predicates()

session_continues = True
mode = 'recommend'
reply = 'Hello what can I do for you?'
end_time = 0
start_time = 0
total = 0
#while(session_continues):
for i in range(10):

    reply = sentence_diversity(reply).strip()
    total_time = end_time - start_time
    print("Execution time:", total_time, "seconds")
    print('\nSun Tzu:\n' + reply + '\n\nYou: ')
    total += total_time
    r = reasoner(paths)
    query = 'What is the best strategy for overcoming obstacles in business?'
    start_time = time.time()
    if query == 'end':
        session_continues = False
        continue

    if mode == 'ask':
        query = reply + query
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
total /= 10
print('Average execution time: ', total, ' seconds')
