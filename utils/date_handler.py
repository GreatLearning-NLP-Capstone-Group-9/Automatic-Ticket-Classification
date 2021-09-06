import re
from pathlib import Path

exceptions = {}

class DateHandler:
    def __init__(self):
        self.patterns = []
        short = 'jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|0ct|n0v'
        long = 'january|february|march|april|may|june|july|august|september' \
               '|october|november|december|janijary'
        mons = '(0?[1-9]|1[0-2])'
        months = f'({long}|{short})'
        all_months = f'({months}|{mons})'
        days = '([12][o0-9]|3[o01]|[o0]?[1-9])'
        superscripts = '(st|nd|rd|th|tm)'
        years = '(0[1-9]|[1-9][0-9]|19[0-9][0-9]|20[0-9][0-9])'
        years4 = '(19[0-9][0-9]|20[0-9][0-9])'
        hour_zone = r'(([0-1][0-9]|2[0-3])\s?:\s?([0-5][0-9]))?'
        time_zone = '(cest|cet|gmt)?'
        beg = r'(?:\s|^)('
        end = r')(?:\s|$)'
        whitespace = r'\s?'
        sep = r'\s?[\s\.,/-]\s?'
        dash = r'(/|-)'

        # (d[d] [of] mon[a-z] yy[yy]) (d[d] - mon[a-z] - yy[yy])
        # (d[d] , mon[a-z] , yy[yy])
        patterns = [beg + days + whitespace + superscripts +
                    r'?\s?(-|\.|of)?\s?' + months +
                    r'[a-y]{0,6}\s?(-|\.|,|of)?\s?' + years + whitespace +
                    hour_zone + whitespace + time_zone + whitespace + end]

        # (mon[a-z] d[d] [of] yy[yy]) (mon[a-z] - d[d] - yy[yy])
        # (mon[a-z] - d[d], yy[yy])
        patterns.append(beg + months + r'[a-y]{0,6}\s?[-\.]?\s?'
                        + days + whitespace + superscripts +
                        r'?\s?(,|\.|\s|of|-)\s?' + years + whitespace +
                        hour_zone + whitespace + time_zone + whitespace + end)

        # (d[d] m[m] yyyy) (dd - mm - yyyy) (dd / mm / yyyy) (dd . mm . yyyy)
        patterns.append(beg + days + sep + mons +
                        sep + years + whitespace + hour_zone +
                        whitespace + time_zone + whitespace + end)

        # (m[m] d[d] yyyy) (mm - dd - yyyy) (mm / dd / yyyy) (mm . dd . yyyy)
        patterns.append(beg + mons + sep + days +
                        sep + years + whitespace + hour_zone +
                        whitespace + time_zone + whitespace + end)

        # (yyyy m[m] d[d]) (yyyy - mm - dd) (yyyy / mm / dd) (yyyy . mm . dd)
        patterns.append(beg + years4 + sep + mons +
                        sep + days + whitespace + hour_zone +
                        whitespace + time_zone + whitespace + end)

        # (dd-mon[a-z]-yy[yy])
        patterns.append(beg + days + sep + months +
                        sep + years + whitespace + hour_zone +
                        whitespace + time_zone + whitespace + end)

        # (dd-dd-mon[a-z]-yy[yy])
        patterns.append(beg + days + sep + days + sep + months +
                        sep + years + whitespace + hour_zone +
                        whitespace + time_zone + whitespace + end)

        # ddmon[a-z]yy[yy]
        patterns.append(beg + days + whitespace + months +
                        whitespace + years + whitespace + hour_zone +
                        whitespace + time_zone + whitespace + end)

        # dd [th / st] mon[a-z] yy[yy]
        patterns.append(beg + days + whitespace + superscripts + sep +
                        months + sep + years + whitespace + hour_zone +
                        whitespace + time_zone + whitespace + end)

        # dd / mm
        patterns.append(beg + days + dash + all_months + end)

        # mm / dd
        patterns.append(beg + all_months + dash + days + end)

        patterns = [re.compile(pattern) for pattern in patterns]
        self.patterns = patterns

    def get_tok_indexlist(self, token_list):
        '''
        Given a list of text tokens, it returns a list with the the elements
        representing the starting point of a each token
        considering the spaces between the tokens
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
        Given a list of text tokens, it returns a dictionary with a
        reference mapping of characters to tokens index
        eg: Input = ["ab","cd","ef"]
            Output = {0: 0, 1: 0, 3: 1, 4: 1, 6: 2, 7: 2}
        '''
        chars_to_tokens = {}
        token_index = self.get_tok_indexlist(token_list)
        for index, token in enumerate(token_list):
            for i in range(token_index[index], token_index[index]+len(token)):
                chars_to_tokens[i] = index
        return chars_to_tokens

    def find_date_regex(self, text):
        dates = list()
        for _, pattern in enumerate(self.patterns):
            matches = re.finditer(pattern, text)
            for match in matches:
                dates.extend([(match.start(),
                              match.end()-1,
                              match.group(0).strip())])
        return dates

    def return_date_index(self, matches, tags_list, char_map):
        '''
        Given the matched groups,token_list,token_tags,char_mapping,
        extract the index of the tags_list to be qualified as DATE for SPV
        '''
        words_include = []
        existing_tags_index = []
        for match in matches:
            start = match[0]
            end = match[1]
            include = list(range(start, end, 1))
            words = list(set(
                [value for key, value in char_map.items() if key in include]))
            words_include.extend(words)
        existing_tags_index = [idx for idx,
                               tag in enumerate(tags_list) if tag != "O"]
        words_include_filtered = [
            i for i in words_include if i not in existing_tags_index]
        return words_include_filtered

    def match_ref(self, text, token_list, tags_list, entity='', verbose=False):
        date_indices = []
        text = text.strip().lower()
        if any(exp in text for exp in exceptions):
            return date_indices
        if text and not text.isspace():
            matches = self.find_date_regex(text)
            if len(matches) > 0:
                char_map = self.char_mapping(token_list)
                date_indices = self.return_date_index(
                    matches, tags_list, char_map)
                date_indices = sorted(list(set(date_indices)))
            if verbose and len(date_indices) > 0:  # pragma: no cover <--
                print(f'\nFinal Matches {entity}: '
                      f'{[token_list[idx] for idx in date_indices]}\n')
        return date_indices


if __name__ == '__main__':
    import spacy
    nlp = spacy.load('en_core_web_sm')

    test = "501,002MT"
    doc = nlp(test)
    toks = [t.text for t in doc]
    toks = [t.strip() for t in toks]
    text = " ".join(toks)
    tags = ['O']*len(doc)
    tag = "DATE"
    date_hdlr = DateHandler()
    date_indices = date_hdlr.match_ref(text, toks, tags,
                                       entity=tag,
                                       verbose=True)
    print(text)
    print(toks)
    print(['DATE' if idx in date_indices else 'O'
           for idx in range(len(toks))])
