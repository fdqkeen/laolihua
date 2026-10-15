# 银发中国 · 数说老龄化 —— Streamlit 部署包

> 中国人口老龄化与养老资源交互式数据可视化作品（Python + Streamlit + Plotly）
> 2026 年第十四届全国大学生数字媒体科技作品及创意竞赛 · 数字艺术与可视化设计类赛项

本部署包为**自包含**结构：数据层（`data.py`）、可视化主程序（`streamlit_app.py`）与依赖清单均已内置，
无需任何外部数据文件即可运行。所有数据均来自国家统计局、民政部等公开渠道，并在「数据说明」页逐条披露。

---

## 一、目录结构

```
部署包/
├── streamlit_app.py        # 可视化主程序（Streamlit 入口）
├── data.py                 # 数据层（全部指标与来源元数据，无需外部文件）
├── requirements.txt        # Python 依赖
├── .streamlit/
│   └── config.toml         # Streamlit 基础配置（端口 / 主题 / 无埋点）
├── start.bat               # Windows 一键启动脚本
├── start.sh                # Linux / macOS 启动脚本
├── Dockerfile              # 容器化部署
└── README.md               # 本说明
```

---

## 二、本地运行（最常用）

### 方式 A：Windows 一键启动
双击 `start.bat`，脚本会自动安装依赖并启动服务，结束后浏览器访问：
```
http://localhost:8501
```

### 方式 B：命令行启动（Windows / macOS / Linux）
```bash
# 1) 建议新建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 2) 安装依赖（国内推荐清华镜像）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3) 启动
streamlit run streamlit_app.py --server.port 8501
```
启动后终端会显示本地访问地址（默认 `http://localhost:8501`）。

---

## 三、部署到公网（供评委访问）

### 方案 1：Streamlit Community Cloud（免费，推荐）
1. 将本部署包全部文件上传到 **GitHub 公开仓库**（保持目录结构不变）；
2. 打开 https://streamlit.io/cloud ，用 GitHub 登录；
3. 点击 **New app** → 选择仓库 → 入口文件填 `streamlit_app.py`；
4. 点击 **Deploy**，等待构建完成即可获得形如 `https://xxx.streamlit.app` 的公网地址；
5. 后续更新代码只需 `git push`，平台自动重新部署。

> 该平台免费额度足以支撑竞赛展示与评审访问，无需信用卡。

### 方案 2：Docker 容器部署（云服务器 / 内网）
```bash
docker build -t yinfa-china:latest .
docker run -d -p 8501:8501 --name yinfa yinfa-china:latest
```
访问 `http://<服务器公网IP>:8501`。如需域名与 HTTPS，可在前面加一层 Nginx 反向代理。

### 方案 3：传统云服务器（PythonAnywhere / 阿里云 / 腾讯云等）
1. 上传本包到服务器；
2. 安装依赖：`pip install -r requirements.txt`；
3. 以守护进程方式运行（推荐 `nohup` 或 `screen`）：
   ```bash
   nohup streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 > app.log 2>&1 &
   ```
4. 在云厂商控制台**放行 8501 端口**（入站安全组），即可通过 `http://<公网IP>:8501` 访问。

---

## 四、交互说明

页面左侧为**交互控制台**，可实时调整：
- **年份区间**：控制图 1（老龄化进程）的观察窗口；
- **高亮省份**：在图 6（31 省方格地图）中框选某一省份；
- **排名范围**：切换图 7 显示「全部 / 前 10 / 后 10」省份。

左侧「章节导航」可点击跳转，右下角「回到顶部」便于长页浏览。
全部交互仅改变观察窗口，不改变数据口径与结论。

---

## 五、数据来源与合规声明

- 全部指标取自国家统计局《国民经济和社会发展统计公报》《中国统计年鉴 2025》、
  第七次全国人口普查公报、民政部《民政事业发展统计公报》等官方公开资料，逐项在「数据说明」页注明来源与口径。
- 派生指标（如每千名老人床位数、老年抚养比）均在代码 `data.py` 中给出计算式，可复算核验。
- 缺失年份一律留空、不做插值虚构；情景外推（图 11）为一元线性拟合示意，**不代表官方预测**。
- 本作品不含任何 AI 生成或合成的图片、音视频内容；使用的第三方开源软件（Python / Streamlit / Plotly / pandas）均遵循各自许可协议。

---

## 六、常见问题

**Q1：启动报错 `ModuleNotFoundError: No module named 'xxx'`**
依赖未装全。请先执行 `pip install -r requirements.txt`（或加上清华镜像参数）。

**Q2：页面打不开 / 端口被占用**
改用其他端口，例如 `--server.port 8800`；云服务器请确认安全组已放行该端口。

**Q3：图表显示空白**
多为网络拉取前端资源缓慢，稍等刷新即可；若在纯内网环境，可改用 `pip install` 时一并装好，
或直接在能联网的机器上运行演示。

**Q4：需要修改文案 / 数据**
编辑 `streamlit_app.py`（页面文案、章节、读图提示）或 `data.py`（指标与来源）后重新启动即可。
