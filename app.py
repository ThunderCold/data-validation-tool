import tkinter as tk
from tkinter import font
from tkinter import filedialog
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from google.api_core.exceptions import InvalidArgument
import csv
from frictionless import Schema
from frictionless import validate
import yaml
import time
import os

window = tk.Tk()
window.title('mytitle')
window.geometry('1280x720')
window.resizable(False, False)
custom_font = font.Font(family='Ariel', size=15)

s_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    }
]
# cur_messege = tk.StringVar()
global yaml_data2
global pagenum_list
sleep_time = 7
page2_curnum = 0
page2_yaml_len = 0
cur_page = 1 # function in queue
constraints_list = ['minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum', 'minLength', 'maxLength', 'jsonSchema', 'pattern', 'enum']
type_list = ['string', 'number', 'integer', 'boolean', 'datetime', 'date', 'time', 'year', 'yearmonth', 'duration', 'geopoint', 'geojson', 'any', 'object', 'array', 'list']
pagenum_list = ['']

def showPage1():
    frame2.pack_forget()
    frame3.pack_forget()
    frame1.pack(expand=True, fill='both')
    frame1.tkraise()

def showPage2():
    frame1.pack_forget()
    frame3.pack_forget()
    frame2.pack(expand=True, fill='both')
    frame2.tkraise()

def showPage3():
    frame1.pack_forget()
    frame2.pack_forget()
    frame3.pack(expand=True, fill='both')
    frame3.tkraise()

def browseDataFile():
    file_path = filedialog.askopenfilename()
    try:
        entry_data.delete(0, tk.END)
        entry_data.insert(tk.END, os.path.relpath(file_path))
    except Exception as e:
        print(f"An error occurred: {e}")

def browseDescriptionFile():
    file_path = filedialog.askopenfilename()
    try:
        entry_description.delete(0, tk.END)
        entry_description.insert(tk.END, os.path.relpath(file_path))
    except Exception as e:
        print(f"An error occurred: {e}")

def browseYamlFile2():
    file_path = filedialog.askopenfilename()
    try:
        entry2_yaml.delete(0, tk.END)
        entry2_yaml.insert(tk.END, os.path.relpath(file_path))
    except Exception as e:
        print(f"An error occurred: {e}")

def browseDataFile3():
    file_path = filedialog.askopenfilename()
    try:
        entry3_data.delete(0, tk.END)
        entry3_data.insert(tk.END, os.path.relpath(file_path))
    except Exception as e:
        print(f"An error occurred: {e}")

def browseYamlFile3():
    file_path = filedialog.askopenfilename()
    try:
        entry3_yaml.delete(0, tk.END)
        entry3_yaml.insert(tk.END, os.path.relpath(file_path))
    except Exception as e:
        print(f"An error occurred: {e}")

def chkbox_apiPress():
    if chkbox_api_var.get():
        entry_api.config(state='normal')
    else:
        entry_api.delete(0, tk.END)
        entry_api.config(state='disabled')

def newMessege(s):
    text1_result.config(state='normal')
    text1_result.insert('end', f'{s}\n\n')
    text1_result.yview_moveto(1.0)
    text1_result.config(state='disabled')
    # cur_messege.set(f'System Messege: {s}')
    frame1.update_idletasks()

def askGemini(i, model, listReport):

    name = listReport[0][i]
    title = listReport[1][i]
    description = listReport[2][i]
    type = listReport[3][i]

    print(f"name: {name}")
    newMessege(f'Detecting {name} field...')

    max_question = f'name: {name}\ntitle: {title}\ndescription: {description}\ntype: {type}\n\nThe above is the description of a data field. What is the maximum reasonable real-world value ​​for this data field? Please output this value ​​directly without any additional explanation. If the maximum reasonable real-world value ​​cannot be determined, "Null" is output.'
    max_response = model.generate_content(
        contents=max_question,
        safety_settings=s_settings
    )
    min_question = f'name: {name}\ntitle: {title}\ndescription: {description}\ntype: {type}\n\nThe above is the description of a data field. What is the minimum reasonable real-world value ​​for this data field? Please output this value ​​directly without any additional explanation. If the minimum reasonable real-world value ​​cannot be determined, "Null" is output.'
    min_response = model.generate_content(
        contents=min_question,
        safety_settings=s_settings
    )
    # print(f"max: {max_response.text.strip()}")
    # print(f"min: {min_response.text.strip()}")
    newMessege(f'{name} field:\nminimum:{min_response.text.strip()}, maximum:{max_response.text.strip()}')
    return max_response.text.strip(), min_response.text.strip()

