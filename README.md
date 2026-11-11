# Depth Anything V2 深度估计

上传单张图片，预览相对深度并下载同尺寸16位归一化PNG。使用Small型号，权重约100MB；支持CPU或GPU。归一化数值不能作为米制距离，也不能直接跨图片比较。

独立部署包在项目根目录运行 `bash install.sh`，执行 `.venv/bin/python runtime/prefetch.py --project .` 准备权重，再运行 `bash start.sh`。服务监听6006。安装、镜像保存与30GB总额度说明见UPLOAD_GUIDE.md。

模型固定revision见app.json。Small权重Apache-2.0；保留上游许可。界面、下载输出和部署配置由本项目编写。
