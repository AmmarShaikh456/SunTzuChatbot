
from colorama import Fore, Style
import os
import sys
from call_gpt import predicate_gen, sentence_diversity, sentence_gen, chat, query_confirm, change_mind_confirm, irrelevant_reply
import random
from reasoner import reasoner
from filter import get_predicates, filter


# Check for OpenAI API key before starting session
api_key = os.getenv("OPENAI_API_KEY")
# if not api_key or not api_key.strip().startswith("sk-"):
#     print(Fore.YELLOW + "Sun Tzu:" + Style.RESET_ALL)
#     print("\nYour strategy is incomplete. The OpenAI API key is missing or invalid.\nSet your key with:\n\n    $env:OPENAI_API_KEY='sk-...yourkey...'\n\nThen run: python main.py\n\nOnly with proper preparation can wisdom be revealed.")
#     sys.exit(1)

paths = ['data/info_list.pl', 'data/state.pl', 'data/knowledge.pl', 'src/functions.pl', 'src/update.pl', 'src/preference.pl', 'src/extra_preference.pl', 'src/results.pl', 'data/log.pl', 'src/query.pl']

attrs, values = get_predicates()
r = reasoner(paths)

session_continues = True
mode = 'recommend'
confirm = ''
# Sun Tzu-style opening prompt (always greets as Sun Tzu, not a proverb)
reply = 'Greetings, seeker of wisdom. I am Sun Tzu. How may I guide you?'

# Track if this is the first turn
first_turn = True

# Sun Tzu-style prompt options for continuing the conversation
sun_tzu_prompts = [
    "Upon which battlefield of thought shall we engage next?",
    "What challenge or question weighs upon your mind?",
    "Where shall we direct our wisdom and strategy now?",
    "What matter requires the counsel of Sun Tzu?",
    "Which path of strategy do you wish to explore?",
    "What obstacle stands before you, awaiting guidance?",
    "How may I assist you in your pursuit of victory?",
    "What wisdom do you seek in the art of war and life?",
    "What dilemma calls for a strategist’s insight?",
    "What is your next question, seeker of wisdom?"
]

while(session_continues):
    # Only apply sentence_diversity after the first turn
    if not first_turn:
        reply = sentence_diversity(reply).strip()
    print('\n' + Fore.RED + 'Sun Tzu:' + Style.RESET_ALL)
    if confirm:
        print(confirm + ' ' + reply + Fore.CYAN + '\n\nYou: ' + Style.RESET_ALL)
        confirm = ''
    else:
        print(reply + Fore.CYAN + '\n\nYou: ' + Style.RESET_ALL)
    # After first print, set first_turn to False
    first_turn = False
    query = input()

    if mode == 'ask':
        query = '[begin context] ' + reply + ' [end context] ' + query
    query_predicates = predicate_gen(query).strip()
    print(Fore.GREEN + '\n[extracted semantics] ' + Style.RESET_ALL + query_predicates)

    query_predicates = filter(query_predicates, attrs, values)
    # End session if user says quit, thank you, end, or stop
    if query_predicates == 'quit.' or any(word in query.lower() for word in ['thank', 'thanks', 'end', 'stop', 'bye', 'farewell']):
        session_continues = False
        print('\n' + Fore.RED + 'Sun Tzu:' + Style.RESET_ALL + '\n' + 'Your gratitude is received. May your path be clear and your actions decisive. Farewell, seeker of wisdom.')
        continue

    if query_predicates == 'irrelevant.':
        irr_reply = irrelevant_reply(query)
        # Use a random Sun Tzu prompt for continued engagement
        next_prompt = random.choice(sun_tzu_prompts)
        if mode == 'ask':
            reply = irr_reply + ' ' + reply
        else:
            reply = irr_reply + ' ' + next_prompt
    else:
        reply_predicates = r.reason(query_predicates)
        if not reply_predicates:
            reply = 'Your question is unclear. Please clarify your intent, for clarity is the foundation of strategy.'
        elif type(reply_predicates) == dict and 'Success' in reply_predicates:
            reply = 'The situation yields no clear wisdom. Success is found, but no advice emerges for ' + reply_predicates['Fail'] + '.'
            mode = 'recommend'
        else:
            confirm = query_confirm(query_predicates)
            mode = reply_predicates['Mode']
            if mode == 'change':
                mode = 'ask'
                print(Fore.GREEN + '\n[preference confirming] ' + Style.RESET_ALL + reply_predicates['Output'])
                reply = change_mind_confirm(reply_predicates['Output'])
            elif mode == 'ask':
                reply = 'Do you seek generational wisdom for ' + reply_predicates['Output'] + ' or another topic/category?'
            elif mode == 'recommend':
                reply = sentence_gen(reply_predicates['Output'][1:-1]).strip() + ' Do you like it?'
            elif mode == 'quit':
                session_continues = False
                response = chat(query + ' Please quit.')
                print(Fore.RED + 'Sun Tzu:' + Style.RESET_ALL + '\n' + response)
                continue