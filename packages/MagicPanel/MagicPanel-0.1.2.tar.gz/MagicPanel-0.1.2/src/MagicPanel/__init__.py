# Project:          MagicPanel
# Author:           Yifan Zhang (Peking University)
# Email:            zyfcode@outlook.com
# Latest update:    2022-04-26

import csv
from os.path import join

# 定义类：「准面板」。
class QuasiPanel:
    def __init__(self, contents=[[]]):
        self.__contents = contents

    # 制备一个面板的框架。
    def __make_panel_frame(self, units, time):
        # units是一个列表，包含所有样本名称（如国家名）。
        # time是一个二元列表，包含时间线的起止年份。
        # 返回值是一个列表。
        panel_frame = [["unit", "time"]]
        for unit in units:
            for timepoint in range(time[0], time[1] + 1):
                panel_frame.append([unit, timepoint])
        return panel_frame

    # 提取原矩阵的部分列，返回子矩阵。
    # 如果输入重复的index，则会出现重复的列。
    def __get_sub_matrix(self, matrix, col_nums=[0]):
        sub_matrix = []
        for row in matrix:
            sub_matrix.append([])
            for j in col_nums:
                if j in range(len(matrix[0])):
                    sub_matrix[-1].append(row[j])
        return sub_matrix

    # 定位单元格。
    def __locate(self, unit, year, var):
        # 只对已经符合面板数据格式规范的矩阵适用。
        # 返回值是坐标。
        matrix = self.contents()
        vars = matrix[0]
        for i in range(len(matrix)):
            if matrix[i][0] == unit and matrix[i][1] == year:
                for j in range(len(vars)):
                    if var == vars[j]:
                        return i, j
        return None, None

    # 提取准面板内容，返回值为矩阵。
    def contents(self):
        return self.__contents

    # 从csv文件导入矩阵。
    def import_from_csv(self, path: str, filename: str, encoding: str="utf-8", optimize: bool=True):
        # 为什么不用pandas：读取大型csv文件时，pandas容易出现DtypeWarning。
        with open(join(path, filename + ".csv"), encoding=encoding) as f:
            csv_reader = csv.reader(f)
            data = list(csv_reader)
        # 当开启格式优化选项时，进行优化。
        if optimize:
            # 删去矩阵末尾的空行。
            while len(data) > 0:
                is_null = True
                if len(data[-1]) != 0:
                    for cell in data[-1]:
                        if len(cell) > 0:
                            is_null = False
                            break
                if is_null:
                    del data[-1]
                else:
                    break
            # 如果各行长度不相等，用空字符串补齐较短的行。
            length = [len(line) for line in data]
            if max(length) != min(length):
                for line in data:
                    if len(line) != max(length):
                        for i in range(max(length) - len(line)):
                            line.append("")
            # 如果每行（包括索引行）末尾都有空字符串，则删去。
            is_null = True
            while is_null:
                for line in data:
                    if len(line[-1]) != 0:
                        is_null = False
                if is_null:
                    for line in data:
                        del line[-1]
        self.__contents = data
        return self

    # 对横向的准面板进行标准化。
    def standardize_hor(self, index_row: int=0, unit_col: int=0, var_col=1, var_name="", first_time_col: int=2):
        # 引入数据，去掉表头之前的行。
        matrix = self.contents()
        matrix = matrix[index_row:]
        # 获取起止时间点。
        start_timepoint = int(matrix[0][first_time_col])
        for col in range(-1, -len(matrix[0]), -1):
            if matrix[0][col] != "":
                end_timepoint = int(matrix[0][col])
                break
        # 获取样本名称列表。
        units = list(set(row[unit_col] for row in matrix[1:] if len(row) > 0))
        # 获取变量名称列表。
        if var_col == None:
            varlist = [var_name]
        else:
            varlist = list(set(row[var_col] for row in matrix[1:] if len(row) > 0))
        # 制备面板框架。
        panel_frame = self.__make_panel_frame(units=units, time=[start_timepoint, end_timepoint])
        # 向面板框架内填充数据。
        for varname in varlist:
            panel_frame[0].append(varname)
            # 对每一个“样本-时间点”进行查找。
            for row in panel_frame[1:]:
                unit, timepoint = row[0], row[1]
                # 确定年份。
                for i in range(len(matrix[0])):
                    if matrix[0][i] == str(timepoint):
                        this_timepoint_col = i
                # 如果原始数据里没有变量名。
                if var_col == None:
                    for ori_row in matrix:
                        if ori_row[unit_col] == unit:
                            the_value = ori_row[this_timepoint_col]
                            break
                        # 如果找不到（理论上似乎不可能），则填充空字符串。
                        the_value = ""
                # 如果原始数据里有变量名。
                else:
                    for ori_row in matrix:
                        if ori_row[unit_col] == unit and ori_row[var_col] == varname:
                            the_value = ori_row[this_timepoint_col]
                            break
                        the_value = ""
                row.append(the_value)
        self.__contents = panel_frame
        return self

    # 对纵向的准面板进行标准化。
    def standardize_ver(self, index_row: int=0, unit_col: int=0, time_col: int=1, first_var_col: int=2):
        # 引入数据，去掉表头之前的行。
        matrix = self.contents()
        matrix = matrix[index_row:]
        # 指定要提取的行号。
        col_nums = [unit_col, time_col]
        for i in range(first_var_col, len(matrix)):
            col_nums.append(i)
        # 提取子矩阵。
        sub_matrix = self.__get_sub_matrix(matrix=matrix, col_nums=col_nums)
        self.__contents = sub_matrix
        return self

    # 处理政策数据。
    def standardize_policy(self, start, end, mode: str="sync", varname: str="", treat_time=0):
        # 第一行是索引，第二行开始是数据。
        # 提取所有国家/地区名，制作面板框架，并加入新的一列。
        matrix = self.contents()
        units = list(set(row[0] for row in matrix[1:] if len(row) > 0))
        panel_frame = self.__make_panel_frame(units, [start, end])
        if varname != "":
            panel_frame[0].append(varname)
            for i in range(1, len(panel_frame)):
                panel_frame[i].append("")
        self.__contents = panel_frame

        # 处理同时施行的政策。
        if mode == "sync":
            for row in matrix[1:]:
                unit = row[0]
                treated = int(row[1])
                if treated:
                    for tp in range(start, treat_time):
                        j, k = self.__locate(unit, tp, varname)
                        panel_frame[j][k] = "0"
                    for tp in range(treat_time, end + 1):
                        j, k = self.__locate(unit, tp, varname)
                        panel_frame[j][k] = "1"
                else:
                    for tp in range(start, end + 1):
                        j, k = self.__locate(unit, tp, varname)
                        panel_frame[j][k] = "0"

        # 处理不同时施行的政策。
        elif mode == "diac":
            for row in matrix[1:]:
                unit = row[0]
                treated = True
                if row[1] == "":
                    treated = False
                if treated:
                    for tp in range(start, int(row[1])):
                        j, k = self.__locate(unit, tp, varname)
                        panel_frame[j][k] = "0"
                    for tp in range(int(row[1]), end + 1):
                        j, k = self.__locate(unit, tp, varname)
                        panel_frame[j][k] = "1"
                else:
                    for tp in range(start, end + 1):
                        j, k = self.__locate(unit, tp, varname)
                        panel_frame[j][k] = "0"

        # 处理复杂的政策数据。
        elif mode == "complex":
            # 添加变量。
            for var in matrix[0][2:]:
                panel_frame[0].append(var)
                for row in panel_frame[1:]:
                    row.append("")
            # 填补空缺时间点的变量值。
            for unit in units:
                # 确定时间节点。
                tps = []
                data = []
                for row in matrix[1:]:
                    if row[0] == unit:
                        tps.append(int(row[1]))
                        data.append(row[2:])
                tps.append(end + 1)
                # 写入数据。
                for i in range(len(tps) - 1):
                    row_data = data[i]
                    for tp in range(tps[i], tps[i + 1]):
                        for row in panel_frame[1:]:
                            if row[0] == unit and str(row[1]) == str(tp):
                                row[2:] = row_data

        # 处理多次变化的政策。
        # 该选项现已停用。
        elif mode == "unstable":
            # 第一列是国家/地区名，第二列起按照变量值、时间点、变量值、时间点、……交替，最后一列是变量值。
            for row in matrix[1:]:
                unit = row[0]
                # 清除行末空值。
                # row_contents的长度一定是偶数。
                row_contents = [item for item in row if item != ""]
                # 分离出所有时间点和所有变量值。
                timepoints = [start] + [int(row_contents[2 * n]) for n in range(1, int(len(row_contents) / 2))] + [end]
                values = [row_contents[2 * n + 1] for n in range(int(len(row_contents) / 2))]
                # 写入每个时间点对应的变量值。
                for i in range(len(timepoints) - 1):
                    for tp in range(timepoints[i], timepoints[i + 1]):
                        j, k = self.__locate(unit, tp, varname)
                        panel_frame[j][k] = values[i]
                # 补上最后一个时间点的变量值。
                j, k = self.__locate(unit, end, varname)
                panel_frame[j][k] = values[-1]
        else:
            return None
        self.__contents = panel_frame
        return self

    # 导出为Panel类的实例
    def gen_panel(self):
        matrix = self.contents()
        panel = Panel()._force(matrix)
        return panel

