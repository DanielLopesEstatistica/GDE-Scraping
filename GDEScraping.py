from selenium import webdriver
import time
import re
import bs4

def get_score(soup, n):
    try:
        # find the span element with id="span_fixo_1_2"
        span_element = soup.find('span', {'id': f'span_fixo_1_{n+1}'})

        # extract the "nota" value from the span element
        nota = span_element.text.strip()
        nota = float(nota.replace(',', '.'))

        # extract the "votos" value from the span element
        votos = span_element.next_sibling.strip()[1:-1]
        votos = int(re.findall(r'\d+', votos)[0])
        
    except:
        nota = 0
        votos = 0
    
    return nota, votos

def get_att(soup):
    td_tags = soup.find_all('td')
    att_list = []
    values_list = []
    for k in range(len(td_tags)):
        table_name = td_tags[k].get_text().strip()
        if k%2 == 0:
            att_list.append(table_name[:-1])
        else:
            values_list.append(table_name)
    
    return att_list, values_list
        

# Configure the webdriver
driver = webdriver.Firefox()

# Define the URL to scrape
url = "https://sistemas.dac.unicamp.br/siga/nucleo/login.xhtml?gde=1"

driver.get(url)

username = "SeuUsername"
password = "SuaSenha"

time.sleep(1)
driver.find_element("xpath", "//input[@id='frmConteudo:txtFieldUsuario']").click()
driver.find_element("xpath", "//input[@id='frmConteudo:txtFieldUsuario']").send_keys(username)
driver.find_element("xpath", "//input[@id='frmConteudo:txtFieldSenha']").click()
driver.find_element("xpath", "//input[@id='frmConteudo:txtFieldSenha']").send_keys(password)
driver.find_element("xpath", "//input[@id='frmConteudo:buttonConfirmar']").click()

time.sleep(1)

for n in range(5438):
    try:
        url = f"https://grade.daconline.unicamp.br/perfil/?professor={n+1}"
        driver.get(url)
        time.sleep(1)
        driver.find_element("xpath", "//a[contains(@href, '#tab_avaliacao')]").click()
    
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        
        #id_list.append(n+1)
        
        score = get_score(soup, n)
        score_list.insert(0, score[0])
        votes_list.insert(0, score[1])
    
        table = get_att(soup)
        att_list.insert(0, table[0])
        values_list.insert(0, table[1])
        time.sleep(0.1)
        
    except:
        id_list.insert(0, n+1)
        score_list.insert(0, 0)
        votes_list.insert(0, 0)
        att_list.insert(0, 0)
        values_list.insert(0, 0)
        time.sleep(0.1)

driver.quit()

everything_list = [[id_list], [score_list], [votes_list], [att_list], [values_list]]

with open('everything.pickle', 'wb') as f:
    pickle.dump(everything_list, f)
    
att1 = []
att6 = []
att22 = []
att23 = []
att26 = []

for m in range(len(everything_list[0][0])):
    try:
        number = len(everything_list[3][0][m])
    except:
        number = 1
    this_id = everything_list[0][0][m]
    this_score = everything_list[1][0][m]
    this_votes = everything_list[2][0][m]
    this_att = everything_list[3][0][m]
    this_values = everything_list[4][0][m]
    total_row = [[this_id], [this_score], [this_votes], [this_att], [this_values]]
    if(number == 1):
        att1.append(total_row)
    if(number == 6):
        att6.append(total_row)
    if(number == 22):
        att22.append(total_row)
    if(number == 23):
        att23.append(total_row)
    if(number == 26):
        att26.append(total_row)

import pandas as pd

def turn_to_df(atts):
    # Loop over the list and create a DataFrame for each element
    dfs = []
    for lst in atts:
        lst = [lst]
        # Extract values from the list
        id_val = lst[0][0]
        nota_val = lst[0][1]
        votos_val = lst[0][2]
        columns = lst[0][3][0]
        values = lst[0][4][0]

        # Create a dictionary from the extracted values
        dict_values = {"id": id_val, "nota": nota_val, "votos": votos_val}
        for i in range(len(columns)):
            dict_values[columns[i]] = [values[i]]

        # Create a DataFrame from the dictionary
        df = pd.DataFrame.from_dict(dict_values)
        dfs.append(df)

    # Concatenate the DataFrames into a single DataFrame
    final_df = pd.concat(dfs, ignore_index=True)

    return final_df
    
df6 = turn_to_df(att6)
df22 = turn_to_df(att22)
df23 = turn_to_df(att23)
df26 = turn_to_df(att26)
merged_df = pd.concat([df6.iloc[:, :4], df22.iloc[:, :4], df23.iloc[:, :4], df26.iloc[:, :4]])
