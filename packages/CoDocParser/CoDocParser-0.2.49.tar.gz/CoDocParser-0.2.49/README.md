# 文档解析器器

cots.document.parser 是一个文档解析器，现支持pdf,txt,html,excel,项目的目录结构如下。

## 目录结构

```
├── docparser                   # 文档解析源码
│   ├── config                             # 解析配置项目录
│   ├── core                               # 解析器抽象定义
│   ├── extends                            # 自定义扩展
│   ├── implements                         # 解析器实现
├── docs                        # 文档
├── tests                       # 测试示例文件
```

## 发布

```
# 生成依赖清单
pip freeze > requirements.txt

# 根据依赖清单安装环境
pip install -r requirements.txt


# 
pip install --user --upgrade setuptools wheel

# 本地安装
python setup.py install

# 构建输出
python setup.py sdist

#上传包
twine upload --username Admin --password Admin --repository-url http://nuget.cityocean.com/pypi/COMS-Pypi/legacy dist/*

#安装包
 
pip install cots_document_converter -i http://nuget.cityocean.com/pypi/COMS-Pypi/simple --trusted-host nuget.cityocean.com

```
