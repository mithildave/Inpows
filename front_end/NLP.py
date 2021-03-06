#################################################################
# NLP class definition
# Include tokens, dependency edges and parsing processes.
#################################################################


from stanfordnlp.server import CoreNLPClient
import os

import Inpows.tools.Log as log

import re
from Inpows.tools.root_directory import root_dir
from Inpows.tools.system_operations import check_sys_proc_exists_by_name

# annotator_list = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse']
# client = CoreNLPClient(annotators=annotator_list, timeout=60000, memory='8G')

class RootToken:
    def __init__(self):
        self.word = 'root'
        self.pos = ''
        self.ner = ''
        self.lemma = ''


class RootEdge:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.dep = 'root'



class Token:
    def __init__(self, token):
        self.word = token.word
        self.pos = token.pos
        self.ner = token.ner
        self.lemma = token.lemma
        self.dep = []
        self.mapping = []
        self.mapping_vote = []
        self.modifiers = []
        self.final_mapping = None


class Dependency:
    def __init__(self, edge):
        self.source = edge.source - 1
        self.target = edge.target - 1
        self.dep = edge.dep
        self.paths = []
        self.prep_mapping = []
        self.api_paths = []


class NLParsing:
    def __init__(self):
        self.text = ''
        self.annotate = ''
        self.sentence = ''
        self.token = []
        self.dependency = []
        self.root = None
        self.modifier_group = []
        self.start_server = self.check_nlp_server()
        self.replaced_tokens = []
        self.replaced_tokens_concept = []
        self.replaced_tokens_condition = []

    def check_nlp_server(self):
        log.log('Check NLP server status...')
        if check_sys_proc_exists_by_name('edu.stanford.nlp.pipeline.StanfordCoreNLPServer'):
            log.log('NLP server already started!')
            return False
        else:
            log.log('NLP server is not started, a temporary server will created and closed after synthesis.\n '
                   'If you prefer using faster NLP service, please follow the instructions in the\n'
                    '\tthird_party_pkgs\n'
                   'folder and start NLP service via following bash commands:\n'
                   '\tsh start_nlp_server.sh')
            return True


    def preprocessing(self,text, domain):
        if domain == 'Flight':
            text = text.replace('one way ','').replace('washington dc', 'washington').replace('san francisco', 'francisco').replace('san jose', 'jose').replace('fort worth', 'worth').replace('worth texas', 'worth').replace('california', '').replace('pennsylvania', '').replace('colorado', '').replace('georgia', '').replace('o clock', '').replace('am', 'AM').replace('AMerican airline', 'american airline')
        elif domain == 'ASTMatcher':
            text = text.replace('for statement', 'forstatement')
        elif domain == 'scikit-learn':
            variable_regex = r'(<[^>]+>)'
            variable_count = 0;
            match = re.search(variable_regex, text)
            while match:
                self.replaced_tokens.append(text[match.start()+1: match.end()-1])
                text = text.replace(match.group(), 'var' + str(variable_count), 1)
                variable_count += 1
                match = re.search(variable_regex, text)
                
        elif domain == 'HPC-FAIR':
            variable_regex = r'(\"[^\"]+\")'
            variable_count = 0;
            match = re.search(variable_regex, text)
            while match:
                self.replaced_tokens.append(text[match.start()+1: match.end()-1])
                text = text.replace(match.group(), 'string' + str(variable_count), 1)
                variable_count += 1
                match = re.search(variable_regex, text)

            #condition_regex = r'(<.+>)'
            stack = []
            conditions = []
            cond = ""
            for ch in text:
                if ch == '<':
                    if not stack:
                        cond = ""
                    else:
                        cond += ch
                    stack.append(ch)
                elif ch == '>':
                    stack.pop()
                    if not stack:
                        conditions.append(cond)
                        cond = ""
                    else:
                        cond += ch
                else:
                    cond += ch

            condition_count = 0;

            for each in conditions:
                self.replaced_tokens_condition.append(each)
                text = text.replace('<'+each+'>', 'condition' + str(condition_count), 1)
                condition_count += 1

            concept_regex = r'(\{[^\}]+\})'
            concept_count = 0;
            match = re.search(concept_regex, text)
            while match:
                elf.replaced_tokens_concept.append(text[match.start() + 1: match.end() - 1])
                text = text.replace(match.group(), 'concept' + str(concept_count), 1)
                concept_count += 1
                match = re.search(concept_regex, text)

            # -----> END CHANGE

        log.lprint('test: ', text)
        city = ["washington", "atlanta", "philadelphia", "dallas", "francisco", "boston", "baltimore", "denver",
                "worth", "pittsburgh", "detroit",
                "westchester", "oakland", "stapleton", "tacoma", "jose"]
        for i in city:
            while i in text:
                index = text.find(i)
                text = text[0].capitalize() + text[1:index] + text[index].capitalize() + text[index+1:]
        return text.replace('\n', '')



    def parsing(self, text, domain):
        self.text = self.preprocessing(text, domain)
        log.log('Start parsing sentence: ' + self.text)
        self.stanford_parsing()
        self.domain_annotator(domain)
        self.set_local()

    def set_local(self):
        for t in self.sentence.token:
            self.token.append(Token(t))
        for e in self.sentence.enhancedPlusPlusDependencies.edge:
            tmp = Dependency(e)
            self.dependency.append(tmp)
            self.token[tmp.source].dep.append(tmp)
        self.root = self.sentence.enhancedPlusPlusDependencies.root[0]-1

    def stanford_parsing(self):
        log.log('starting JAVA Stanford CoreNLP Server...')
        # setting nlp configurations
        # %env CORENLP_HOME=/Users/zifannan/Documents/code/java/stanford-corenlp-full-2018-10-05

        annotator_list = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse']
        client = CoreNLPClient(start_server=self.start_server, annotators=annotator_list, timeout=60000, memory='8G')
        self.annotate = client.annotate(self.text)
        client.stop()
        self.sentence = self.annotate.sentence[0]
        # self.dependency = self.sentence.enhancedPlusPlusDependencies

    def domain_annotator(self, domain):
        if domain == 'Flight':
            weekday = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            airlines = ['continental', 'american', 'american', 'twa', 'united', 'delta', 'eastern', 'us']
            seat_class = ['coach', 'first', 'economy']
            city = ["washington", "atlanta","philadelphia","dallas","francisco","boston","baltimore","denver","worth","pittsburgh","detroit",
                    "westchester","oakland","stapleton","tacoma","jose"]
            month = ["september","august","november","june","july","october","april","may"]
            aircraft = ["819","727","320","813","2153","dc10","296","747","825","269","1039","257","315","459","jet"]
            daynum = ["first","twentieth","nineteenth","seventeenth","ninth","third","fourteenth","seventh",
                      "fifteenth","thirtieth","fourth","fifth","eighth","twelfth","sixteenth","second","tenth","eleventh"]
            time = ["evening","8","morning","10am","10","noontime","day","9","225pm","afternoon","230","324pm","110pm",
                    "12","5","645am","755am","755","9pm","8am","815am","1pm","420","615pm","night","630am","650","555","6pm","nighttime","tomorrow","7pm","today","2pm"]

            for t in range(len(self.sentence.token)):
                # log.test(self.sentence.token[t].word)
                if self.sentence.token[t].word in weekday:
                    self.sentence.token[t].ner = 'WEEKDAY'
                elif self.sentence.token[t].word in airlines:
                    self.sentence.token[t].ner = 'AIRLINES'
                elif self.sentence.token[t].word in seat_class:
                    self.sentence.token[t].ner = 'CLASS'
                elif self.sentence.token[t].word.lower() in city:
                    self.sentence.token[t].ner = 'CITY'
                elif self.sentence.token[t].word in month:
                    self.sentence.token[t].ner = 'MONTH'
                elif self.sentence.token[t].word in aircraft:
                    self.sentence.token[t].ner = 'AIRCRAFT'
                elif self.sentence.token[t].word in daynum:
                    self.sentence.token[t].ner = 'DAYNUM'
                elif self.sentence.token[t].word in time:
                    self.sentence.token[t].ner = 'TIME'

        elif domain == 'TextEditing':
            string = ['colon', 'space', 'dollar', 'name']
            integer = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th' '13th', '80th', '1', '2', '3', '4',
                       '5', '6', '7', '8', '9', '10', '14','52']
            general_ordi = ['first']

            for t in range(len(self.sentence.token)):
                if self.sentence.token[t].word in string:
                    self.sentence.token[t].ner = 'STRING'
                elif self.sentence.token[t].word in integer:
                    self.sentence.token[t].ner = 'INTEGER'
                elif self.sentence.token[t].word in general_ordi:
                    self.sentence.token[t].ner = 'GENERAL'

        elif domain == 'ASTMatcher':
            string = ['pi', '*']
            unary = []

            for t in range(len(self.sentence.token)):
                if self.sentence.token[t].word in string:
                    self.sentence.token[t].ner = 'STRING'
                elif self.sentence.token[t].word in unary:
                    self.sentence.token[t].ner = 'UNARY'
        elif domain == 'scikit-learn':
            variable_regex = r'(<.+>)'
            int_regex = r'\d+'
            int_ordinal_regex = r'\d+\w\w'
            float_regex = r'\d*\.\d+'
            for t in range(len(self.sentence.token)):
                # <---- START CHANGE
                if re.match(variable_regex, self.sentence.token[t].word):
                    self.sentence.token[t].ner = 'var'
                # ----> END CHANGE
                elif re.match(int_regex, self.sentence.token[t].word):
                    self.sentence.token[t].ner = 'int'
                elif re.match(int_regex, self.sentence.token[t].word):
                    self.sentence.token[t].ner = 'int'
                elif re.match(int_ordinal_regex, self.sentence.token[t].word):
                    self.sentence.token[t].ner = 'int'
                    stripped_int_regex = r'\d+'
                    self.sentence.token[t].word = re.match(stripped_int_regex, self.sentence.token[t].word).group(0)
                    self.sentence.token[t].lemma = re.match(stripped_int_regex, self.sentence.token[t].word).group(0)
                elif re.match(float_regex, self.sentence.token[t].word):
                    self.sentence.token[t].ner = 'float'


        elif domain == 'HPC-FAIR':
            variable_regex = r'(".+")'
            condition_regex = r'(<.+>)'
            concept_regex = r'(\{.+\})'
            for t in range(len(self.sentence.token)):
                if re.match(variable_regex, self.sentence.token[t].word):
                    self.sentence.token[t].ner = 'string'
                elif re.match(condition_regex, self.sentence.token[t].word):
                    self.sentence.token[t].ner = 'condition'
                elif re.match(concept_regex, self.sentence.token[t].word):
                    self.sentence.token[t].ner = 'hpc_concept'

            # concept_regex = r'(\{.+\})'
            # for t in range(len(self.sentence.token)):
            #     if re.match(concept_regex, self.sentence.token[t].word):
            #         self.sentence.token[t].ner = 'concept'

    def displayNode(self, index, n):
        log.lprint('---' * n + '| ', self.token[index].word, '[' + self.token[index].pos + '], [', self.token[index].ner + '], [', self.token[index].lemma, ']')
        for e in self.token[index].dep:
            self.displayNode(e.target, n+1)

    def displayByNode(self, n):
        self.displayNode(self.root, n)
        # for e in self.token[self.root].dep:
        #     self.displayNode(e.target, n+1)


    def displayByEdge(self):
        log.lprint('---------------- Dependency graph -----------------')
        for e in self.dependency:
            log.lprint(self.token[e.source].word,
                  '[' + self.token[e.source].pos + ']',
                  '[' + self.token[e.source].ner + ']',
                  '[' + self.token[e.source].lemma + ']',
                  self.token[e.source].mapping,
                  '--' + e.dep + '-->',
                  self.token[e.target].word,
                  '[' + self.token[e.target].pos + ']',
                  '[' + self.token[e.target].ner + ']',
                  '[' + self.token[e.target].lemma + ']',
                  self.token[e.target].mapping,
                  '====>>',
                  e.api_paths, e.prep_mapping)
            log.lprint('')
        log.lprint('--------------------------------------------------')

    def displayByEdgeFile(self, write_file):
        log.fprint(write_file, '---------------- Dependency graph -----------------')
        for e in self.dependency:
            log.fprint(write_file, self.token[e.source].word,
                  '[' + self.token[e.source].pos + ']',
                  '[' + self.token[e.source].ner + ']',
                  '[' + self.token[e.source].lemma + ']',
                  self.token[e.source].mapping,
                  '--' + e.dep + '-->',
                  self.token[e.target].word,
                  '[' + self.token[e.target].pos + ']',
                  '[' + self.token[e.target].ner + ']',
                  '[' + self.token[e.target].lemma + ']',
                  self.token[e.target].mapping,
                  '====>>',
                  e.api_paths, e.prep_mapping)
            log.fprint(write_file, '')
        log.fprint(write_file, '--------------------------------------------------')

    def display_stanfordnlp_result(self):
        for e in self.sentence.enhancedPlusPlusDependencies.edge:
            log.lprint(self.sentence.token[e.source - 1].word,
                  '[' + self.sentence.token[e.source - 1].pos + ']',
                  '[' + self.sentence.token[e.source - 1].coarseNER + ',' + self.sentence.token[
                      e.source - 1].fineGrainedNER + ']',
                  '[' + self.sentence.token[e.source - 1].lemma + ']',
                  '--' + e.dep + '-->',
                  self.sentence.token[e.target - 1].word,
                  '[' + self.sentence.token[e.target - 1].pos + ']',
                  '[' + self.sentence.token[e.target - 1].coarseNER + ',' + self.sentence.token[
                      e.target - 1].fineGrainedNER + ']',
                  '[' + self.sentence.token[e.target - 1].lemma + ']')
