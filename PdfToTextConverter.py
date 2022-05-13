from io import StringIO
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LTTextBox, LTTextLine, LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from HtmlConverter import HTMLPrivateConverter


class PdfToText(object):
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self.codec = 'utf-8'
        self.scale = 1

    def convert_pdf_to_txt(self, path, page_no=-1):
        rsrcmgr = PDFResourceManager()

        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        i = 0
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                      check_extractable=True):
            i += 1
            if i != page_no:
                continue
            interpreter.process_page(page)

        fp.close()
        device.close()
        str = retstr.getvalue()
        retstr.close()

        return str

    def read_pdf(self, file_name):
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        fp = open(file_name, 'rb')
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        pages = {}
        for page in PDFPage.create_pages(document):
            dictionary = {}
            dictionary['textbox'] = []
            dictionary['textline'] = []

            interpreter.process_page(page)
            layout = device.get_result()
            for item in layout:
                if isinstance(item, LTTextBox):
                    dictionary['textbox'].append(item)
                    for child in item:
                        if isinstance(child, LTTextLine):
                            dictionary['textline'].append(child)
            pages[layout.pageid] = dictionary
        return pages

    def compare_pdf(self, file1, file2, header_text, x_margin=10, compare_margin=0.2):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        fp = open(file1, 'rb')
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)

        out = StringIO()

        layoutmode = 'normal'
        scale = 1.3
        fontscale = 1

        html_coverter = HTMLPrivateConverter(rsrcmgr, out, scale=scale,
                                             layoutmode=layoutmode, laparams=laparams, fontscale=fontscale,
                                             imagewriter=None, header_text=header_text, x_margin=x_margin)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        testpages = PDFPage.create_pages(document)

        file_dict = self.read_pdf(file2)

        for page in testpages:
            interpreter.process_page(page)
            layout = device.get_result()

            html_coverter.page_begin(layout)
            if file_dict.get(layout.pageid) == None:
                break
            compare_page = file_dict[layout.pageid]

            for item in layout:
                if isinstance(item, LTTextBox):
                    html_coverter.begin_div('textbox', 1, item.x0 + html_coverter.x_margin, item.y1, item.width,
                                            item.height,
                                            item.get_writing_mode())

                    for child in item:
                        if isinstance(child, LTTextLine):
                            self.compare_textline(child, compare_page, html_coverter, compare_margin)
                            html_coverter.put_newline()
                    html_coverter.end_div()
            html_coverter.page_end()

        fp.close()
        device.close()
        retstr.close()

        return out.getvalue()

    def compare_textline(self, child, compare_page, html_coverter, compare_margin):
        comp_result = True
        for comp_textline in compare_page['textline']:
            if child.x0 - compare_margin < comp_textline.x0 and comp_textline.x0 < child.x0 + compare_margin and child.y1 - compare_margin < comp_textline.y1 and comp_textline.y1 < child.y1 + compare_margin:
                if child.get_text() != comp_textline.get_text():
                    html_coverter.put_text_invalid(child.get_text(), child._objs[0].fontname, child._objs[0].size)
                else:
                    html_coverter.put_text(child.get_text(), child._objs[0].fontname, child._objs[0].size)

                comp_result = False
                break

        if comp_result:
            html_coverter.put_text_invalid(child.get_text(), child._objs[0].fontname, child._objs[0].size)

    def convert_list(self, obj):
        list = []
        for child in obj:
            list.append(child)
        return list

