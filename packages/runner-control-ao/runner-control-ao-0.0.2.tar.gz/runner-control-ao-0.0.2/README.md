# runner-control-ao

定义runner接口类。

# 打包上传
```bash
python3 -m pip install --upgrade setuptools wheel twine build

python3 -m build

python3 -m twine upload dist/*
```
# 下载使用
```bash
pip install email_control_ao
```
```python
import runner_control_ao
```