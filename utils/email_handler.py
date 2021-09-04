
'''
Email regex is resused from the
Almost perfect email regex: https://emailregex.com
'''
import re

email_regex = r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+' \
              r'(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|' \
              r'"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|' \
              r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")' \
              r'@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+' \
              r'[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|' \
              r'\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}' \
              r'(?:25[0-5]|2[0-4][0-9]|' \
              r'[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:' \
              r'(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|' \
              r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'

class EmailHandler:
    '''Matches email addresses in the text'''

    def __init__(self):
        self.pattern = re.compile(email_regex)

    def get_tok_indexlist(self, token_list):
        '''
        Given a list of text tokens, it returns a list with the the elements
        representing the starting point of a each token considering the spaces
        between the tokens
        eg: Input = ["ab","cd","ef"]
            Output = [0,3,6]
        '''
        tok_index = []
        for index, _ in enumerate(token_list):
            if index == 0:
                tok_index.extend([0])
            else:
                # +1 to consider space
                tok_index.extend([tok_index[-1]+len(token_list[index-1])+1])
        return tok_index

    def char_mapping(self, token_list):
        '''
        Given a list of text tokens,it returns a dictionary with
        a reference mapping of characters to tokens index
        eg: Input = ["ab","cd","ef"]
            Output = {0: 0, 1: 0, 3: 1, 4: 1, 6: 2, 7: 2}
        '''
        chars_to_tokens = {}
        token_index = self.get_tok_indexlist(token_list)
        for index, token in enumerate(token_list):
            for i in range(token_index[index], token_index[index]+len(token)):
                chars_to_tokens[i] = index
        return chars_to_tokens

    def find_email_regex(self, text):
        emails = list()
        matches = re.finditer(self.pattern, text.lower())
        for match in matches:
            emails.extend([(match.end()-1,
                            100,
                            match.start()-1,
                            match.group(0).strip())])
        return emails

    def return_email_index(self, matches, char_map, tags_list):
        '''
        Given the matched groups,token_list,token_tags,char_mapping, extract
        index of the tags_list to be qualified as MAIL for SPV
        '''
        words_include = []
        for match in matches:
            start = match[2]
            end = match[0]
            include = list(range(start, end, 1))
            words = list(
                set([value for key, value in char_map.items()
                     if key in include]))
            words_include.extend(words)
        existing_tags_index = [idx for idx, tag in
                               enumerate(tags_list) if tag != "O"]
        words_include_filtered = [i for i in words_include
                                  if i not in existing_tags_index]
        return words_include_filtered

    def match_ref(self, text, token_list, tags_list,
                  entity='MAIL', verbose=False):
        email_indices = []
        text = text.strip().lower()

        matches = self.find_email_regex(text)
        if len(matches) > 0:
            char_map = self.char_mapping(token_list)
            email_indices = self.return_email_index(matches, char_map, tags_list)
            if verbose and len(email_indices) > 0:  # pragma: no cover <--
                print(f'\nFinal Matches {entity}: '
                      f'{[token_list[idx] for idx in email_indices]}\n')
        return email_indices


if __name__ == '__main__':
    import spacy
    from pprint import pprint
    nlp = spacy.load('en_core_web_sm')

    test = "mailto: john.doe@gmail.com from: jane.doe@outlook.com"
    doc = nlp(test)
    toks = [t.text for t in doc]
    toks = [t.strip() for t in toks]
    text = " ".join(toks)
    tags = ['O']*len(doc)
    tag = "MAIL"
    email_hdlr = EmailHandler()
    email_indices = email_hdlr.match_ref(text, toks, tags,
                                         entity=tag,
                                         verbose=True)
    tags = [tag if idx in email_indices else 'O'
            for idx in range(len(toks))]
    print(text)
    print(toks)
    print(tags)
    pprint(list(zip(toks, tags)), compact=True)
