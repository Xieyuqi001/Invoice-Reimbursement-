# 发票管理系统

一个简洁高效的发票和订单图片管理工具，帮助用户快速整理发票信息并生成可打印的PDF文件。

## 简介

本系统旨在解决发票报销流程中的整理问题。用户上传发票图片和订单图片，填写相关信息后，系统自动生成包含所有信息的PDF文件，方便打印和提交给财务部门。

**技术栈：**
- 后端：Python + FastAPI
- 前端：HTML + Tailwind CSS
- 数据库：SQLite
- PDF生成：ReportLab

## 功能说明

### 核心功能

| 功能 | 说明 |
|------|------|
| **图片上传** | 支持拖拽、点击选择、Ctrl+V 粘贴三种方式上传发票/订单图片 |
| **OCR识别** | 上传发票图片后自动识别发票号码，支持重新识别 |
| **信息录入** | 填写姓名、学号、发票号、课题组名称、对公/对私、其他信息 |
| **一键预设** | 保存常用信息，批量录入时一键填充，提高效率 |
| **PDF生成** | 自动生成包含文字信息和图片的PDF文件 |
| **预览/下载** | 支持浏览器预览PDF或直接下载 |
| **批量导出** | 一键导出所有记录为PDF压缩包或Excel汇总表 |
| **历史记录** | 保存所有录入记录，支持编辑和删除 |

### PDF输出格式

每份PDF包含2页：
- **第1页**：文字信息区（顶部）+ 发票图片
- **第2页**：订单图片（整页）

文件命名：`{发票号}.pdf`

## 使用流程

### 1. 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 设置预设（可选）

首次使用时，在"预设信息"区域填写常用信息：
1. 填写姓名、学号、课题组名称等
2. 点击"保存预设"
3. 后续录入时点击"一键填充预设"即可自动填充

### 3. 录入发票

1. 点击"一键填充预设"（如有预设）
2. 填写发票号（必填）
3. 上传发票图片和订单图片
4. 点击"保存记录"

### 4. 导出文件

- **单个PDF**：点击记录的"预览"或"下载"按钮
- **批量PDF**：点击"导出全部PDF"，下载ZIP压缩包
- **Excel汇总**：点击"导出Excel"，下载汇总表格

## 输入输出

### 输入

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 姓名 | 文本 | 是 | 报销人姓名 |
| 学号 | 文本 | 是 | 报销人学号 |
| 发票号 | 文本 | 是 | 发票唯一编号 |
| 课题组名称 | 文本 | 否 | 默认"丘陵课题组" |
| 对公/对私 | 选择 | 否 | 默认"对公" |
| 其他信息 | 文本 | 否 | 备注信息 |
| 发票图片 | 图片 | 是 | JPG/PNG格式 |
| 订单图片 | 图片 | 是 | JPG/PNG格式 |

### 输出

| 类型 | 格式 | 说明 |
|------|------|------|
| 单个PDF | PDF | 包含文字信息+发票图片+订单图片 |
| 批量PDF | ZIP | 所有记录的PDF打包 |
| Excel汇总 | XLSX | 所有记录的文字信息汇总表 |

## 项目结构

```
Fapiao/
├── app/
│   ├── main.py              # FastAPI 主应用
│   ├── models.py            # 数据库模型
│   ├── database.py          # 数据库配置
│   ├── schemas.py           # 数据验证模型
│   ├── config.py            # 配置文件（OCR密钥等）
│   ├── services/
│   │   ├── pdf_generator.py # PDF生成服务
│   │   └── ocr_service.py   # OCR识别服务
│   └── routers/
│       └── records.py       # API路由
├── static/
│   └── index.html           # 前端界面
├── uploads/                 # 上传的图片存储
├── exports/                 # 导出的文件
├── fapiao.db               # SQLite数据库
├── requirements.txt        # Python依赖
└── README.md               # 本文档
```

## API接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/records | 创建新记录 |
| GET | /api/records | 获取所有记录 |
| GET | /api/records/{id} | 获取单条记录 |
| PUT | /api/records/{id} | 更新记录 |
| DELETE | /api/records/{id} | 删除记录 |
| GET | /api/records/{id}/preview | 预览PDF（浏览器打开） |
| GET | /api/records/{id}/download | 下载PDF |
| GET | /api/export/all | 导出所有PDF（ZIP） |
| GET | /api/export/excel | 导出Excel汇总 |
| POST | /api/ocr/recognize | OCR识别发票号码 |
| GET | /api/ocr/status | 获取OCR服务状态 |

## OCR配置（可选）

系统支持发票号码自动识别功能，需要配置百度AI OCR服务：

### 获取百度AI API密钥

