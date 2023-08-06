from collections import defaultdict

from bokeh.models.layouts import Column, Row
from bokeh.models import Toggle

class FigureGroup(object):
    def __init__(self, *figures):
        self.__figures = figures

    def legend(self, layout=Column, **kwargs):
        buttons = []
    
        for (label, color), glyphs in self.__figures_label_to_glyphs().items():
            toggle = Toggle(label=label, background=color)
            toggle.active = True
            
            for glyph in glyphs:
                toggle.js_link('active', glyph, 'visible')
            
            buttons.append(toggle)
        
        return layout(*buttons, **kwargs)

    def __figures_label_to_glyphs(self):
        label_to_glyphs = defaultdict(list)
        
        for figure in self.__figures:
            for key, value in self.__figure_label_to_glyphs(figure).items():
                label_to_glyphs[key].extend(value)
                
        return label_to_glyphs

    def __figure_label_to_glyphs(self, figure):
        legend = self.__figure_legend(figure)
        label_to_glyphs = dict()
        
        for item in legend.items:
            label = item.label.get('value', None)
            
            if not item.renderers:
                continue
            
            if label:
                ref_glyph = item.renderers[0].glyph # https://stackoverflow.com/questions/610883/how-to-know-if-an-object-has-an-attribute-in-python # Always references the first glyph
                
                color = getattr(ref_glyph, 'fill_color', getattr(ref_glyph, 'line_color', 'grey')) # use fill_color if exists otherwise line_color, default to grey if none exist
                
                label_to_glyphs.update({(label, color): item.renderers})
        
        return label_to_glyphs

    def __figure_legend(self, figure):
        return figure.legend[0]
