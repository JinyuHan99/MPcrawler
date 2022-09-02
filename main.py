import json
from pymatgen.ext.matproj import MPRester  # 用来爬取MP网站
from tqdm import tqdm  # 添加进度条显示
from itertools import zip_longest # 迭代器，交替打印可迭代值。如果iterables中的一个被完全印刷，剩余的值由分配给值填充fillvalue参数。
import os


if __name__ == '__main__':
    #创建用于分组的函数
    def grouper(iterable,n,fillvalue=None):
        args = [iter(iterable)]*n
        return zip_longest(*args,fillvalue=fillvalue) # 通过 zip(*[iter(s)]*n) 这样的惯用形式将一系列数据聚类为长度为 n 的分组
    # 使用api查询材料编号

    # 创建文件夹
    dir_name = 'quaternary_cifs' # 存放目录
    API_KEY = 'NXLXwuF4n9BAN7x0HVm'  # Materialsproject账号的API
    with MPRester(API_KEY) as m:
        entries = m.query({"elements":{"$nin":["S","H","B","C","N","F","Si","P","Cl","As","Se","Br","Te","I","At","Ts","Og"],"$in":["Sc","Fe","Cu",""], "$all": ["O"]}, "nelements":4},["material_id"])
        # print(entries)
        print("id数目："+str(len(entries)))
        oxide_mp_ids = [e['material_id'] for e in entries]  # entries结构[{'materials_id':'mp-760084'},{}……]，取出id并保存
        # [f(i) for i in range()] ：  将range（）内的i做f(i)处理后以列表形式储存
    data = []
    mp_id_groups = [g for g in grouper(oxide_mp_ids,1000)]  # 是每组1000个的分组

    #将编号写入文件
    with open('{}.json'.format(dir_name), 'w') as f:
        json.dump(oxide_mp_ids, f)
    # print(mp_id_groups)

    # 对于每一个材料id查询cif文件并保存在列表中
    for group in tqdm(mp_id_groups):
        mp_id_list =  list(filter(None,group))   # filter对象不能被json序列读取，因此需要转换为list
        # filter() 函数用于过滤序列，过滤掉不符合条件的元素，返回由符合条件元素组成的新列表。该接收两个参数，第一个为函数，第二个为序列，序列的每个元素作为参数传递给函数进行判断，然后返回 True 或 False，最后将返回 True 的元素放到新列表中
        # 函数进行数据过滤空值None, 默认会把0、false这样具体的值过滤掉
        entries = m.query({"material_id":{"$in":mp_id_list}},["material_id","cif"])
        #,"formula","spacegroup","formula","spacegroup","band_gap","density","volume","formation_energy_per_atom","magnetism"
        data.extend(entries)

    a = data
    data1 = data

    # print(data)

    for i in range(len(data1)):
        data1[i]["magnetic_ordering"] = data[i]["magnetism"]["ordering"]
        data1[i]['spacegroup_symbol'] = data[i]['spacegroup']['symbol']
        del data1[i]["magnetism"]
        del data1[i]['spacegroup']
        print(data1)



    # print(data)
    # print(data1)



    print("cif文件数目："+str(len(data1)))
    dir_name1 = 'properties_4_elements_cif'
    with open('{}.json'.format(dir_name1), 'w') as f:
        json.dump(data1, f)

    # 创建目录
    if not os.path.exists(dir_name):
        os.mkdir('{}'.format(dir_name))

    # 统计有哪些氧化物的化学式相同，创建文件夹，将相应的cif保存在同一个文件夹内
    formula_list = [d['formula'] for d in data]
    for i,formula in enumerate(formula_list):
        formula = dict(sorted(formula.items(), key=lambda e: e[0])) # e表示dict.items()中的一个元素，e[0]表示按键排序，e[1]则表示按值排序。reverse=False可以省略，默认为升序排列

        # 提取出化学式作为文件名
        formula_name = ''
        for key,value in formula.items():
            formula_1 = '{}{}'.format(key,int(value))
            formula_name = formula_name + formula_1
        # print(formula_name)

        # 以化学式为文件名创建文件夹
        if not os.path.exists('{}/{}'.format(dir_name,formula_name)):
            os.mkdir("{}/{}".format(dir_name,formula_name))

        # 在相应文件夹下写入cif文件
        spacegroup = str(data[i]['spacegroup']['symbol']).replace("/","_")
        id = data[i]['material_id']
        if not os.path.exists('{}/{}/{}'.format(dir_name,formula_name,spacegroup)):
            os.mkdir('{}/{}/{}'.format(dir_name,formula_name,spacegroup))
        with open("{}/{}/{}/{}.cif".format(dir_name,formula_name,spacegroup,id), 'w') as f:
            f.write(data[i]["cif"])















