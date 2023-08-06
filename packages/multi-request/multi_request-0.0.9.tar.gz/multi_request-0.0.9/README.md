
## 说明
**本包用于使用多线程调接口保存结果**

如果你有很大量的数据需要调用你的某个接口，然后把结果保存到文件， 这个包可以提供一个封装好的类，简化多线程的编写，
并能按任意设定值把结果拆分保存到文件。只需编写针对单次调用的输入输出转换函数。

- 输入：pandas DataFrame 格式的原始数据，每一行可用于构造一次请求的参数
- 输出：文件支持fth, csv, xlsx三种格式， 默认保存在当前目录下的data目录


## 示例

#### 1. 准备数据和函数
```python
# a. 输入数据 df (DataFrame格式)
## df的每一行是一次请求需要的原始数据

# b. 处理单次输入的函数
import json
def makeReqData(json_str):
    # json_str: row.to_json() df的一行数据
    # TODO: 使用json_str生成请求参数
    json_str = json.loads(json_str)
    return json_str

# c. 处理单次输出的函数
def makeResult(r):
    # r: res.json(), 接口返回的json
    # TODO: 选取需要保存的字段, 保存为新的dict, 用于写到文件
    data = r.get("data")
    return data
```


#### 2. 多线程调用接口保存文件


```python
# 方法一
from multi_request import mreq

m = mreq.MultiRequest()
m.url = "http://127.0.0.1:8080/xxx"  # 请求接口, 目前只支持 POST 方法
m.makeReqData = makeReqData  # 你的生成单次请求数据的函数
m.makeResult = makeResult  # (可选) 处理单次返回数据的函数, 生成最终结果字典
m.input_data = df  # 原始请求数据， pandas的 DataFrame 格式
m.parallel_batch_size = 20  # (可选) 并发数，默认: 100
m.save_batch_size = 12  # (可选) 每几个保存一个文件，默认: 5000
m.res_format = "fth"  # (可选) 默认: fth, 支持格式: fth, csv, xlsx
m.res_dir = "data"  # (可选) 保存结果的目录, 默认: ./data
m.run()
```


```python
# 方法二
from multi_request import mreq

params = {
    "url": "http://127.0.0.1:8080/xxx",
    "makeReqData": makeReqData,
    "makeResult": makeResult,
    "input_data": df,
    "parallel_batch_size": 20,
    "save_batch_size": 8,
    "res_format": "csv",
    "res_dir": "tmp_csv",
}
m = mreq.MultiRequest(**params)
m.run()
```


```python
# 使用默认参数
from multi_request import mreq

params = {
    "url": "http://127.0.0.1:8080/xxx",
    "makeReqData": makeReqData,
    "input_data": df,
}
m = mreq.MultiRequest(**params)
m.run()
```