1. 访问 [百度AI开放平台](https://ai.baidu.com/)
2. 注册/登录账号
3. 创建应用，获取 `APP_ID`、`API_KEY`、`SECRET_KEY`
4. **重要**：在应用管理中开通以下服务：
   - ✅ **通用文字识别**
   - ✅ **增值税发票识别**
5. 编辑 `app/config.py`，填入密钥：

```python
BAIDU_OCR_APP_ID = "你的APP_ID"
BAIDU_OCR_API_KEY = "你的API_KEY"
BAIDU_OCR_SECRET_KEY = "你的SECRET_KEY"
```

### 免费额度

- 百度AI OCR提供 **1000次/天** 免费调用额度
- 足够日常使用

### OCR识别流程

```
上传发票图片 → 调用百度增值税发票识别API → 提取InvoiceNum字段 → 自动填充表单
```

如果增值税发票识别失败，系统会自动降级使用通用文字识别，通过正则匹配提取发票号。

## 更新说明

### v1.2.0 (当前版本)
- **新增**：OCR发票号自动识别功能
  - 集成百度AI OCR服务（增值税发票识别 + 通用文字识别）
  - 上传发票图片后自动识别发票号码
  - 识别结果自动填充到表单
  - 支持重新识别
  - 识别失败时提示用户手动输入
  - 智能降级：增值税发票识别失败时自动使用通用文字识别
- **新增**：OCR服务状态显示
  - 页面显示OCR服务是否可用
  - 识别过程实时状态反馈（识别中/已识别/识别失败）
- **新增**：配置文件 `app/config.py`
- **修复**：百度API返回格式兼容问题（InvoiceNum字段可能是字符串或字典）
- **依赖**：新增 `baidu-aip`、`chardet` 依赖

### v1.1.0
- **新增**：PDF中文显示支持（使用系统字体）
- **新增**：预览功能分离（预览用浏览器打开，下载触发保存）
- **新增**：字段扩展
  - 课题组名称（默认"丘陵课题组"）
  - 对公/对私（下拉选择）
  - 其他信息（文本框）
- **新增**：一键预设功能
  - 保存常用信息到浏览器本地存储
  - 一键填充预设值
  - 支持部分预设（留空字段不填充）

### v1.0.0 (初始版本)
- 基础功能：图片上传、信息录入、PDF生成
- 支持拖拽和粘贴上传图片
- 历史记录管理（编辑、删除）
- 批量导出PDF和Excel

### 待开发功能
- [ ] 按日期/姓名筛选记录
- [ ] 批量删除记录
- [ ] 自定义PDF模板
- [ ] 多语言支持

## 注意事项

1. **数据库迁移**：如果更新了数据库模型，需要运行迁移脚本或删除旧数据库
2. **浏览器兼容**：推荐使用Chrome、Edge等现代浏览器
3. **图片格式**：支持JPG、PNG格式，建议图片清晰度足够打印
4. **预设存储**：预设信息保存在浏览器本地，清除浏览器数据会丢失预设
5. **OCR服务开通**：创建百度AI应用后，必须手动开通「通用文字识别」和「增值税发票识别」服务，否则会报错 `No permission to access data`
6. **OCR依赖**：首次使用OCR功能前，需确保安装了 `baidu-aip` 和 `chardet` 依赖包

## 许可证

MIT License

---

## GitHub版本更新指南

### 如何获取最新版本

```bash
# 克隆仓库
git clone https://github.com/你的用户名/Fapiao.git

# 进入目录
cd Fapiao

# 安装依赖
pip install -r requirements.txt

# 复制配置文件模板
cp app/config.example.py app/config.py

# 编辑配置文件，填入你的百度AI密钥
# 然后启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 如何更新到最新版本

```bash
# 进入项目目录
cd Fapiao

# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 重启服务
```

### 版本更新流程（开发者）

如果你要更新代码并推送到GitHub：

```bash
# 1. 查看修改的文件
git status

# 2. 添加修改的文件
git add .

# 3. 提交修改（写清楚更新内容）
git commit -m "feat: 添加XXX功能"

# 4. 推送到GitHub
git push origin main
```

**提交信息规范：**

| 前缀 | 说明 |
|------|------|
| `feat:` | 新功能 |
| `fix:` | 修复bug |
| `docs:` | 文档更新 |
| `style:` | 代码格式调整 |
| `refactor:` | 代码重构 |
| `chore:` | 构建/工具更新 |

### 数据迁移

如果更新涉及数据库结构变化：

1. 备份数据：`cp fapiao.db fapiao.db.backup`
2. 拉取代码：`git pull`
3. 运行迁移脚本（如有）
4. 重启服务
