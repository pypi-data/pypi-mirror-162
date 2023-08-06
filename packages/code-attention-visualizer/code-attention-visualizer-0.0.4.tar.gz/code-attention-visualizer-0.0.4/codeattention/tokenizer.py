"""Utilities to create token files for Python and Java """
import abc
import json
import asttokens
import javalang


class Tokenizer(metaclass=abc.ABCMeta):
    """Tokenizer class to create a token list from a string.
    The token list is a list of dicts with the following keys:
    - t: the token text
    - i: the token index
    - c: the token column
    - l: the token line
    - d: the number of tokens sharing the same index i (they derive from a
            split via the separator, typically an "_")
    - si: the token subindex
    """

    def __init__(self, separator="_"):
        self.separator = separator
        self.tokens = None

    def tokenize(self, source_code):
        """Tokenize the source code."""
        tokens_minimal = self._minimal_parsing(source_code)
        tokens_fine_grade = self.tokens_split_on(
            tokens=tokens_minimal, separator=self.separator)
        tokens_no_space = self.remove_space_and_newline(tokens_fine_grade)
        tokens_reindexed = self.reassign_indices(tokens_no_space)
        self.tokens = tokens_reindexed
        return tokens_reindexed

    @abc.abstractmethod
    def _minimal_parsing(self, source_code):
        pass

    def tokens_split_on(self, tokens, separator="_"):
        """Split the char in subchar based on a separator such as "_" """
        new_tokens_list = []
        for t in tokens:
            if separator in t['t']:
                new_tokens_list += self.get_subtokens(
                    token=t, separator=separator)
            else:
                new_tokens_list.append(t)
        return new_tokens_list

    def get_subtokens(self, token, separator):
        """Split a token in subtokens based on the identifier."""
        parent_token = token
        string_text = parent_token['t']
        subtokens_list = []
        index = parent_token['i']
        start_column = parent_token['c']
        start_line = parent_token['l']
        subtokens = string_text.split(separator)
        for j, subtoken in enumerate(subtokens):
            t_copy = dict(parent_token)
            t_copy['t'] = subtoken
            t_copy['c'] = start_column
            t_copy['l'] = start_line
            t_copy['si'] = j
            t_copy['d'] = len(subtokens)
            subtokens_list.append(t_copy)
            # advance the counter
            index += 1
            start_column += (len(subtoken) + len(separator))
            start_line += subtoken.count('\n')
        return subtokens_list

    def remove_space_and_newline(self, tokens):
        """Remove all the tokens representing white spaces or new lines.
        """
        new_tokens = []
        for token in tokens:
            if token['t'].strip() not in ['', '\n']:
                new_tokens.append(token)
        return new_tokens

    def reassign_indices(self, tokens):
        """Reassign the indices of the tokens."""
        all_indices = []
        for token in tokens:
            all_indices.append(token['i'])
        # create a mapping between old indices and new incremental indices
        new_i = 0
        mapping = {}
        for e in sorted(set(all_indices)):
            mapping[e] = new_i
            new_i += 1
        # reassign the indices
        for token in tokens:
            token['i'] = mapping[token['i']]
        return tokens

    def get_tokens(self):
        """Return the token list."""
        if self.tokens is None:
            raise ValueError("No tokens to return. Call tokenize() first.")
        return self.tokens

    def save_tokens(self, filename='example_tokens.json'):
        """Save the token list in a json file."""
        if self.tokens is None:
            raise ValueError("No tokens to save. Call tokenize() first.")
        with open(filename, 'w') as fp:
            json.dump(self.tokens, fp)


class PythonTokenizer(Tokenizer):
    """Python tokenizer class."""

    def _minimal_parsing(self, source_code):
        atok = asttokens.ASTTokens(source_code, parse=True)
        tokens = []
        for i, t in enumerate(atok.tokens):
            c_token = {}
            c_token['t'] = t.string
            c_token['i'] = i
            c_token['l'] = t.start[0]
            c_token['c'] = t.start[1]
            tokens.append(c_token)
        return tokens


class JavaTokenizer(Tokenizer):
    """Java tokenizer class."""

    def _minimal_parsing(self, source_code):
        initial_tokens = list(javalang.tokenizer.tokenize(source_code))
        tokens = []
        i = 0
        old_line = 0
        end_col_last_token = 0
        for t in initial_tokens:
            c_token = {}
            c_token['t'] = t.value
            c_token['i'] = i
            c_token['l'] = t.position.line
            c_token['c'] = t.position.column
            # if it is a new line, add newline tokens in a number equal to the
            # difference between the old line and the new line
            if t.position.line > old_line:
                for j in range(old_line, t.position.line):
                    filler_token = {}
                    filler_token['t'] = '\n'
                    filler_token['i'] = i
                    filler_token['l'] = j
                    filler_token['c'] = end_col_last_token
                    tokens.append(filler_token)
                    end_col_last_token = 0
                    i += 1
            # if there are some spaces, insert new spaces as the difference
            # between the old column and the new column
            if t.position.column > end_col_last_token:
                space_length = t.position.column - end_col_last_token
                filler_token = {}
                filler_token['t'] = ' ' * space_length
                filler_token['i'] = i
                filler_token['l'] = t.position.line
                filler_token['c'] = end_col_last_token
                tokens.append(filler_token)
                end_col_last_token += space_length
                i += 1
            # add the new token
            tokens.append(c_token)
            end_col_last_token = t.position.column + len(t.value)
            i += 1
            old_line = t.position.line
        return tokens
