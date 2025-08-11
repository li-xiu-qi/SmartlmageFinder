#!/usr/bin/env python3
"""
SmartImageFinder 项目启动模块
负责启动前后端服务
"""

import os
import sys
import subprocess
import time
import signal
import argparse
from pathlib import Path
from typing import Optional, List

try:
    import yaml
    import psutil
except ImportError as e:
    print(f"❌ 依赖导入失败: {e}")
    print("请先运行环境初始化脚本: python start.py init")
    sys.exit(1)


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


class LogLevel:
    """日志级别类"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    OTHER = "other"


class SmartImageFinderStarter:
    def __init__(self, backend_only: bool = False, frontend_only: bool = False, reload: bool = False):
        self.base_path = Path(__file__).parent.parent.absolute()
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.should_exit = False
        
        # 命令行选项
        self.backend_only = backend_only
        self.frontend_only = frontend_only
        self.reload = reload
        
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
║          🚀 智能图片搜索系统 - 快速启动服务                      ║
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

    def _get_log_level(self, line: str) -> str:
        """判断日志级别"""
        message = line.upper()
        if any(error_indicator in message for error_indicator in ["ERROR:", "EXCEPTION:", "CRITICAL:"]):
            return LogLevel.ERROR
        elif any(warn_indicator in line for warn_indicator in ["WARNING:", "USERWARNING:", "WARN:"]):
            return LogLevel.WARNING
        elif any(info_indicator in line for info_indicator in ["INFO:", "DEBUG:", "WILL WATCH", "STARTED", "WAITING", "APPLICATION", "READY IN"]):
            return LogLevel.INFO
        return LogLevel.OTHER

    def _stream_output(self, pipe, prefix: str, color: str):
        """从管道中实时读取并打印输出"""
        try:
            # 使用 utf-8 编码读取
            with os.fdopen(pipe.fileno(), 'r', encoding='utf-8', errors='replace') as reader:
                for line in reader:
                    if self.should_exit:
                        break
                    line = line.strip()
                    if line:
                        log_level = self._get_log_level(line)
                        display_prefix = prefix.replace(" Error]", "]")  # 统一使用正常的前缀
                        
                        if log_level == LogLevel.ERROR:
                            self.print_colored(f"{display_prefix} {line}", Colors.RED)
                        elif log_level == LogLevel.WARNING:
                            self.print_colored(f"{display_prefix} {line}", Colors.YELLOW)
                        elif log_level == LogLevel.INFO:
                            self.print_colored(f"{display_prefix} {line}", Colors.CYAN)
                        else:
                            self.print_colored(f"{display_prefix} {line}", color)
        except Exception as e:
            self.print_colored(f"💭 输出流读取异常(可以忽略): {e}", Colors.YELLOW)

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

    def start_backend(self) -> bool:
        """启动后端服务"""
        main_script = self.base_path / "main.py"
        if not main_script.exists():
            self.print_colored("❌ main.py文件不存在", Colors.RED)
            return False

        self.print_colored("正在启动后端服务...", Colors.BLUE)
        
        try:
            # 设置环境变量，确保 Python 输出使用 UTF-8 编码
            my_env = os.environ.copy()
            my_env["PYTHONIOENCODING"] = "utf-8"
            
            # 使用subprocess.Popen直接启动后端进程
            # 通过命令行传递是否启用热加载到 main.py
            backend_cmd = [sys.executable, str(main_script)]
            if self.reload:
                backend_cmd.append("--reload")

            self.backend_process = subprocess.Popen(
                backend_cmd,
                cwd=self.base_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
                env=my_env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            # 创建输出流线程
            self._create_output_thread(self.backend_process.stdout, "[Backend]", Colors.CYAN)
            self._create_output_thread(self.backend_process.stderr, "[Backend Error]", Colors.RED)
            
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
            # 设置环境变量，确保输出使用 UTF-8 编码
            my_env = os.environ.copy()
            my_env["PYTHONIOENCODING"] = "utf-8"
            # npm 输出强制使用 UTF-8
            my_env["FORCE_COLOR"] = "true"
            
            # 使用subprocess.Popen直接启动前端进程
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
                env=my_env,
                shell=sys.platform == "win32",
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            # 创建输出流线程
            self._create_output_thread(self.frontend_process.stdout, "[Frontend]", Colors.PURPLE)
            self._create_output_thread(self.frontend_process.stderr, "[Frontend Error]", Colors.RED)
            
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
        config_file = self.base_path / "backend" / "config" / "files" / "config.yaml"
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
        """显示服务信息（优先读取环境变量）"""
        self.print_colored("\n" + "="*60, Colors.GREEN)
        self.print_colored("🎉 SmartImageFinder 服务启动成功！", Colors.GREEN)
        self.print_colored("="*60, Colors.GREEN)

        # 后端地址
        host, port = self.get_backend_config()
        env_host = os.getenv("SIF_HOST")
        env_port = os.getenv("SIF_PORT")
        if env_host:
            host = env_host
        if env_port:
            try:
                port = int(env_port)
            except ValueError:
                pass
        backend_url = f"http://{host}:{port}"
        if host == '0.0.0.0':
            backend_url = f"http://localhost:{port}"

        if not self.frontend_only:
            self.print_colored(f"🔗 后端API地址: {backend_url}", Colors.CYAN)
            self.print_colored(f"📖 API文档地址: {backend_url}/docs", Colors.CYAN)
            # 显示前端代理后端的目标（若配置）
            proxy_origin = os.getenv("SIF_BACKEND_ORIGIN")
            if not proxy_origin:
                proxy_origin = backend_url
            self.print_colored(f"🧩 前端代理后端: {proxy_origin}", Colors.CYAN)

        # 前端地址
        if not self.backend_only:
            fe_port = 5173
            env_fe = os.getenv("SIF_FRONTEND_PORT")
            if env_fe:
                try:
                    fe_port = int(env_fe)
                except ValueError:
                    pass
            self.print_colored(f"🌐 前端地址: http://localhost:{fe_port}", Colors.CYAN)
            self.print_colored(f"📱 移动端访问: http://你的IP:{fe_port}", Colors.CYAN)

        self.print_colored("="*60, Colors.GREEN)
        self.print_colored("💡 按 Ctrl+C 停止服务", Colors.YELLOW)
        self.print_colored("="*60, Colors.GREEN)

    def run(self):
        """主运行函数"""
        self.print_banner()
        self.print_tip_card()
        
        # 检查环境是否已初始化
        from environment_checker import is_environment_ready
        self.print_colored("\n🔍 检查环境状态...", Colors.BOLD)
        
        if not is_environment_ready():
            self.print_colored("❌ 环境未初始化", Colors.RED)
            self.print_colored("请先运行: python start.py init", Colors.YELLOW)
            return False
        else:
            self.print_colored("✓ 环境已初始化", Colors.GREEN)
        
        # 检查配置文件
        from environment_checker import check_config_file, check_model_exists
        self.print_colored("\n⚙️ 检查配置...", Colors.BOLD)
        
        if not self.frontend_only:
            if not check_config_file():
                self.print_colored("❌ 配置文件不存在", Colors.RED)
                self.print_colored("请重新运行: python start.py init", Colors.YELLOW)
                return False
            else:
                self.print_colored("✓ 配置文件存在", Colors.GREEN)
                
            if not check_model_exists():
                self.print_colored("⚠️ 模型文件不存在，请确保模型路径配置正确", Colors.YELLOW)
        
        # 启动服务
        self.print_colored("\n🚀 启动服务...", Colors.BOLD)
        
        backend_started = False
        frontend_started = False
        
        # 启动后端
        if not self.frontend_only:
            backend_started = self.start_backend()
        
        # 启动前端
        if not self.backend_only:
            frontend_started = self.start_frontend()
 
        # 显示服务信息并监控
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
    parser = argparse.ArgumentParser(description="SmartImageFinder 项目启动脚本")
    parser.add_argument("--backend-only", action="store_true", help="仅启动后端服务")
    parser.add_argument("--frontend-only", action="store_true", help="仅启动前端服务")
    parser.add_argument("--reload", action="store_true", help="启用后端热加载 (开发模式)")
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    starter = SmartImageFinderStarter(
        backend_only=args.backend_only,
        frontend_only=args.frontend_only,
        reload=args.reload,
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