def submitPress():
    text1_result.config(state='normal')
    text1_result.delete('1.0', tk.END)
    text1_result.config(state='disabled')

    data_filename = entry_data.get()
    description_filename = entry_description.get()
    api_key = entry_api.get()

    yaml_filename = f'{data_filename}.schema.yaml'
    schema = Schema.describe(data_filename)
    schema.to_yaml(yaml_filename)

    with open(description_filename, newline='') as csvfile:
        with open(yaml_filename, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(csvfile)
            listReport = list(csv_reader)
            yaml_data = yaml.safe_load(file)
            for i in range(len(yaml_data['fields'])):
                yaml_data['fields'][i]['title'] = listReport[1][i]
                yaml_data['fields'][i]['description'] = listReport[2][i]
                # print(yaml_data['fields'][i]['description'])
        with open(yaml_filename, 'w', encoding='utf-8') as file:
            yaml.safe_dump(yaml_data, file)


    newMessege(f'Create {data_filename}.schema.yaml sucessfully')

    if chkbox_api_var.get():
        with open(description_filename, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            listReport = list(csv_reader)

        genai.configure(api_key = api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        with open(yaml_filename, 'r') as file:
            yaml_data = yaml.safe_load(file)

        for i in range(len(yaml_data['fields'])):
            d = {}
            if yaml_data['fields'][i]['type'] == 'integer' or yaml_data['fields'][i]['type'] == 'number':
                get_value = False
                error_break = False
                
                retry_attempts = 3
                attempts = 0

                while attempts < retry_attempts:
                    try:
                        max_constraints, min_constraints = askGemini(i, model, listReport)
                        break
                    except ResourceExhausted as e:
                        attempts += 1
                        if attempts < retry_attempts:
                            # print(f"{e}: 出現 ResourceExhausted 錯誤，將自動重試")
                            newMessege('ResourceExhausted error occurred, will automatically retry')
                            time.sleep(sleep_time)  # 等待一段時間後重試
                        else:
                            # print(f"{e}: 出現 ResourceExhausted 錯誤，多次嘗試仍失敗，終止 AI 偵測")
                            newMessege('Multiple ResourceExhausted errors occurred, terminating AI detection')
                            error_break = True
                            break
                    except InvalidArgument as e:
                        # print(f"{e}: 出現 InvalidArgument 錯誤")
                        newMessege('InvalidArgument error occurred, please check API key')
                        error_break = True
                        break
                    except Exception as e:
                        newMessege('Unexpected error occurred')
                        error_break = True
                        break

                if error_break:
                    break

                try:
                    if max_constraints != 'Null':
                        get_value = True
                        if yaml_data['fields'][i]['type'] == 'integer':
                            d['maximum'] = int(float(max_constraints))
                        else:
                            d['maximum'] = float(max_constraints)
                    if min_constraints != 'Null':
                        get_value = True
                        if yaml_data['fields'][i]['type'] == 'integer':
                            d['minimum'] = int(float(min_constraints))
                        else:
                            d['minimum'] = float(min_constraints)
                except ValueError as e:
                    print(f"Error converting constraints for field {i}: {e}")
                
                if get_value:
                    yaml_data['fields'][i]['constraints'] = d
                with open(yaml_filename, 'w') as file:
                    yaml.safe_dump(yaml_data, file)
                
                time.sleep(sleep_time)
        if not error_break:
            newMessege('AI detection completed')

def page2Show(cur):
    global yaml_data2
    global page2_yaml_len
    page2_yaml_len = len(yaml_data2['fields'])
    if cur == 0:
        btn2_prev.config(state='disabled')
    else:
        btn2_prev.config(state='normal')
    if cur == page2_yaml_len - 1:
        btn2_next.config(state='disabled')
    else:
        btn2_next.config(state='normal')
    entry2_name.config(state='normal')
    entry2_name.delete(0, tk.END)
    entry2_title.delete(0, tk.END)
    entry2_format.delete(0, tk.END)
    # entry2_type.delete(0, tk.END)
    entry2_description.delete(0, tk.END)
    for i in entry2_constraints:
        i.delete(0, tk.END)
    chkbox2_required.deselect()
    chkbox2_unique.deselect()
    if 'name' in yaml_data2['fields'][cur]:
        entry2_name.insert(tk.END, yaml_data2['fields'][cur]['name'])
    entry2_name.config(state='disabled')
    if 'title' in yaml_data2['fields'][cur]:
        entry2_title.insert(tk.END, yaml_data2['fields'][cur]['title'])
    if 'type' in yaml_data2['fields'][cur]:
        omenu2_type_var.set(yaml_data2['fields'][cur]['type'])
        # entry2_type.insert(tk.END, yaml_data2['fields'][cur]['type'])
    if 'format' in yaml_data2['fields'][cur]:
        entry2_format.insert(tk.END, yaml_data2['fields'][cur]['format'])
    if 'description' in yaml_data2['fields'][cur]:
        entry2_description.insert(tk.END, yaml_data2['fields'][cur]['description'])
    if 'constraints' in yaml_data2['fields'][cur]:
        if 'required' in yaml_data2['fields'][cur]['constraints']:
            if yaml_data2['fields'][cur]['constraints']['required']:
                chkbox2_required.select()
        if 'unique' in yaml_data2['fields'][cur]['constraints']:
            if yaml_data2['fields'][cur]['constraints']['unique']:
                chkbox2_unique.select()
        for i in range(9):
            if constraints_list[i] in yaml_data2['fields'][cur]['constraints']:
                tmp = yaml_data2['fields'][cur]['constraints'][constraints_list[i]]
                entry2_constraints[i].insert(tk.END, tmp)

def submit2Press():
    global page2_curnum
    global yaml_data2
    page2_curnum = 0
    with open(entry2_yaml.get(), 'r', encoding='utf-8') as file:
        yaml_data2 = yaml.safe_load(file)
    # entry2_name.config(state='normal')
    entry2_title.config(state='normal')
    omenu2_type.config(state='normal')
    entry2_format.config(state='normal')
    entry2_description.config(state='normal')
    chkbox2_required.config(state='normal')
    chkbox2_unique.config(state='normal')
    for i in entry2_constraints:
        i.config(state='normal')
    btn2_save.config(state='normal')
    page2Show(page2_curnum)

def tmpSave(cur):
    global yaml_data2
    if entry2_name.get() != "":
        yaml_data2['fields'][cur]['name'] = entry2_name.get()
    if entry2_title.get() != "":
        yaml_data2['fields'][cur]['title'] = entry2_title.get()
    # if entry2_type.get() != "":
    #     yaml_data2['fields'][cur]['type'] = entry2_type.get()
    yaml_data2['fields'][cur]['type'] = omenu2_type_var.get()
    if entry2_format.get() != "":
        yaml_data2['fields'][cur]['format'] = entry2_format.get()
    if entry2_description.get() != "":
        yaml_data2['fields'][cur]['description'] = entry2_description.get()
    d = {}
    if chkbox2_required_var.get():
        d['required'] = True
    if chkbox2_unique_var.get():
        d['unique'] = True
    for i in range(9):
        if entry2_constraints[i].get() != "":
            d[constraints_list[i]] = entry2_constraints[i].get()
    yaml_data2['fields'][cur]['constraints'] = d

def prevPress():
    global page2_curnum
    tmpSave(page2_curnum)
    page2_curnum -= 1
    page2Show(page2_curnum)

def nextPress():
    global page2_curnum
    tmpSave(page2_curnum)
    page2_curnum += 1
    page2Show(page2_curnum)

def savePress():
    global page2_curnum
    global yaml_data2
    tmpSave(page2_curnum)
    with open(entry2_yaml.get(), 'w') as file:
        yaml.safe_dump(yaml_data2, file)

def submit3Press():
    data_filename = entry3_data.get()
    yaml_filename = entry3_yaml.get()

    text3_result.config(state='normal')
    text3_result.delete('1.0', tk.END)
    text3_result.config(state='disabled')

    yaml_report = validate(yaml_filename)
    if yaml_report.valid:
        data_report = validate(data_filename, schema=yaml_filename)
        error_num = data_report.stats['errors']
        if error_num == 0:
            newMessege3('There are no errors in the dataset.')
        elif error_num == 1:
            newMessege3('There is 1 error in the dataset:')
        else:
            newMessege3(f'There are {error_num} errors in the dataset:')
        for i in range(error_num):
            newMessege3(f'{data_report.tasks[0].errors[i].title}:\n{data_report.tasks[0].errors[i].message}')
    else:
        newMessege3('The .yaml file is not valid:')
        error_num = yaml_report.stats['errors']
        for i in range(error_num):
            newMessege3(f'{yaml_report.tasks[0].errors[i].title}:\n{yaml_report.tasks[0].errors[i].message}')
            

def newMessege3(cur):
    text3_result.config(state='normal')
    text3_result.insert('end', f'{cur}\n\n')
    text3_result.config(state='disabled')

##########################

menubar = tk.Menu(window)
filemenu = tk.Menu(menubar)
filemenu.add_command(label="page1", command=showPage1)
filemenu.add_command(label="page2", command=showPage2)
filemenu.add_command(label="page3", command=showPage3)
menubar.add_cascade(label='Function', menu=filemenu)
window.config(menu=menubar)
frame1 = tk.Frame(window)
frame2 = tk.Frame(window)
frame3 = tk.Frame(window)

frame1o = tk.Frame(frame1, height=100, width=150)
frame1o.place(x=250, y=370)
scrollbar1 = tk.Scrollbar(frame1o)
scrollbar1.pack(side='right', fill='y')
text1_result = tk.Text(
    frame1o,
    height=13,
    width=65,
    yscrollcommand=scrollbar1.set,
    font=custom_font,
    state='disabled'
)
text1_result.pack()
scrollbar1.config(command=text1_result.yview)

frame3o = tk.Frame(frame3, height=100, width=150)
frame3o.place(x=250, y=300)
scrollbar3 = tk.Scrollbar(frame3o)
scrollbar3.pack(side='right', fill='y')
text3_result = tk.Text(
    frame3o,
    height=13,
    width=65,
    yscrollcommand=scrollbar3.set,
    font=custom_font,
    state='disabled'
)
text3_result.pack()
scrollbar3.config(command=text3_result.yview)

########################## frame1

lbl_data = tk.Label(
    frame1,
    text='Data File',
    fg='black',
    font=custom_font
)

lbl_description = tk.Label(
    frame1,
    text='Description File',
    fg='black',
    font=custom_font
)

lbl_api = tk.Label(
    frame1,
    text='Gemini API Key',
    fg='black',
    font=custom_font
)

lbl_messege = tk.Label(
    frame1,
    text='System Messege',
    fg='black',
    font=custom_font
)

entry_data = tk.Entry(frame1, font=custom_font, width=50)
entry_description = tk.Entry(frame1, font=custom_font, width=50)
entry_api = tk.Entry(frame1, font=custom_font, width=40, state='disabled')

btn_browse_data = tk.Button(
    frame1,
    text='...',
    font=custom_font,
    command=browseDataFile
)

btn_browse_description = tk.Button(
    frame1,
    text='...',
    font=custom_font,
    command=browseDescriptionFile
)

chkbox_api_var = tk.IntVar()
chkbox_api = tk.Checkbutton(
    frame1,
    text='Use Gemini AI',
    font=custom_font,
    variable=chkbox_api_var,
    command=chkbox_apiPress
)

btn_submit = tk.Button(
    frame1,
    text='Submit',
    font=custom_font,
    command=submitPress
)

lbl_data.place(x=20, y=100)
lbl_description.place(x=20, y=150)
chkbox_api.place(x=20, y=200)
lbl_api.place(x=20, y=250)
lbl_messege.place(x=20, y=370)
entry_data.place(x=250, y=100)
entry_description.place(x=250, y=150)
entry_api.place(x=250, y=250)
btn_browse_data.place(x=930, y=100)
btn_browse_description.place(x=930, y=150)
btn_submit.place(x=20, y=300)

############################# frame2

lbl2_yaml = tk.Label(
    frame2,
    text='YAML File',
    fg='black',
    font=custom_font
)

lbl2_name = tk.Label(
    frame2,
    text='name',
    fg='black',
    font=custom_font
)

lbl2_title = tk.Label(
    frame2,
    text='title',
    fg='black',
    font=custom_font
)

lbl2_type = tk.Label(
    frame2,
    text='type',
    fg='black',
    font=custom_font
)

lbl2_format = tk.Label(
    frame2,
    text='format',
    fg='black',
    font=custom_font
)

lbl2_description = tk.Label(
    frame2,
    text='description',
    fg='black',
    font=custom_font
)

lbl2_constraints = tk.Label(
    frame2,
    text='constraints',
    fg='black',
    font=custom_font
)

lbl2_required = tk.Label(
    frame2,
    text='required',
    fg='black',
    font=custom_font
)

lbl2_unique = tk.Label(
    frame2,
    text='unique',
    fg='black',
    font=custom_font
)

lbl2_minimum = tk.Label(
    frame2,
    text='minimum',
    fg='black',
    font=custom_font
)

lbl2_maximum = tk.Label(
    frame2,
    text='maximum',
    fg='black',
    font=custom_font
)

lbl2_exclusiveMinimum = tk.Label(
    frame2,
    text='exclusiveMinimum',
    fg='black',
    font=custom_font
)

lbl2_exclusiveMaximum = tk.Label(
    frame2,
    text='exclusiveMaximum',
    fg='black',
    font=custom_font
)

lbl2_minLength = tk.Label(
    frame2,
    text='minLength',
    fg='black',
    font=custom_font
)

lbl2_maxLength = tk.Label(
    frame2,
    text='maxLength',
    fg='black',
    font=custom_font
)

lbl2_jsonSchema = tk.Label(
    frame2,
    text='jsonSchema',
    fg='black',
    font=custom_font
)

lbl2_pattern = tk.Label(
    frame2,
    text='pattern',
    fg='black',
    font=custom_font
)

lbl2_enum = tk.Label(
    frame2,
    text='enum',
    fg='black',
    font=custom_font
)

entry2_yaml = tk.Entry(frame2, font=custom_font, width=50)
entry2_name = tk.Entry(frame2, font=custom_font, width=25, state='disabled')
entry2_title = tk.Entry(frame2, font=custom_font, width=25, state='disabled')
entry2_format = tk.Entry(frame2, font=custom_font, width=25, state='disabled')
# entry2_type = tk.Entry(frame2, font=custom_font, width=50)
entry2_description = tk.Entry(frame2, font=custom_font, width=50, state='disabled')

omenu2_type_var = tk.StringVar()
omenu2_type = tk.OptionMenu(
    frame2,
    omenu2_type_var,
    *type_list
)
omenu2_type.config(state='disabled')

chkbox2_required_var = tk.BooleanVar()
chkbox2_unique_var = tk.BooleanVar()
entry2_constraints = []
for i in range(9):
    entry2_constraints.append(
        tk.Entry(frame2, font=custom_font, width=20, state='disabled')
    )

chkbox2_required = tk.Checkbutton(
    frame2,
    text='',
    font=custom_font,
    variable=chkbox2_required_var,
    state='disabled'
)

chkbox2_unique = tk.Checkbutton(
    frame2,
    text='',
    font=custom_font,
    variable=chkbox2_unique_var,
    state='disabled'
)

btn2_browse_yaml = tk.Button(
    frame2,
    text='...',
    font=custom_font,
    command=browseYamlFile2
)

btn2_submit = tk.Button(
    frame2,
    text='Submit',
    font=custom_font,
    command=submit2Press
)

btn2_prev = tk.Button(
    frame2,
    text='<',
    font=custom_font,
    command=prevPress,
    state='disabled'
)

btn2_next = tk.Button(
    frame2,
    text='>',
    font=custom_font,
    command=nextPress,
    state='disabled'
)

btn2_save = tk.Button(
    frame2,
    text='save',
    font=custom_font,
    command=savePress,
    state='disabled'
)

lbl2_yaml.place(x=20, y=100)
lbl2_name.place(x=20, y=200)
lbl2_title.place(x=700, y=200)
lbl2_type.place(x=20, y=250)
lbl2_format.place(x=700, y=250)
lbl2_description.place(x=20, y=300)
lbl2_constraints.place(x=20, y=350)
lbl2_required.place(x=250, y=350)
lbl2_unique.place(x=740, y=350)
lbl2_minimum.place(x=250, y=400)
lbl2_maximum.place(x=740, y=400)
lbl2_exclusiveMinimum.place(x=250, y=450)
lbl2_exclusiveMaximum.place(x=740, y=450)
lbl2_minLength.place(x=250, y=500)
lbl2_maxLength.place(x=740, y=500)
lbl2_jsonSchema.place(x=250, y=550)
lbl2_pattern.place(x=740, y=550)
lbl2_enum.place(x=250, y=600)
entry2_yaml.place(x=250, y=100)
entry2_name.place(x=250, y=200)
entry2_title.place(x=800, y=200)
omenu2_type.place(x=250, y=250)
entry2_format.place(x=800, y=250)
entry2_description.place(x=250, y=300)
entry2_constraints[0].place(x=450, y=400)
entry2_constraints[1].place(x=940, y=400)
entry2_constraints[2].place(x=450, y=450)
entry2_constraints[3].place(x=940, y=450)
entry2_constraints[4].place(x=450, y=500)
entry2_constraints[5].place(x=940, y=500)
entry2_constraints[6].place(x=450, y=550)
entry2_constraints[7].place(x=940, y=550)
entry2_constraints[8].place(x=450, y=600)
btn2_browse_yaml.place(x=930, y=100)
btn2_submit.place(x=20, y=150)
btn2_prev.place(x=350, y=650)
btn2_next.place(x=550, y=650)
btn2_save.place(x=750, y=650)
chkbox2_required.place(x=350, y=350)
chkbox2_unique.place(x=820, y=350)

############################# frame3

lbl3_data = tk.Label(
    frame3,
    text='Data File',
    fg='black',
    font=custom_font
)

lbl3_yaml = tk.Label(
    frame3,
    text='YAML File',
    fg='black',
    font=custom_font
)

lbl3_result = tk.Label(
    frame3,
    text='Validation Results',
    fg='black',
    font=custom_font
)

entry3_data = tk.Entry(frame3, font=custom_font, width=50)
entry3_yaml = tk.Entry(frame3, font=custom_font, width=50)

btn3_browse_data = tk.Button(
    frame3,
    text='...',
    font=custom_font,
    command=browseDataFile3
)

btn3_browse_yaml = tk.Button(
    frame3,
    text='...',
    font=custom_font,
    command=browseYamlFile3
)

btn3_submit = tk.Button(
    frame3,
    text='Submit',
    font=custom_font,
    command=submit3Press
)

lbl3_data.place(x=20, y=100)
lbl3_yaml.place(x=20, y=150)
lbl3_result.place(x=20, y=300)
entry3_data.place(x=250, y=100)
entry3_yaml.place(x=250, y=150)
btn3_browse_data.place(x=930, y=100)
btn3_browse_yaml.place(x=930, y=150)
btn3_submit.place(x=20, y=200)

#############################

frame1.pack(expand=True, fill='both')
frame1.tkraise()
window.mainloop()
