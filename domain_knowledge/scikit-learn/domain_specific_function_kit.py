import Inpows.tools.Log as log
import Inpows.back_end.back_end_function_kit as fc
import re


# domain specific knowledge for flight domain
def parsing_rules(nlp, gg):
    variable_sub = r'(var\d+)'
    for dep in nlp.dependency:
        if nlp.token[dep.target].lemma == 'without':
            dep.dep = 'nmod:without'
        elif re.match(variable_sub, nlp.token[dep.target].lemma):
            dep.dep = 'keep'
            nlp.token[dep.target].ner = 'python_var'
            replace_index = int(re.findall(r'(\d+)', nlp.token[dep.target].lemma)[0])
            nlp.token[dep.target].lemma = nlp.replaced_tokens[replace_index]
            nlp.token[dep.target].word = nlp.replaced_tokens[replace_index]

def special_mapping_rules(nlp):
    for token in nlp.token:
        if token.ner == 'python_var':
            # token.mapping.append('')
            pass
    

def special_cases_treatment(nlp, gg, text_index):
    pass
