import re

def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

def find_line_number(file_name, search_str):
    lines = open(file_name, 'r').readlines()
    for line_num in range(len(lines)):
        text = lines[line_num]
        if re.search(search_str,text):
            return line_num

def version_num_calculate(version_str):
    if version_str.find('\"')>-1:
        start_num = version_str.find('\"')+1
    if version_str.find('\"',start_num)>-1:
        end_num = version_str.find('\"',start_num)
    version_info = version_str[start_num:end_num]
    n = re.search('[1-9]',version_info)
    num_idexes = n.span()[0]
    verion_num = int(version_info[num_idexes:].replace('.',''))
    new_verion_num = str(verion_num+1)
    tempt = ''
    for i in new_verion_num:
        tempt += i
        tempt +='.'
    tempt = tempt[:-1]
    new_version_info =version_info.replace(version_info[num_idexes:],tempt)
    print('From version',version_info,'update to',new_version_info)
    new_version_str = version_str.replace(version_info,new_version_info)
    return new_version_str

# a = "    version=\"0.1.0\","
def get_line_string(file_name,line_num):
    lines = open(file_name, 'r').readlines()
    return lines[line_num]

verion_line_num = find_line_number(file_name = 'pyproject.toml',search_str = 'version =')
print(verion_line_num)
verion_info = get_line_string(file_name = 'pyproject.toml',line_num=verion_line_num)
print(verion_info)
new_verion_info =version_num_calculate(verion_info)
replace_line(file_name = 'pyproject.toml',line_num=verion_line_num, text=new_verion_info)
