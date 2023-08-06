"""Class to represent some source code."""

import json

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from matplotlib.pyplot import imshow
from pkg_resources import resource_filename
from typing import List, Tuple, Any, Dict
import warnings
from copy import deepcopy

from .viz_patch import VisualHighlight


class SourceCode(object):
    """Class to represent some source code."""

    def __init__(self, tokens: List[Dict[str, Any]], join_sequence=None):
        """Initialize the source code representation.

        - tokens: List[Dict[str, Any]]
            list of dictionaries which represent tokens.
            They need to have these fields:
                - 't' key contains the string reperesentation of the token,
                - 'i' key contains the major index position of the token,
                - 'si' key contains the minor index position (si = subindex),
                - 'l' key contains the line number of the token,
                - 'c' key contains the column number of the token.
                - 'd' key contains the number of other tokens sharing the same
                  index
            Note that the keys "si" and "d" are optional.
            An example of list of tokens:
            [
                {'t': 'def', 'i': 0, 'l': 1, 'c': 0},
                {'t': 'hello', 'i': 1, 'l': 1, 'c': 4, 'si': 0, 'd': 2},
                {'t': 'python', 'i': 1, 'l': 1, 'c': 10, 'si': 1, 'd': 2},
                {'t': '(', 'i': 2, 'l': 1, 'c': 16},
                ...
            ]
        - join_sequence: str
            (used in the string representation of the source code)
            a string to join the tokens within the same major index.
            in the example above, the join_sequence='_' would create a string
            representation of the source code like this:
            "def hello_python( ..."
        """
        # back compatibility code
        if isinstance(tokens, str):
            warnings.warn(
                'Passing the filepath in the constructor is deprecated. ' +
                'Use SourceCode.from_token_file(path_tokens_file) instead.')
            new_object = SourceCode.from_token_file(tokens)
            self.tokens = new_object.tokens
            self.join_sequence = new_object.join_sequence
        else:
            self.tokens = tokens
            self.join_sequence = join_sequence

    @classmethod
    def from_token_file(cls, path_tokens_file: str, join_sequence=None):
        """Create a source code object from a file with tokens.

        - file_with_tokens: str
            path to a json file containing tokens in this form:
            [
                {'t': 'def', 'i': 0, 'l': 1, 'c': 0},
                {'t': 'hello', 'i': 1, 'l': 1, 'c': 4, 'si': 0, 'd': 2},
                {'t': 'python', 'i': 1, 'l': 1, 'c': 10, 'si': 1, 'd': 2},
                {'t': '(', 'i': 2, 'l': 1, 'c': 16},
                ...
            ]
            where:
                - 't' key contains the string reperesentation of the token,
                - 'i' key contains the major index position of the token,
                - 'si' key contains the minor index position (si = subindex),
                - 'l' key contains the line number of the token,
                - 'c' key contains the column number of the token.
                - 'd' key contains the number of other tokens sharing the same
                  index
        - join_sequence: str
            (used in the string representation of the source code)
            a string to join the tokens within the same major index.
            in the example above, the join_sequence='_' would create a string
            representation of the source code like this:
            "def hello_python( ..."
        """
        tokens = json.loads(open(path_tokens_file, 'r').read())
        return SourceCode(
            tokens=tokens,
            join_sequence=join_sequence
        )

    def __str__(self):
        """Return a string representation of the source code."""
        string_reperesentation = ''
        col = 0
        line = 0
        for token in self.tokens:
            # reach the location of the token
            while line < token['l'] - 1:
                string_reperesentation += '\n'
                line += 1
                col = 0
            while col < token['c']:
                string_reperesentation += ' '
                col += 1
            string_reperesentation += token['t']
            col += len(token['t'])
            line += token['t'].count('\n')
            # check if the character will be followed by another subtoken
            if (
                    ("si" in token.keys()) and
                    (self.join_sequence is not None) and
                    (token['d'] - token["si"] > 1)):
                string_reperesentation += self.join_sequence
                col += len(self.join_sequence)

        return string_reperesentation

    def show_with_weights(
            self,
            weights,
            show_line_numbers: bool = False,
            squares=None,
            lines_highlight: List[Dict[str, Any]] = None,
            named_color='green',
            sum_scaler: float = 1.25,
            char_height: int = 40,
            hide_axes: bool = True,
            ):
        """Show the source code colored according to the weights.

        Parameters:
            - named_color: str
                name of the color to use for the source code
            - weights: list of floats (required)
                list of weights for each token. The higher the more intense the
                color is. In this example the first token is the one with a
                darker shade, while the last token will be completely white.
                weights=[10,5,6,7,3,1]
            - show_line_numbers: bool
                if True, the line numbers will be shown
            - squares: list of floats (default: None)
                one-hot encoding to decide wether some tokens should be
                surrounded by a red square. In this example the first and last
                tokens will be surrounded by a square:
                squares=[1,0,0,0,0,1]
            - lines_highlight: List of Dict (default: None)
                each dictionary should have the following keys:
                "line": to define the line to highlight
                "type": to define the type of highlight:
                    - "background": to highlight the line with a colored
                       background
                    - "squares": to highlight the line with a colored square
                "color": to define the color (use matplotlib named colors)
                "alpha": to define the transparency of the highlight (0 to 1)
                Note that it works only for the type background/
                Example:
                lines_highlight=[
                    {"line": 0, "type": "background", "color": "red",
                     "alpha": 1},
                    {"line": 1, "type": "square", "color": "blue"}
                ]
                to color the first line with red background and the second
                line with blue square. (Remember that the numbering starts
                from 1 since there is no line number zero intuitively.)
            - sum_scaler: float (default: 1.25)
                all the weights will be normalized with the value of the max
                wight multiplied by this number.
                Example with 1.25:
                weights [1, 2, 8] -> normalized weights [.1, 0.2, 0.8]
                since the max is: max(1 + 2 + 8) * 1.25 = 10
                normalized weights = weights / 10
            - char_height: int (default: 40)
            - hide_axes: bool (default: True)
        """
        # PREPARE IMAGE
        path_font_file = \
            resource_filename("codeattention", "assets/FreeMono.ttf")
        source_code_content = self.__str__()

        # COMPUTE GLOBAL ATTENTION
        global_attention = max(weights) * sum_scaler
        global_attention = global_attention if global_attention > 0 else 1

        ratio = .6
        char_width = char_height * ratio


        # compute max width and height required
        lines = source_code_content.splitlines()
        lines_len = [len(line) for line in lines]
        max_width = int(max(lines_len) * char_width)
        max_height = int(char_height * len(lines))

        # Compute the shift for line numbers
        if show_line_numbers:
            odg = len(str(len(lines)))
            shift = odg + 1  # shift to the right considering the extra space
            max_width += int(shift * char_width)
        else:
            shift = 0

        img = Image.new('RGB', (max_width, max_height), color=(255, 255, 255))
        fnt = ImageFont.truetype(path_font_file, char_height)
        drw = ImageDraw.Draw(img, 'RGBA')

        # HIGHLIGHT LINES
        if lines_highlight:
            for l_highlight in lines_highlight:
                new_line_highlight = \
                    VisualHighlight(
                        x=0,
                        y=char_height * int(l_highlight['line'] - 1),
                        width=max_width,
                        height=char_height)
                if l_highlight["type"] == "background":
                    if "alpha" in l_highlight.keys():
                        new_line_highlight.set_alpha(l_highlight["alpha"])
                    new_line_highlight.draw_PIL(
                        drw,
                        background_color=l_highlight["color"],
                        border_color=None)
                elif l_highlight["type"] == "square":
                    new_line_highlight.draw_PIL(
                        drw,
                        background_color='white',
                        border_color=l_highlight["color"])

        # check clicked tokens to draw squares around them
        if squares is not None:
            squared_tokens = np.array(squares)
            squared_tokens_indices = np.where(squared_tokens == 1)[0].tolist()
        else:
            squared_tokens_indices = []

        # INSTANTIATE TOKENS
        # get the positon form the metadata of tokens
        # DEBUG print(tokens)
        # DEBUG print(formattedcode)
        for i, (att, t) in enumerate(zip(weights, self.tokens)):
            # print(t)
            viz_token = \
                VisualHighlight(
                    x=char_width * int(t['c'] + shift),
                    y=char_height * int(t['l'] - 1),
                    width=char_width * len(t['t']),
                    height=char_height
                )
            alpha = att / global_attention
            viz_token.set_alpha(alpha)
            # draw the patch around the token first
            viz_token.draw_PIL(
                drw,
                background_color=named_color,
                border_color='red' if (i in squared_tokens_indices) else None
            )
            # draw one token at the time
            drw.text(
                (viz_token.x, viz_token.y),
                text=t["t"], font=fnt, fill=(0, 0, 0)
            )

        # Print line numbers
        if show_line_numbers:
            for i, line in enumerate(lines):
                drw.text(
                    (0, char_height * i),
                    text=str(i + 1).rjust(odg),
                    font=fnt, fill=(0, 0, 0)
                )

        # img.save(img_name)
        # return img_name
        imshow(np.asarray(img))
        fig = plt.gcf()
        # print(f'max_width: {max_width}')
        # print(f'max_width: {max_height}')
        FACTOR = 60
        fig.set_size_inches(max_width / FACTOR, max_height / FACTOR)

        ax = plt.gca()
        if hide_axes:
            ax.set_xticks([])
            ax.set_yticks([])
        return fig, ax