# 定义类：「面板」
class Panel:
    def __init__(self, units: dict={"country": ["Aruba"]}, time: dict={"year": [2001, 2022]}):
        # 根据传入的初始数据，生成一个面板框架
        index_unit = list(units.keys())[0]
        index_time = list(time.keys())[0]
        panel_frame = [[index_unit, index_time]]
        for unit in units[index_unit]:
            for timepoint in range(time[index_time][0], time[index_time][1] + 1):
                panel_frame.append([unit, timepoint])
        self.__contents = panel_frame

    # 提取原矩阵的部分列，返回子矩阵。
    def __get_sub_matrix(self, matrix, col_nums=[0]):
        sub_matrix = []
        for row in matrix:
            sub_matrix.append([])
            for j in col_nums:
                if j in range(len(matrix[0])):
                    sub_matrix[-1].append(row[j])
        return sub_matrix
    
    # 用新数据强行覆盖面板原内容，新数据的格式必须规范。
    # 强烈不建议外部调用该函数。
    def _force(self, matrix):
        self.__contents = matrix
        return self

    # 提取面板内容，返回值为矩阵。
    def contents(self):
        return self.__contents
    
    # 提取所有样本名称。
    def units(self):
        units = list(set(row[0] for row in self.contents()[1:] if len(row) > 0))
        units.sort()
        return units

    # 提取所有时间点。
    def time(self):
        times = list(set(row[1] for row in self.contents()[1:] if len(row) > 0))
        times.sort()
        return times

    # 提取所有变量名（表头的各项）。
    def variables(self):
        vars = self.contents()[0]
        return vars

    # 返回变量名对应的列号。
    def get_var_col(self, varname: str):
        varlist = self.variables()
        for i in range(len(varlist)):
            if str(varlist[i]) == varname:
                return i
        return None

    # 提取面板中指定样本在指定时间点的指定变量值的坐标。
    def locate(self, unit: str, timepoint, var: str):
        matrix = self.contents()
        vars = matrix[0]
        for i in range(len(matrix)):
            if matrix[i][0] == unit and str(matrix[i][1]) == str(timepoint):
                for j in range(len(vars)):
                    if var == vars[j]:
                        return i, j
        return None, None

    # 提取面板中指定样本在指定时间点的指定变量值。
    def get(self, unit: str, timepoint, var: str):
        location = self.locate(unit, timepoint, var)
        if location != None:
            i, j = location
            return self.contents()[i][j]
        return None

    # 改写指定单元格的值。
    def change(self, unit: str, timepoint, var: str, value: str):
        location = self.locate(unit, timepoint, var)
        if location != None:
            i, j = location
            self.__contents[i][j] = value
        return self

    # 添加一个新变量。
    def add_var(self, varname: str):
        matrix = self.contents()
        matrix[0].append(varname)
        for row in matrix[1:]:
            row.append("")
        self.__contents = matrix
        return self

    # 合并进来一个新的面板。
    def absorb(self, new_panel: "Panel", mode: str="new", mapping: dict={}):
        matrix = self.contents()
        new_matrix = new_panel.contents()
        num_of_vars = len(new_matrix[0])

        if mode == "new":
            # new_matrix第1列是单位，第2列是年份，后面是新变量。
            # warnings = []
            for i in range(2, num_of_vars):
                for old_row in matrix:
                    old_row.append("")
                varname = new_matrix[0][i]
                matrix[0][-1] = varname
                for row in new_matrix[1:]:
                    location = self.locate(row[0], row[1], varname)
                    if location[0] == None:
                        pass
                        # warnings.append("警告：%s %d 超出数据库定义范围。" % (row[0], row[1]))
                    else:
                        j, k = location
                        matrix[j][k] = row[i]
            # for warning in list(set(warnings)):
                # print(warning)

        # 只补充母数据库里为缺失值的样本。
        # 待优化：增加一个append_mark，方便用户进一步处理。
        elif mode == "complementary":
            for old_var in mapping.keys():
                new_var = mapping[old_var]
                old_col = self.get_var_col(old_var)
                new_col = new_panel.get_var_col(new_var)
                if old_col == None or new_col == None:
                    pass
                else:
                    for row in matrix[1:]:
                        value = row[old_col]
                        # 如果是缺失值，则进行替换。
                        if value == "":
                            j, k = new_panel.locate(unit=row[0], timepoint=row[1], var=new_var)
                            # 如果新数据里也没有这一项，则还是跳过。
                            if j == None:
                                pass
                            else:
                                new_value = new_matrix[j][k]
                                row[old_col] = new_value
                        else:
                            pass
        self.__contents = matrix
        return self

    # 提取子数据集。
    # 可以优化（用var_col）。
    def extract(self, varlist: list):
        index = [0, 1]
        for i in range(len(self.variables())):
            if self.variables()[i] in varlist:
                index.append(i)
        sub_matrix = self.__get_sub_matrix(self.contents(), col_nums=index)
        sub_panel = Panel()._force(sub_matrix)
        return sub_panel

    # 从csv文件中获取同义词词典。
    def get_syn_from_csv(path: str, filename: str, encoding: str="utf-8"):
        with open(join(path, filename + ".csv"), encoding=encoding) as f:
            csv_reader = csv.reader(f)
            matrix = list(csv_reader)
        synonyms = {}
        # 遍历第2列以后的列。
        for row in matrix[1:]:
            if len(row) > 0:
                for cell in row[1:]:
                    if cell != "":
                        synonyms[cell] = row[0]
        return synonyms

    # 将样本名称中的同义词进行统一。
    def paraphrase(self, synonyms: dict):
        matrix = self.contents()
        for row in matrix[1:]:
            if row[0] in synonyms.keys():
                row[0] = synonyms[row[0]]
        self.__contents = matrix
        return self

    # 排序。
    def sort(self, varlist: list=[], reverse=False):
        matrix = self.contents()
        index = matrix[:1]
        values = matrix[1:]
        # 默认按样本名称和时间排序。
        values = sorted(values, key=lambda row: int(row[1]), reverse=reverse)
        values = sorted(values, key=lambda row: row[0], reverse=reverse)
        # 继续按照用户指定顺序排序。
        if varlist != []:
            # 判断一个变量的所有非空单元格都能转化成浮点数。
            def __is_float(varname):
                sub_panel = self.extract([varname])
                values = [row[2] for row in sub_panel.contents()[1:]]
                for value in values:
                    if value != "":
                        try:
                            value = float(value)
                        except Exception:
                            return False
                return True
            # 将非空单元格转化为对应浮点数。
            # 空单元格返回无穷大，这样缺失值就会排在最后面。
            def __gen_float(value):
                if value == "":
                    value = float("inf")
                else:
                    value = float(value)
                return value
            # 把用户输入的优先级顺序反过来。
            # 按优先级从低到高逐次排序，这样才能达到想要的效果。
            varlist = varlist[::-1]
            for var in varlist:
                col = self.get_var_col(var)
                if col != None:
                    if __is_float(var):
                        values = sorted(values, key=lambda row: __gen_float(row[col]), reverse=reverse)
                    else:
                        values = sorted(values, key=lambda row: row[col], reverse=reverse)
        matrix = index + values
        self.__contents = matrix
        return self

    # 导出csv文件。
    def export(self, path: str, filename: str, encoding: str="utf-8"):
        with open(join(path, filename + ".csv"), "w+", newline="", encoding=encoding) as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows(self.contents())
        return self
