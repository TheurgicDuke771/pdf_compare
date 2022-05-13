from pdfminer.converter import PDFConverter


##  HTMLConverter
class HTMLPrivateConverter(PDFConverter):
    RECT_COLORS = {
        'figure': 'yellow',
        'textline': 'magenta',
        'textbox': 'cyan',
        'textgroup': 'red',
        'curve': 'black',
        'page': 'gray',
    }

    TEXT_COLORS = {
        'textbox': 'blue',
        'char': 'black',
    }

    def __init__(self, rsrcmgr, outfp, pageno=1, laparams=None,
                 scale=1, fontscale=1.0, layoutmode='normal', showpageno=True,
                 pagemargin=50, imagewriter=None, header_text='', x_margin=0,
                 rect_colors={'curve': 'black', 'page': 'gray'},
                 text_colors={'char': 'black'}):
        PDFConverter.__init__(self, rsrcmgr, outfp, pageno=pageno, laparams=laparams)
        self.scale = scale
        self.fontscale = fontscale
        self.layoutmode = layoutmode
        self.showpageno = showpageno
        self.pagemargin = pagemargin
        self.imagewriter = imagewriter
        self.rect_colors = rect_colors
        self.text_colors = text_colors
        self.debug = False
        if self.debug:
            self.rect_colors.update(self.RECT_COLORS)
            self.text_colors.update(self.TEXT_COLORS)
        self._yoffset = self.pagemargin
        self._font = None
        self._ffont = ('AllAndNone', 11)
        self._fontstack = []
        self.header_text = header_text
        self.x_margin = x_margin
        self.write_header()
        return

    def write(self, text):
        self.outfp.write(text)
        return

    def write_header(self):
        if self.x_margin != 10:
            self.write('<div><span style="position:absolute; color:%s; left:%dpx; top:%dpx; font-size:%dpx;">' %
                       (1, self.x_margin + 200, 0, 30 * self.scale * 1))
        else:
            self.write('<div><span style="position:absolute; color:%s; left:%dpx; top:%dpx; font-size:%dpx;">' %
                       (1, self.x_margin + 7, 0, 30 * self.scale * 1))
        self.write_text(self.header_text)
        self.write('</span></div>\n')
        return

    def write_footer(self):
        self.write('</body></html>\n')
        return

    def write_text(self, text):
        self.write(text)
        return

    def place_rect(self, color, borderwidth, x, y, w, h):
        color = self.rect_colors.get(color)
        if color is not None:
            self.write('<span style="position:absolute; border: %s %dpx solid; '
                       'left:%dpx; top:%dpx; width:%dpx; height:%dpx;"></span>\n' %
                       (color, borderwidth,
                        x * self.scale, (self._yoffset - y) * self.scale,
                        w * self.scale, h * self.scale))
        return

    def place_border(self, color, borderwidth, item):
        self.place_rect(color, borderwidth, item.x0 + self.x_margin, item.y1, item.width, item.height)
        return

    def place_image(self, item, borderwidth, x, y, w, h):
        if self.imagewriter is not None:
            name = self.imagewriter.export_image(item)
            self.write('<img src="%s" border="%d" style="position:absolute; left:%dpx; top:%dpx;" '
                       'width="%d" height="%d" />\n' %
                       (name, borderwidth,
                        x * self.scale, (self._yoffset - y) * self.scale,
                        w * self.scale, h * self.scale))
        return

    def place_text(self, color, text, x, y, size):
        color = self.text_colors.get(color)
        if color is not None:
            self.write('<span style="position:absolute; color:%s; left:%dpx; top:%dpx; font-size:%dpx;">' %
                       (color, x * self.scale, (self._yoffset - y) * self.scale, size * self.scale * self.fontscale))
            self.write_text(text)
            self.write('</span>\n')
        return

    def begin_div(self, color, borderwidth, x, y, w, h, writing_mode=False):
        self._fontstack.append(self._font)
        self._font = None
        self.write('<div style="position:absolute; border: %s %dpx solid; writing-mode:%s; '
                   'left:%dpx; top:%dpx; width:%dpx; height:%dpx;">' %
                   (color, borderwidth, writing_mode,
                    x * self.scale, (self._yoffset - y) * self.scale,
                    w * self.scale, h * self.scale))
        return

    def end_div(self):
        if self._font is not None:
            self.write('</span>')
        self._font = self._fontstack.pop()
        self.write('</div>')
        return

    def put_text(self, text, fontname, size):
        self.write('<span style="font-family: %s; font-size:%dpx; letter-spacing:-1.2;">' %
                   (fontname, size * self.scale * self.fontscale))
        self.write_text(text)
        self.write('</span>')

        return

    def put_text_invalid(self, text, fontname, size):
        self.write(
            '<span style="font-family: %s; font-size:%dpx; background-color:rgb(255,153,153); letter-spacing:-1.2;">' %
            (fontname, size * self.scale * self.fontscale))
        self.write_text(text)
        self.write('</span>')
        return

    def page_begin(self, layout):
        self._yoffset += layout.y1
        self.place_border('page', 1, layout)
        if self.x_margin != 10:
            self.write('<div style="position:absolute; left:%dpx; top:%dpx;">' % (
                self.x_margin + 200, (self._yoffset - layout.y1) * self.scale))
        else:
            self.write('<div style="position:absolute; left:%dpx; top:%dpx;">' % (
                self.x_margin + 7, (self._yoffset - layout.y1) * self.scale))
        self.write('<a name="%s">Page %s</a></div>\n' % (layout.pageid, layout.pageid))

    def page_end(self):
        self._yoffset += self.pagemargin

    def put_newline(self):
        self.write('<br>\n')
        return

    def close(self):
        self.write_footer()
        return

