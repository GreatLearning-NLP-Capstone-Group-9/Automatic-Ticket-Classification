import re


class LinkHandler:
    '''Matches any website links in the text'''

    def __init__(self):

        http_protocol = r"""h[it]tps?:"""
        # generic_protocol = r"""[a-z][\w-]+"""
        top_level_domain = r"""(?:com|net|org|edu|gov|mil|aero|asia|biz|""" + \
            r"""cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|""" + \
            r"""travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|""" + \
            r"""au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|""" + \
            r"""bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|""" + \
            r"""cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|""" + \
            r"""es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|""" + \
            r"""gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|""" + \
            r"""il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|""" + \
            r"""kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|""" + \
            r"""md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|""" + \
            r"""my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|""" + \
            r"""pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|""" + \
            r"""sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|""" + \
            r"""sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|""" + \
            r"""tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|""" + \
            r"""ye|yt|yu|za|zm|zw)"""

        pattern = r"""(?i)\b((?:""" + http_protocol + \
            r"""(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.]""" + \
            top_level_domain + \
            r"""/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)""" + \
            r"""[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)""" + \
            r"""[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])""" + \
            r"""|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.]""" + \
            top_level_domain + \
            r"""\b/?(?!@)))"""
        self.pattern = re.compile(pattern)

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

    def find_link_regex(self, text):
        links = list()
        matches = re.finditer(self.pattern, text.lower())
        for match in matches:
            links.extend([(match.start()-1,
                           match.end()-1,
                           match.group(0).strip())])
        return links

    def return_link_index(self, matches, char_map, tags_list):
        '''
        Given the matched groups,token_list,token_tags,char_mapping, extract
        index of the tags_list to be qualified as LINK for SPV
        '''
        words_include = []
        for match in matches:
            start = match[0]
            end = match[1]
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
                  entity='LINK', verbose=False):
        link_indices = []
        text = text.strip().lower()

        matches = self.find_link_regex(text)
        if len(matches) > 0:
            char_map = self.char_mapping(token_list)
            match_indices = self.return_link_index(matches,
                                                   char_map,
                                                   tags_list)

            if len(match_indices) > 0:
                for idx in match_indices:
                    tok = token_list[idx]
                    alpha_tok = re.sub('[^a-zA-Z]', '', tok)
                    if len(alpha_tok) < 6:
                        continue
                    if alpha_tok.islower() or alpha_tok.isupper():
                        link_indices.append(idx)

            if verbose and len(link_indices) > 0:  # pragma: no cover <--
                print(f'\nFinal Matches {entity}: '
                      f'{[token_list[idx] for idx in link_indices]}\n')
        return link_indices


if __name__ == '__main__':
    import spacy
    from pprint import pprint
    nlp = spacy.load('en_core_web_sm')

    test = "www.google.com/?search Search Results: ..."
    doc = nlp(test)
    toks = [t.text for t in doc]
    toks = [t.strip() for t in toks]
    text = " ".join(toks)
    tags = ['O']*len(doc)
    tag = "LINK"
    link_hdlr = LinkHandler()
    link_indices = link_hdlr.match_ref(text, toks, tags,
                                       entity=tag,
                                       verbose=True)
    tags = [tag if idx in link_indices else 'O'
            for idx in range(len(toks))]
    print(text)
    print(toks)
    print(tags)
    pprint(list(zip(toks, tags)), compact=True)
