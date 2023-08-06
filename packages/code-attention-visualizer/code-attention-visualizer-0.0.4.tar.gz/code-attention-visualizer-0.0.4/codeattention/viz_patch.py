"""Class to represent the Token objects to highlight."""

from matplotlib import colors
from typing import List, Tuple, Dict, Any


class VisualHighlight(object):

    def __init__(self, x, y, width, height):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.alpha = 0.1

    def draw_PIL(self, drw,
                 background_color: str = 'lime',
                 alpha: float = None,
                 border_color: str = None,
                 border_width: int = 2):
        """Draw the patch on the plot.
            - alpha: float between 0 and 1 for the transparency of the patch.
              if not se the self.alpha parameter is used which is 0.1 by
              default.
            - background_color: string for the color of the patch.
            - border_color (default: None): string for the color of the border.
            - border_width (default: 2): int for the width of the border.
        """
        color_rgb = list(colors.to_rgb(background_color))
        color_rgb = [int(c * 255) for c in color_rgb]
        if alpha is None:
            alpha = self.alpha
        alpha = int(alpha * 255)
        color_rgba = color_rgb + [alpha]
        color_rgba = tuple(color_rgba)
        coors = [
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height]
        rect = \
            drw.rectangle(
                coors,
                outline=border_color,
                width=border_width,
                fill=color_rgba
            )

    def set_alpha(self, alpha):
        self.alpha = alpha

    def __repr__(self):

        return 'x:' + str(self.x).zfill(3) \
                + ' - y:' + str(self.y).zfill(3) \
                + ' - width:' + str(self.width).zfill(4) \
                + ' - height:' + str(self.height).zfill(4) \
                + ' - alpha:' + str(self.alpha)
