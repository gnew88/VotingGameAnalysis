import pandas as pd
from datetime import date
from docx import Document
from docx.shared import Inches
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

class reportGenerator:
    def __init__(self):
        self.document = Document()
    
    ######### put table in our document ##########
    def add_table(self, table):
        t = self.document.add_table(table.shape[0]+1, table.shape[1])
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.style='Table Grid' 

        # add the header rows.
        for j in range(table.shape[-1]):
            t.cell(0,j).text = table.columns[j]

        # add the rest of the data frame
        for i in range(table.shape[0]):
            for j in range(table.shape[-1]):
                t.cell(i+1,j).text = str(table.values[i,j])

        for row in t.rows:
            for cell in row.cells:
                paragraphs = cell.paragraphs
                for paragraph in paragraphs:
                    for run in paragraph.runs:
                        font = run.font
                        font.size= Pt(10)

    def basic_info(self, files, control_amount, treatment_amount):
        ######## title ########
        self.document.add_heading('【Voting Game】Data Analysis Report', level = 0)

        ######## basic information ########
        self.document.add_heading('Basic Information', level = 1)

        # today's date 
        date_p = self.document.add_paragraph()
        today = date.today()
        day = today.strftime("%B %d, %Y")
        date_p.add_run('Date: ').bold = True
        date_p.add_run(day)

        # the files we have used
        file_p = self.document.add_paragraph()
        file_p.add_run('Files: ').bold = True
        for idx in range(len(files)):
            if idx != len(files) - 1:
                file_p.add_run(files[idx] + ", ")
            else:
                file_p.add_run(files[idx])

        # Number of observations
        ct_p = self.document.add_paragraph()
        ct_p.add_run('Number of Observations: ').bold = True
        ct_p.add_run(f"{control_amount + treatment_amount} (Total), {control_amount} (Control), {treatment_amount} (Treatment)")
    
    def participants_distribution(self, distribution_table):
        ######### Distribution of Observations ########
        self.document.add_heading('Distribution of Observations', level = 1)
        distriInfo_p = self.document.add_paragraph()
        distriInfo_p.add_run('- Control/treatment group.')
        distriInfo_p.add_run('\n- Whether they are is large team or small team in two games.')
        self.add_table(distribution_table)
    
    def data_analysis(self, paired_table, largePq_int_all, largePq_int_sin, largePq_no_all, largePq_no_sin,
                      ct_wtp, sum_reg, sum_f, max_reg, max_f, min_reg, min_f):
        ######### Data Analysis ########
        self.document.add_heading('Data Analysis', level = 1)
        
        ##### paired t test
        self.document.add_heading('Election WTP v.s. Referendum WTP', level = 2)
        pairedT_p = self.document.add_paragraph()
        pairedT_p.add_run('- Use control group data only.')
        pairedT_p.add_run('\n- We implement paired t test for testing whether the mean difference between pairs of wtp and wtp_pq is zero under different grouping conditions')
        self.add_table(paired_table)
        
        ##### The interaction - is_large, is_pq
        space = self.document.add_paragraph()
        space.add_run(' ')        

        self.document.add_heading('The interaction effect between is_large and is_pq', level = 2)
        largePq_p = self.document.add_paragraph()
        largePq_p.add_run('- Use control group data only.')
        largePq_p.add_run('\n- Model: reg wtp is_pq is_large is_pq*is_large')
        largePq_p.add_run('\n- We also provide a model without interaction term.')
        
        space = self.document.add_paragraph()
        space.add_run(' ')

        self.document.add_heading('With interaction term - all players', level = 3)
        self.add_table(largePq_int_all)
        
        space = self.document.add_paragraph()
        space.add_run(' ')

        self.document.add_heading('With interaction term - single player', level = 3)
        largePq_sin_p = self.document.add_paragraph()
        largePq_sin_p.add_run('- If there are n players, then we run the regression n times.')
        largePq_sin_p.add_run('\n- The combinations of the signs of the coefficients and the number of people whose model satisfy the according condition.')
        self.add_table(largePq_int_sin)
        
        space = self.document.add_paragraph()
        space.add_run(' ')

        self.document.add_heading('Without interaction term - all players', level = 3)
        self.add_table(largePq_no_all)
        
        space = self.document.add_paragraph()
        space.add_run(' ')

        self.document.add_heading('Without interaction term - single player', level = 3)
        self.add_table(largePq_no_sin)
        
        ######### Control v.s. Treatment
        space = self.document.add_paragraph()
        space.add_run(' ')
        self.document.add_heading('Control Group WTP v.s. Treatment Group WTP', level = 2)
        ct_p = self.document.add_paragraph()
        ct_p.add_run('- Both of the control group data and treatment group data are used.')
        ct_p.add_run('\n- The WTP of control group is defined as the sum of the wtp in two games.')
        ct_p.add_run('\n- We implement unpaired t test to determine whether there is a significant difference between the WTP in two groups.')
        self.add_table(ct_wtp)
        
        ######### interaction: treatment, sb_condition
        space = self.document.add_paragraph()
        space.add_run(' ')
        
        self.document.add_heading('The interaction effect between treatment and sb_condition', level = 2)
        tr_sb_p = self.document.add_paragraph()
        tr_sb_p.add_run('- Both of the control group and treatment group data are used.')
        tr_sb_p.add_run('\n- Model: wtp treatment sb bs bb sb*treatment bs_treatment bb_treatment')
        tr_sb_p.add_run('\n- There are three modes to calculate WTP of control group: sum, max., and min. of two games.')
        
        space = self.document.add_paragraph()
        space.add_run(' ')        
        self.document.add_heading('Contorl group WTP = sum of a and b', level = 3)
        self.document.add_heading('Linear regression result', level = 4)
        self.add_table(sum_reg)
        self.document.add_heading('F test', level = 4)
        self.add_table(sum_f)
        
        space = self.document.add_paragraph()
        space.add_run(' ')
        self.document.add_heading('Contorl group WTP = max(a, b)', level = 3)
        self.document.add_heading('Linear regression result', level = 4)
        self.add_table(max_reg)
        self.document.add_heading('F test', level = 4)
        self.add_table(max_f)

        space = self.document.add_paragraph()
        space.add_run(' ')

        self.document.add_heading('Contorl group WTP = min(a, b)', level = 3)
        self.document.add_heading('Linear regression result', level = 4)
        self.add_table(min_reg)
        self.document.add_heading('F test', level = 4)
        self.add_table(min_f)
        
    def save_document(self):
        today = date.today()
        day = today.strftime("%B %d, %Y")
        fileName = day + "_report.docx"
        self.document.save(fileName)
        return fileName
