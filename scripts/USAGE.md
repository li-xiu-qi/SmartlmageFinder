# SmartImager 启动脚本

## 使用方法

### 1. 环境初始化（首次运行）
```bash
python start.py init
```

### 2. 启动项目
```bash
python start.py
```

### 3. 仅启动后端
```bash
python start.py --backend-only
```

### 4. 仅启动前端
```bash
python start.py --frontend-only
```

## 项目结构

- `start.py` - 主启动脚本（统一入口）
- `scripts/` - 核心脚本模块
  - `environment_checker.py` - 环境检查模块
  - `model_manager.py` - 模型管理模块
  - `config_manager.py` - 配置管理模块
  - `init_environment.py` - 环境初始化模块
  - `start_project.py` - 项目启动模块
