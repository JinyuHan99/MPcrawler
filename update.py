import os
import json
from pymatgen.ext.matproj import MPRester  # 用来爬取MP网站


key_word = 'Ni-O'  # 查询式
API_KEY = 'NXLXwuF4n9BAN7x0HVm'  # Materialsproject账号的API
with MPRester(API_KEY) as m:
    entries = m.get_data(key_word,prop='material_id')
    oxide_mp_ids = [e['material_id'] for e in entries]
# 找出没有的材料编号
with open('oxide_mp_ids.json', 'r') as f:
    old_mp_ids = json.load(f)
    new_mp_ids = list(set(oxide_mp_ids) - set(old_mp_ids)) # set()函数创建一个无序不重复元素集，可进行关系测试，删除重复数据，还可以计算交集、差集、并集等
# 查询新材料的cif文件
new_data = m.query({"material_id": {"$in": new_mp_ids}}, ["material_id", "formula", "cif"])
# 将新材料cif写入文件
formula_list = [d['formula'] for d in new_data]

for i, formula in enumerate(formula_list):
    formula = dict(sorted(formula.items(), key=lambda e: e[0]))
    # 提取出化学式作为文件名
    formula_name = ''
    for key, value in formula.items():
        formula_1 = '{}{}'.format(key, int(value))
        formula_name = formula_name + formula_1
    # 以化学式为文件名创建文件夹
    if not os.path.exists('mp_oxide_cifs/{}'.format(formula_name)):
        os.mkdir("mp_oxide_cifs/{}".format(formula_name))
    # 在相应文件夹下写入cif文件
    spacegroup = str(new_data[i]['spacegroup']['symbol']).replace("/", "_")
    id = new_data[i]['material_id']
    if not os.path.exists('mp_oxide_cifs/{}/{}'.format(formula_name, spacegroup)):
        os.mkdir('mp_oxide_cifs/{}/{}'.format(formula_name, spacegroup))
    with open("mp_oxide_cifs/{}/{}/{}.cif".format(formula_name, spacegroup, id), 'w') as f:
        f.write(new_data[i]["cif"])

#追加编号文件
with open('oxide_mp_ids.json', 'r') as f:
    list1 = json.load(f)
    list1.extend(oxide_mp_ids)  # append将列表作为整体添加，extend添加单个元素
with open('oxide_mp_ids.json', 'w') as f:
    json.dump(list1,f)

