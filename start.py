#!/usr/bin/env python3
"""
SmartImageFinder 一键启动脚本
自动安装依赖、检查配置、启动前后端服务
使用subprocess控制前后端服务（修复Windows多进程问题）
"""

import os
import sys
import subprocess
import time
import signal
import argparse
from pathlib import Path
from typing import Optional, List


def install_requirements_if_needed():
    """如果需要的话先安装依赖"""
    base_path = Path(__file__).parent.absolute()
    requirements_file = base_path / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt文件不存在")
        return False
    
    print("📦 正在安装Python依赖...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            cwd=base_path,
            capture_output=True,
            text=True,
            shell=sys.platform == "win32"
        )
        if result.returncode == 0:
            print("✓ Python依赖安装成功")
            return True
        else:
            print(f"❌ Python依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Python依赖安装失败: {e}")
        return False


# 先安装依赖，然后再导入
if not install_requirements_if_needed():
    print("依赖安装失败，退出...")
    sys.exit(1)

# 现在可以安全导入这些依赖了
import yaml
import psutil


class Colors:
    """终端颜色类"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class SmartImageFinderStarter:
    def __init__(self, skip_deps: bool = False, config_only: bool = False, backend_only: bool = False, frontend_only: bool = False):
        self.base_path = Path(__file__).parent.absolute()
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.should_exit = False
        
        # 命令行选项
        self.skip_deps = skip_deps
        self.config_only = config_only
        self.backend_only = backend_only
        self.frontend_only = frontend_only
        
        # 设置信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def print_colored(self, message: str, color: str = Colors.WHITE):
        """打印彩色文本"""
        print(f"{color}{message}{Colors.ENDC}")

    def print_banner(self):
        """打印启动横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    SmartImageFinder 启动器                    ║
