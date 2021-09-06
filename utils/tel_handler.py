import re
# import phonenumbers as pn


class TelHandler:
    '''Matches telephone numbers in the text'''

    def __init__(self):
        beg = r'(?:\s|^)('
        end = r')(?:\s|$)'
        start = r'^('
        eol = r')$'
        separator = r'(\s|-)'

        anchor = r'(telephone\s:\s|telephone\s:|telephone:\s|' + \
            r'telephone\s|telephone\.\s|telephone' + \
            r'|tel\s:\s|tel\s:|tel:\s|tel\s|tel\.\s|tel\+|tel' + \
            r'|phone\s:\s|phone\s:|phone:\s|phone\s|phone\.\s|phone' + \
            r'|cell\s:\s|cell\s:|cell:\s|cell\s|cell\.\s|cell' + \
            r'|direct\s:\s|direct\s:|direct:\s|direct\s|direct\.\s|direct' + \
            r'|mobile\s:\s|mobile\s:|mobile:\s|mobile\s|mobile\.\s|mobile' + \
            r'|number\s:\s|number\s:|number:\s|number\.\s' + \
            r'|fax\sto\s:\s|fax\sto:\s|fax\s:\s|fax\s:|' + \
            r'fax:\s|fax\s|fax\.\s|fax\+|fax' + \
            r'|facsimile\s:\s|facsimile\s:|facsimile:\s|' +\
            r'facsimile\s|facsimile\.\s|facsimile' + \
            r'|f\s:\s|f\s:|f:\s|f\s|f\.\s|f' + \
            r'|t\s:\s|t\s:|t:\s|t\s|t\.\s|t)'

        country_code = r'\+?(9[976]\d|8[987530]\d|6[987]\d|5[90]\d|42\d|' \
            r'3[875]\d|2[98654321]\d|9[8543210]|8[6421]|' \
            r'6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)'

        generic_pattern = beg + anchor + \
            r'(?:(?:\+?([1-9]|[0-9]|[0-9][0-9])\s' \
            r'(?:[.-]\s)?)?(?:(\s([2-9]1[02-9]|[02-8]1|[02-8][02-9])\s)' \
            r'|([1-9]|[0-9]1[02-9]|[02-8]1|[02-8][02-9]))\s(?:[.-]\s)?)?' \
            r'([2-9]1[02-9]|[02-9]1|[02-9]{2})\s(?:[.-]\s)?([0-9]{4})' \
            r'(?:\s(?:#|x.?|ext.?|extension)\s(\d+))?' + end

        generic_pattern_2 = beg + anchor + country_code + \
            separator + r'\d{2,4}' + \
            separator + r'\d{2,4}' + \
            separator + r'\d{2,4}' + end

        generic_pattern_3 = beg + anchor + country_code + \
            separator + r'\d{4,6}' + \
            separator + r'\d{4,6}' + end

        # generic pattern for international numbers
        # country codes folowed by 1-14 digits
        generic_pattern_4 = beg + anchor + country_code + \
            separator + r'\d{5,14}' + end

        generic_pattern_5 = beg + anchor + country_code + \
            separator + r'\d{2}' + \
            separator + r'\d{7}' + end

        generic_pattern_6 = start + country_code + \
            separator + r'\d{2,4}' + \
            separator + r'\d{2,4}' + \
            separator + r'\d{2,4}' + eol

        generic_pattern_7 = start + country_code + \
            separator + r'\d{4,6}' + \
            separator + r'\d{4,6}' + eol

        generic_pattern_8 = start + country_code + \
            separator + r'\d{2}' + \
            separator + r'\d{7}' + eol

        generic_pattern_9 = start + country_code + \
            separator + r'\d{5,14}' + eol

        brazil_pattern = beg + anchor + r'(\()?\s*(\d{2})\s*(\s |\))*' + \
            r'(9?\d{4})(\s|-)?(\d{4})($|\n)' + end

        canada_pattern = beg + anchor + r'(?:(?:\+?1\s*(?:[.-]\s*)?)?' + \
            r'(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|' + \
            r'([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))' + \
            r'\s*(?:[.-]\s*)?)?' + \
            r'([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*' + \
            r'(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)' + \
            r'\s*(\d+))?' + end

        china_pattern_1 = beg + anchor + \
            r'(13[0-9] | 14[57] | 15[012356789] ' + \
            r'| 17[0678] | 18[0-9])[0-9]{8}' + end

        china_pattern_2 = beg + anchor + \
            r'1[34578][012356789]\d{8} | 134[012345678]\d{7}' + \
            end

        germany_pattern = beg + anchor + r'([\+][0-9]{1, 3}[.\-])?' + \
            r'([\(]{1}[0-9]{1, 6}[\)])?' + \
            r'([0-9 \.\-\/ ]{3, 20})((x|ext|extension)[]?[0-9]{1, 4})?' + \
            end

        india_pattern = beg + anchor + \
            r'((\+*)((0[-]+)*|(91)*)(\d{12}|\d{10})) ' + \
            r'|\d{5}([-]*)\d{6}' + end

        indonesia_pattern = beg + anchor + \
            r'\(?(?: \+62 | 62 | 0)(?: \d{2, 3})?\)?' + \
            r'[.-]?\d{2, 4}[.-]?\d{2, 4}[.-]?\d{2, 4}' + \
            end

        japan_pattern = beg + anchor + \
            r'(?:\d{10}|\d{3}-\d{3}-\d{4}|\d{2}-\d{4}-\d{4}|' + \
            r'\d{3}-\d{4}-\d{4})' + end

        russia_pattern = beg + anchor + r'((\+7 | 7 | 8)+([0-9]){10})' + \
            end

        us_pattern = beg + anchor + r'1?\W*([2-9][0-8][0-9])\W*' + \
            r'([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?' + \
            end

        uk_pattern = beg + anchor + \
            r'(?:(?:\(?(?:0(?:0|11)\)?[\s-]?\(?|\+)44\)?[\s-]?' + \
            r'(?:\(?0\)?[\s-]?)?)|(?:\(?0))(?:(?:\d{5}\)?[\s-]?\d{4,5})|' + \
            r'(?:\d{4}\)?[\s-]?(?:\d{5}|\d{3}[\s-]?\d{3}))|' + \
            r'(?:\d{3}\)?[\s-]?\d{3}[\s-]?\d{3,4})|(?:\d{2}\)?' + \
            r'[\s-]?\d{4}[\s-]?\d{4}))(?:[\s-]?' + \
            r'(?:x|ext\.?|\#)\d{3,4})?' + end

        patterns = [generic_pattern, generic_pattern_2, generic_pattern_3,
                    generic_pattern_4, generic_pattern_5, generic_pattern_6,
                    generic_pattern_7, generic_pattern_8, generic_pattern_9,
                    brazil_pattern, canada_pattern,
                    china_pattern_1, china_pattern_2, germany_pattern,
                    india_pattern, indonesia_pattern, japan_pattern,
                    russia_pattern, us_pattern, uk_pattern]

        self.patterns = [re.compile(p) for p in patterns]

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

    def find_tel_regex(self, text):
        tels = list()
        for _, pattern in enumerate(self.patterns):
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                tels.extend([(match.start(),
                              match.end()-1,
                              match.group(0).strip())])
        return tels

    def return_tel_index(self, matches, char_map, tags_list):
        '''
        Given the matched groups,token_list,token_tags,char_mapping, extract
        index of the tags_list to be qualified as MAIL for SPV
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

    def match_ref(self, text, token_list, tags_list, entity='', verbose=False):
        tel_indices = []
        text = text.strip().lower()

        matches = self.find_tel_regex(text)
        if len(matches) > 0:
            char_map = self.char_mapping(token_list)
            tel_indices = self.return_tel_index(matches, char_map, tags_list)
            tel_indices = sorted(list(set(tel_indices)))
            if verbose and len(tel_indices) > 0:  # pragma: no cover <--
                print(f'\nFinal Matches {entity}: '
                      f'{[token_list[idx] for idx in tel_indices]}\n')
        return tel_indices


if __name__ == '__main__':
    import spacy
    from pprint import pprint
    nlp = spacy.load('en_core_web_sm')

    test = "COMPANY REGISTRATION NUMBER 273 7924"
    doc = nlp(test)
    toks = [t.text for t in doc]
    toks = [t.strip() for t in toks]
    text = " ".join(toks)
    tags = ['O']*len(doc)
    tag = "TEL"
    tel_hdlr = TelHandler()
    tel_indices = tel_hdlr.match_ref(text, toks, tags,
                                     entity=tag,
                                     verbose=True)
    tags = [tag if idx in tel_indices else 'O'
            for idx in range(len(toks))]
    print(text)
    print(toks)
    print(tags)
    pprint(list(zip(toks, tags)), compact=True)
