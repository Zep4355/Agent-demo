# 部署上线指南：把「一句话 Agent」变成公开网址

技术路线：**GitHub（存代码） → Streamlit Community Cloud（免费托管）**
最终得到一个公开网址：`https://你的应用名.streamlit.app`

> ⚠️ 提前读这 3 条，避免踩坑：
> 1. **绝对不要把 `.env` 推到 GitHub**（里面有你的 API key）——项目已内置 `.gitignore` 自动排除它
> 2. 公开网址**谁都能用**，每次调用消耗你的 DeepSeek 余额；不演示时可以在 Streamlit Cloud 上暂停应用
> 3. 部署后 API key 通过云平台的 **Secrets** 配置，不写进代码

---

## 第 1 步：准备账号和工具

- [注册 GitHub](https://github.com)（免费）
- 电脑没装 Git 的话：去 https://git-scm.com/download/win 下载安装，一路"下一步"即可

## 第 2 步：本地把项目变成 Git 仓库

打开 `agent_demo` 文件夹 → 地址栏输入 `cmd` 回车，依次运行：

```bash
git init
git add .
git commit -m "一句话Agent 网页版"
```

（项目自带 `.gitignore`，`.env` 和运行时文件不会被提交，放心）

## 第 3 步：推送到 GitHub

1. 打开 GitHub → 右上角 **+** → **New repository**
2. 名字填 `agent-demo`，选 **Public**，不要勾选任何初始化选项 → Create
3. 复制你仓库的地址：`https://github.com/你的用户名/agent-demo.git`
4. 回到 cmd，运行（把地址换成你的）：

```bash
git branch -M main
git remote add origin https://github.com/你的用户名/agent-demo.git
git push -u origin main
```

- 首次 push 会弹出 GitHub 登录窗口，按提示授权即可
- 成功后打开 GitHub 仓库页面，能看到代码就对了

## 第 4 步：Streamlit Cloud 部署

1. 打开 https://streamlit.io/cloud
2. 点 **Sign in with GitHub**（用你的 GitHub 授权登录）
3. 点 **New app** → 选仓库 `agent-demo` → Main file 填 `web_app.py` → **Deploy**
4. 等 2~3 分钟，部署完成后拿到网址：`https://agent-demo-你的用户名.streamlit.app`

## 第 5 步：配置 API key（Secrets）

部署的代码里**没有**你的 key，需要在云平台单独配置：

1. 在 Streamlit Cloud 的 app 页面 → 点 **⚙️ Settings** → **Secrets**
2. 填入：

```toml
DEEPSEEK_API_KEY = "sk-你的真实key"
```

3. 保存 → **Restart app**，刷新网址就能用了

## 验证

打开你的公开网址 → 输入"查一下西安今天的天气，整理成报告保存" → 看到 Agent 干活日志 = 部署成功 🎉

## 常用维护

| 操作 | 方法 |
|---|---|
| 更新代码 | 本地改完 `git add .` → `git commit -m "xxx"` → `git push`，Cloud 自动重新部署 |
| 暂停应用 | Streamlit Cloud 的 app 设置里 Stop（省额度） |
| 换 key | Settings → Secrets 修改 → Restart |
