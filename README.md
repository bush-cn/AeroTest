# AeroTest航宇智测

[前端仓库](https://github.com/pizza2k/unitTest.git)

## 使用
首先安装依赖：
```bash
pip install -r requirements.txt
```

配置`DEEPSEEK_API_KEY`环境变量：
```bash
export DEEPSEEK_API_KEY=your_api_key  # Linux
$env:DEEPSEEK_API_KEY=your_api_key  # Windows PowerShell
```

在`config.py`中配置仓库路径等参数。

### 命令行运行
`-r`表示开启参照分析。
```bash
python run.py <fucntion_name> <file_name> [-r]  
```

### 可视化运行
```bash
python app.py 
```
然后按提示打开`localhost:5000`进入可视化界面。