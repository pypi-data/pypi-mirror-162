import pandas as pd
import os
def merge(dir,new_filepatch):
    # 新建列表，存放文件名
    filename_excel = []
    # 新建列表，存放每个文件数据框
    frames = []
    # root 所指的是当前正在遍历的这个文件夹的本身的地址
    # dirs 是一个 list ，内容是该文件夹中所有的目录(即子文件夹的名字)的名字(不包括子目录)
    # files 同样是 list, 内容是该文件夹中所有的文件(不包括子目录)
    for root, dirs, files in os.walk(dir):
        for file in files:
            filename_excel.append(os.path.join(root, file))
            df = pd.read_excel(os.path.join(root, file))  # excel转换成DataFrame
            frames.append(df)
    # print(filename_excel)
    result = pd.concat(frames)
    # print(result)
    result.to_excel(new_filepatch)