║                                                              ║
║          🚀 智能图片搜索系统 - 一键启动解决方案                   ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.print_colored(banner, Colors.CYAN)

    def print_tip_card(self):
        """打印小提示卡片"""
        tip_card = """
╔══════════════════════════════════════════════════════════════╗
║                    📱 小提示                                 ║
╠══════════════════════════════════════════════════════════════╣
║  🔍 关注"筱可AI研习社"公众号获取更多支持：                       ║
║  • 💬 技术问题咨询和解答                                      ║
║  • 📚 最新AI技术分享和教程                                    ║
║  • 🚀 项目更新通知和新功能介绍                                ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.print_colored(tip_card, Colors.YELLOW)

    def signal_handler(self, signum, frame):
        """信号处理器"""
        self.print_colored("\n\n🛑 收到停止信号，正在关闭服务...", Colors.YELLOW)
        self.should_exit = True
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """清理资源"""
        self.print_colored("🧹 正在清理资源...", Colors.BLUE)
        
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.print_colored("正在停止后端进程...", Colors.BLUE)
                self.backend_process.terminate()
                try:
                    self.backend_process.wait(timeout=5)
                    self.print_colored("✓ 后端服务已停止", Colors.GREEN)
                except subprocess.TimeoutExpired:
                    self.print_colored("⚠️ 后端进程未响应，强制终止", Colors.YELLOW)
                    self.backend_process.kill()
                    self.backend_process.wait()
            except Exception as e:
                self.print_colored(f"⚠️ 停止后端进程时出现错误: {e}", Colors.YELLOW)

        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                self.print_colored("正在停止前端进程...", Colors.BLUE)
                self.frontend_process.terminate()
                try:
                    self.frontend_process.wait(timeout=5)
                    self.print_colored("✓ 前端服务已停止", Colors.GREEN)
                except subprocess.TimeoutExpired:
                    self.print_colored("⚠️ 前端进程未响应，强制终止", Colors.YELLOW)
                    self.frontend_process.kill()
                    self.frontend_process.wait()
            except Exception as e:
                self.print_colored(f"⚠️ 停止前端进程时出现错误: {e}", Colors.YELLOW)

        # 额外清理可能残留的进程
        self.kill_remaining_processes()

    def kill_remaining_processes(self):
        """清理可能残留的进程"""
        try:
            # 查找并终止可能残留的FastAPI进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'uvicorn' in cmdline and 'main:app' in cmdline:
                        proc.terminate()
                        proc.wait(timeout=3)
                        self.print_colored(f"✓ 清理残留的后端进程 PID: {proc.pid}", Colors.GREEN)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
                    
            # 查找并终止可能残留的Vite进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'vite' in cmdline or ('node' in proc.info['name'] and 'dev' in cmdline):
                        proc.terminate()
                        proc.wait(timeout=3)
                        self.print_colored(f"✓ 清理残留的前端进程 PID: {proc.pid}", Colors.GREEN)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
        except Exception as e:
            self.print_colored(f"⚠️ 清理残留进程时出现错误: {e}", Colors.YELLOW)

    def run_command(self, command: List[str], description: str, cwd: Optional[Path] = None) -> bool:
        """运行命令"""
        self.print_colored(f"正在{description}...", Colors.BLUE)
        try:
            result = subprocess.run(
                command, 
                cwd=cwd or self.base_path, 
                capture_output=True, 
                text=True, 
                shell=sys.platform == "win32"
            )
            if result.returncode == 0:
                self.print_colored(f"✓ {description}成功", Colors.GREEN)
                return True
            else:
                self.print_colored(f"❌ {description}失败: {result.stderr}", Colors.RED)
                return False
        except Exception as e:
            self.print_colored(f"❌ {description}失败: {e}", Colors.RED)
            return False

    def _stream_output(self, pipe, prefix: str, color: str):
        """从管道中实时读取并打印输出"""
        for line in iter(pipe.readline, ''):
            if self.should_exit:
                break
            line = line.strip()
            if line:
                self.print_colored(f"{prefix} {line}", color)
                
    def _create_output_thread(self, pipe, prefix: str, color: str):
        """创建输出流线程"""
        import threading
        thread = threading.Thread(
            target=self._stream_output,
            args=(pipe, prefix, color),
            daemon=True
        )
        thread.start()
        return thread

    def check_python_version(self) -> bool:
        """检查Python版本"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.print_colored(f"✓ Python版本: {version.major}.{version.minor}.{version.micro}", Colors.GREEN)
            return True
        else:
            self.print_colored(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)", Colors.RED)
            return False

    def check_node_version(self) -> bool:
        """检查Node.js版本"""
        try:
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.print_colored(f"✓ Node.js版本: {version}", Colors.GREEN)
                return True
            else:
                self.print_colored("❌ Node.js未安装或不在PATH中", Colors.RED)
                return False
        except Exception:
            self.print_colored("❌ Node.js未安装或不在PATH中", Colors.RED)
            return False

    def check_npm_version(self) -> bool:
        """检查npm版本"""
        try:
            result = subprocess.run(
                ["npm", "--version"], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.print_colored(f"✓ npm版本: {version}", Colors.GREEN)
                return True
            else:
                self.print_colored("❌ npm未安装或不在PATH中", Colors.RED)
                return False
        except Exception:
            self.print_colored("❌ npm未安装或不在PATH中", Colors.RED)
            return False

    def install_frontend_dependencies(self) -> bool:
        """安装前端依赖"""
        frontend_dir = self.base_path / "frontend"
        package_json = frontend_dir / "package.json"
        
        if not package_json.exists():
            self.print_colored("❌ frontend/package.json文件不存在", Colors.RED)
            return False

        node_modules = frontend_dir / "node_modules"
        if node_modules.exists():
            self.print_colored("✓ 前端依赖已安装", Colors.GREEN)
            return True

        return self.run_command(
            ["npm", "install"],
            "安装前端依赖",
            frontend_dir
        )

    def check_config_file(self) -> bool:
        """检查配置文件"""
        config_file = self.base_path / "backend" / "config_files" / "config.yaml"
        return config_file.exists()

    def check_model_exists(self) -> bool:
        """检查模型是否存在"""
        config_file = self.base_path / "backend" / "config_files" / "config.yaml"
        if not config_file.exists():
            return False
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                model_path = config.get('MODEL_PATH', '')
                
                if not model_path:
                    return False
                
                # 检查绝对路径或相对路径
                if os.path.isabs(model_path):
                    return os.path.exists(model_path)
                else:
                    full_path = self.base_path / model_path
                    return full_path.exists()
        except Exception:
            return False
    def run_init_config(self) -> bool:
        """运行初始化配置脚本"""
        init_script = self.base_path / "init_config.py"
        if not init_script.exists():
            self.print_colored("❌ init_config.py脚本不存在", Colors.RED)
            return False

        self.print_colored("正在运行配置初始化脚本...", Colors.BLUE)
        try:
            # 使用 subprocess.Popen 来允许用户交互输入
            process = subprocess.Popen(
                [sys.executable, str(init_script)],
                cwd=self.base_path,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            
            # 等待进程完成
            returncode = process.wait()
            
            if returncode == 0:
                self.print_colored("✓ 配置初始化完成", Colors.GREEN)
                return True
            else:
                self.print_colored("❌ 配置初始化失败", Colors.RED)
                return False
        except Exception as e:
            self.print_colored(f"❌ 配置初始化失败: {e}", Colors.RED)
            return False    
    def start_backend(self) -> bool:
        """启动后端服务"""
        main_script = self.base_path / "main.py"
        if not main_script.exists():
            self.print_colored("❌ main.py文件不存在", Colors.RED)
            return False

        self.print_colored("正在启动后端服务...", Colors.BLUE)
        
        try:
            # 使用subprocess.Popen直接启动后端进程
            self.backend_process = subprocess.Popen(
                [sys.executable, str(main_script)],
                cwd=self.base_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            # 创建输出流线程
            stdout_thread = self._create_output_thread(self.backend_process.stdout, "[Backend]", Colors.CYAN)
            stderr_thread = self._create_output_thread(self.backend_process.stderr, "[Backend Error]", Colors.RED)
            
            # 等待一段时间检查服务是否启动成功
            time.sleep(5)
            
            if self.backend_process.poll() is None:
                self.print_colored(f"✓ 后端服务启动成功 (PID: {self.backend_process.pid})", Colors.GREEN)
                return True
            else:
                self.print_colored("❌ 后端服务启动失败", Colors.RED)
                return False
        except Exception as e:
            self.print_colored(f"❌ 启动后端服务时出现错误: {e}", Colors.RED)
            return False

    def start_frontend(self) -> bool:
        """启动前端服务"""
        frontend_dir = self.base_path / "frontend"
        if not frontend_dir.exists():
            self.print_colored("❌ frontend目录不存在", Colors.RED)
            return False

        self.print_colored("正在启动前端服务...", Colors.BLUE)
        
        try:
            # 使用subprocess.Popen直接启动前端进程
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
                shell=sys.platform == "win32",
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            # 创建输出流线程
            stdout_thread = self._create_output_thread(self.frontend_process.stdout, "[Frontend]", Colors.PURPLE)
            stderr_thread = self._create_output_thread(self.frontend_process.stderr, "[Frontend Error]", Colors.RED)
            
            # 等待一段时间检查服务是否启动成功
            time.sleep(8)  # 前端启动通常需要更长时间
            
            if self.frontend_process.poll() is None:
                self.print_colored(f"✓ 前端服务启动成功 (PID: {self.frontend_process.pid})", Colors.GREEN)
                return True
            else:
                self.print_colored("❌ 前端服务启动失败", Colors.RED)
                return False
        except Exception as e:
            self.print_colored(f"❌ 启动前端服务时出现错误: {e}", Colors.RED)
            return False

    def monitor_processes(self):
        """监控进程状态"""
        while not self.should_exit:
            time.sleep(5)
            
            # 检查后端进程
            if self.backend_process and self.backend_process.poll() is not None and not self.should_exit:
                self.print_colored("⚠️ 后端进程意外退出", Colors.YELLOW)
                if not self.frontend_only:
                    self.should_exit = True
                    break
            
            # 检查前端进程
            if self.frontend_process and self.frontend_process.poll() is not None and not self.should_exit:
                self.print_colored("⚠️ 前端进程意外退出", Colors.YELLOW)
                if not self.backend_only:
                    self.should_exit = True
                    break

    def get_backend_config(self) -> tuple:
        """从配置文件读取后端服务配置"""
        config_file = self.base_path / "backend" / "config_files" / "config.yaml"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                host = config.get('HOST', '127.0.0.1')  # 默认值
                port = config.get('PORT', 8000)  # 默认值
                return host, port
        except Exception as e:
            self.print_colored(f"⚠️ 读取后端配置文件失败: {e}，使用默认配置", Colors.YELLOW)
            return '127.0.0.1', 8000

    def show_service_info(self):
        """显示服务信息"""
        self.print_colored("\n" + "="*60, Colors.GREEN)
        self.print_colored("🎉 SmartImageFinder 服务启动成功！", Colors.GREEN)
        self.print_colored("="*60, Colors.GREEN)
        
        if not self.frontend_only:
            host, port = self.get_backend_config()
            backend_url = f"http://{host}:{port}"
            if host == '0.0.0.0':
                backend_url = f"http://localhost:{port}"  # 当绑定所有网卡时，显示 localhost
            self.print_colored(f"🔗 后端API地址: {backend_url}", Colors.CYAN)
            self.print_colored(f"📖 API文档地址: {backend_url}/docs", Colors.CYAN)
            
        if not self.backend_only:
            self.print_colored("🌐 前端地址: http://localhost:5173", Colors.CYAN)
            self.print_colored("📱 移动端访问: http://你的IP:5173", Colors.CYAN)
            
        self.print_colored("="*60, Colors.GREEN)
        self.print_colored("💡 按 Ctrl+C 停止服务", Colors.YELLOW)
        self.print_colored("="*60, Colors.GREEN)

    def run(self):
        """主运行函数"""
        self.print_banner()
        self.print_tip_card()
        
        # 如果只是运行配置
        if self.config_only:
            return self.run_init_config()

        # 1. 检查环境
        self.print_colored("\n🔍 检查运行环境...", Colors.BOLD)
        
        if not self.check_python_version():
            return False
        
        if not self.frontend_only:
            self.print_colored("检查后端运行环境...", Colors.BLUE)
            
        if not self.backend_only:
            if not self.check_node_version() or not self.check_npm_version():
                return False

        # 2. 安装前端依赖（Python依赖已在脚本开头安装）
        if not self.skip_deps and not self.backend_only:
            self.print_colored("\n📦 安装前端依赖...", Colors.BOLD)
            if not self.install_frontend_dependencies():
                return False
        elif not self.skip_deps:
            self.print_colored("\n✓ Python依赖已安装", Colors.GREEN)
        else:
            self.print_colored("\n⏭️ 跳过依赖安装", Colors.YELLOW)

        # 3. 检查配置
        self.print_colored("\n⚙️ 检查配置...", Colors.BOLD)
        
        if not self.frontend_only:
            if not self.check_config_file():
                self.print_colored("⚠️ 配置文件不存在，尝试运行初始化配置...", Colors.YELLOW)
                if not self.run_init_config():
                    return False
            else:
                self.print_colored("✓ 配置文件存在", Colors.GREEN)
                
            if not self.check_model_exists():
                self.print_colored("⚠️ 模型文件不存在，请确保模型路径配置正确", Colors.YELLOW)

        # 4. 启动服务
        self.print_colored("\n🚀 启动服务...", Colors.BOLD)
        
        backend_started = False
        frontend_started = False
        
        # 启动后端
        if not self.frontend_only:
            backend_started = self.start_backend()
        
        # 启动前端
        if not self.backend_only:
            frontend_started = self.start_frontend()

        # 5. 显示服务信息并监控
        if backend_started or frontend_started:
            self.show_service_info()
            
            try:
                self.monitor_processes()
            except KeyboardInterrupt:
                pass
        else:
            self.print_colored("❌ 服务启动失败", Colors.RED)
            return False

        return True


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="SmartImageFinder 一键启动脚本")
    parser.add_argument("--skip-deps", action="store_true", help="跳过依赖安装")
    parser.add_argument("--config-only", action="store_true", help="仅运行配置初始化")
    parser.add_argument("--backend-only", action="store_true", help="仅启动后端服务")
    parser.add_argument("--frontend-only", action="store_true", help="仅启动前端服务")
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    starter = SmartImageFinderStarter(
        skip_deps=args.skip_deps,
        config_only=args.config_only,
        backend_only=args.backend_only,
        frontend_only=args.frontend_only
    )
    
    try:
        success = starter.run()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        starter.print_colored("\n\n👋 用户取消启动", Colors.YELLOW)
        starter.cleanup()
        sys.exit(0)
    except Exception as e:
        starter.print_colored(f"\n❌ 发生未知错误: {e}", Colors.RED)
        starter.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
