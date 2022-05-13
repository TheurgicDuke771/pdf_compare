from io import StringIO
import tkinter as tk
from tkinter import filedialog, messagebox
from PdfToTextConverter import PdfToText


global source_file_path, target_file_path, margin_value, output_file_path
source_file_path = ''
target_file_path = ''
margin_value = 0.2
output_file_path = 'output.html'


def get_source_file_path():
    global source_file_path
    source_file_path = filedialog.askopenfilename(filetypes=[("PDF files", ".pdf"), ('All Files', '*.*')])
    messagebox.showinfo("INFO", f"Source file {source_file_path} uploaded.")
    print(source_file_path)


def get_target_file_path():
    global target_file_path
    target_file_path = filedialog.askopenfilename(filetypes=[("PDF files", ".pdf"), ('All Files', '*.*')])
    messagebox.showinfo("INFO", f"Target file {target_file_path} uploaded.")
    print(target_file_path)


def update_output_filename(entry):
    global output_file_path
    output_file_path = entry.get()
    if output_file_path is None or output_file_path == '':
        output_file_path = 'output.html'
    print(output_file_path)


def update_margin(entry):
    global margin_value
    margin_value = entry.get()
    try:
        margin_value = float(margin_value)
    except:
        margin_value = 0.2
    print(margin_value)


def merge_html(output_html1, output_html2):
    html = StringIO()
    html.write('<!DOCTYPE HTML PUBLIC>\n')
    html.write('<html><head>\n')
    html.write('<meta http-equiv="Content-Type" content="text/html; charset=%s">\n' % 'utf-8')
    html.write('</head><body>\n')

    html.write('<table><tr><td>\n')
    html.write(output_html1)
    html.write('</td>\n')
    html.write('<td>\n')
    html.write(output_html2)
    html.write('</td></tr></table>\n')

    html.write('</body></html>\n')
    return html.getvalue()


def compare_pdf(file1, file2, output_file, compare_margin=0.2):
    if file1 is not None and file1 != '' and file2 is not None and file2 != '':
        pdf_reader = PdfToText()

        output_html1 = pdf_reader.compare_pdf(file1, file2, 'AS-IS', compare_margin=compare_margin)
        output_html2 = pdf_reader.compare_pdf(file2, file1, 'TO-BE', 650, compare_margin=compare_margin)

        html = merge_html(output_html1, output_html2)

        f_out = open(output_file, 'w', -1, 'utf-8')
        f_out.write(html)
        messagebox.showinfo("INFO", f"Comparison completed. \nResult saved in {output_file} file.")

        global source_file_path, target_file_path, margin_value, output_file_path
        source_file_path = ''
        target_file_path = ''
        margin_value = 0.2
        output_file_path = 'output.html'

    else:
        messagebox.showerror("ERROR", "Please Upload a file first")


def replace_string_to_sql_format(sql_str):
    sql_str = str(sql_str)
    sql_str = sql_str.replace('\\', '\\\\')
    sql_str = sql_str.replace("'", "\\'")
    return sql_str


def main():
    global source_file_path, target_file_path, margin_value, output_file_path
    scores = tk.Tk()
    scores.geometry('350x200')
    scores.winfo_screenwidth(), scores.winfo_screenheight()
    scores.resizable(width=False, height=False)

    label1 = tk.Label(scores, text="PDF Diff Tool", font=("Arial", 20))
    label1.grid(row=0, column=0, columnspan=4)

    uploadFile1 = tk.Button(
        scores,text="Upload Source File",width=20,command=get_source_file_path)
    uploadFile1.grid(row=1, column=0, pady=7)

    uploadFile2 = tk.Button(
        scores,text="Upload Target File",width=20,command=get_target_file_path)
    uploadFile2.grid(row=1, column=1, padx=10, pady=7)

    output_file = tk.Entry(scores)
    output_file.insert(0, output_file_path)
    output_file.grid(row=2, column=0, pady=5)
    update_output_file_btn = tk.Button(
        scores, text="Update Output File Name", width=20, command=lambda: update_output_filename(output_file))
    update_output_file_btn.grid(row=2, column=1, padx=10, pady=5)
    
    margin = tk.Entry(scores)
    margin.insert(0, margin_value)
    margin.grid(row=3, column=0, pady=5)
    update_margin_btn = tk.Button(
        scores, text="Update Margin Value", width=20, command=lambda: update_margin(margin))
    update_margin_btn.grid(row=3, column=1, padx=10, pady=5)

    dfButton = tk.Button(
        scores,text="PDF Diff",width=20,bg="green",fg="white",
        command=lambda: compare_pdf(source_file_path,target_file_path, output_file_path, margin_value))
    dfButton.grid(row=4, column=0, pady=5)
    
    closeButton = tk.Button(
        scores,text="Close",width=20,bg="red",fg="white",command=exit)
    closeButton.grid(row=4, column=1, padx=10, pady=5)

    scores.mainloop()


if __name__ == "__main__":
    main()

