<div align="center">
  <img src="assets/logo/logo.png" alt="SmartImageFinder Logo" width="200">
  <h1>SmartImageFinder</h1>

  <p>Intelligent image search engine and management system based on multimodal vector models and vision multimodal models</p>

  <div>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
    <img src="https://img.shields.io/badge/version-1.0.0-green.svg" alt="Version">
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.100+-orange.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/React-18-61DAFB.svg" alt="React">
  </div>

  <div>
    <a href="README.md">中文</a> | 
    <a href="README_EN.md">English</a>
  </div>
</div>

## Project Overview

An intelligent image search engine and management system that enables precise text-to-image, image-to-image, and other smart retrieval methods, while providing a complete image management solution. This project uses the FastAPI + React technology stack, integrating Jina CLIP V2 and multimodal large language models to provide a one-stop solution for personal image management.

## Features

### Image Management

- Intuitive image browsing interface with grid layout and image preview
- Powerful tag management system supporting multi-tag classification and filtering
- Flexible metadata editing, including title, description, and custom tags
- Efficient batch operation support for uploading, analyzing, and tag management
- Support for drag-and-drop uploads and multi-file selection

### Multimodal AI Analysis

- High-precision vector encoding based on CLIP V2 model
- Support for three vector retrieval modes:
  - Text-to-image matching: Find similar images through natural language descriptions
  - Image-to-image matching: Find similar content based on reference images
  - Hybrid vector search: Multi-dimensional search combining title, description, and image content
- Integration with multimodal vision model APIs for intelligent image analysis:
  - Automatic generation of image titles and detailed descriptions
  - Intelligent extraction of key tags
  - Support for batch AI analysis processing

### User Interface

- Modern interface design based on React + Ant Design
- Responsive layout, adapting to different screen sizes
- Support for image preview, zoom, and editing operations
- Intuitive tag filtering and search interface
- Real-time display of processing progress and status notifications
- Support for dark/light theme switching

## 🎯 Key Highlights

- **🚀 One-Click Startup**: Brand new intelligent startup script that automatically installs dependencies, configures environment, and starts services - experience full functionality in minutes
- **🧠 Multimodal AI Search**: CLIP V2-based text-to-image, image-to-image, and hybrid search for search-engine-level precision
- **🏷️ Smart Tagging System**: AI-generated image titles, descriptions, and tags with flexible categorization management
- **⚡ High-Performance Vector Retrieval**: SQLite + sqlite-vec lightweight vector database with millisecond search response
- **🎨 Modern Interface**: Beautiful React + Ant Design interface supporting drag-and-drop upload and batch processing
- **🔧 Zero-Configuration Startup**: Out-of-the-box configuration script with flexible switching between local models and cloud APIs

## ⚡ 30-Second Quick Start

```bash
# Clone the project
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder

# One-click startup (handles all configuration automatically)
python start.py
```

That's it! The startup script will automatically:
✅ Check environment dependencies  ✅ Install required packages  ✅ Download AI models  ✅ Start services

## Use Cases

- Personal image library management and organization
- Design material retrieval and management
- Intelligent image classification and retrieval
- Content-based image similarity search
- Intelligent image annotation and description generation

## Technical Architecture

### Backend

- FastAPI framework providing high-performance API services
- SQLite + sqlite-vec implementing lightweight and efficient vector storage and retrieval
- Jina CLIP V2 model for feature vector extraction
- Integration with multimodal large model APIs for content understanding and generation

### Frontend

- React 18 + TypeScript for building the user interface
- Ant Design 5.x providing UI component library
- Vite as development and build tool
- Axios for handling HTTP requests
- Support for file drag-and-drop and batch processing

## Core Features Showcase

- Multimodal search: Support for text search, image search, and hybrid search
- Smart tags: Automatically generate and manage image tags
- Metadata management: Flexibly edit and organize image information
- AI analysis: Intelligently generate image descriptions and tags
- Batch processing: Efficiently process large numbers of image files
- System management: Monitor system status and configuration management

## Requirements

- Python 3.8+
- Node.js 16+
- SQLite 3
- CUDA-supported GPU (recommended but not required)
- Sufficient disk space for storing images and vector data

## Quick Start

### 🚀 One-Click Startup (Recommended)

We provide a convenient one-click startup script that automatically handles all configuration and service startup:

```bash
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder
python start.py
```

🎉 **One-Click Startup Features**:

- Automatically check and install Python and Node.js dependencies
- Automatically run configuration initialization (including model download)
- Automatically start frontend and backend services
- Intelligent service status monitoring
- Graceful error handling and service shutdown

### 🔧 Startup Options

The startup script supports various options to meet different needs:

```bash
# Complete startup (default)
python start.py

# Skip dependency installation (for environments with dependencies already installed)
python start.py --skip-deps

# Only run configuration initialization
python start.py --config-only

# Only start backend service
python start.py --backend-only

# Only start frontend service
python start.py --frontend-only
```

### 📝 Manual Setup

If you need manual control over the startup process, follow these steps:

1. **Clone the repository**:

```bash
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder
```

2. **Install backend dependencies**:

```bash
pip install -r requirements.txt
```

3. **Run the initialization configuration script**:

```bash
python init_config.py
```

The script will automatically complete the following operations:

- Check and install ModelScope dependencies
- Download the JINA CLIP V2 model locally
- Create the `config.yaml` file based on the example configuration
- Configure all necessary paths and parameters

⚠️ **Configuration Notes**:

- During script execution, you can choose to use an existing local model or download a new one
- Optionally configure the OpenAI API key to enable AI analysis features
- Configuration file paths will be automatically generated as absolute paths based on your project directory

4. **Start the backend service**:

```bash
python main.py
```

The service will run on `http://localhost:1000`, and API documentation can be viewed at `http://localhost:1000/docs`.

5. **Install frontend dependencies and start**:

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on <http://localhost:5173>.

## 💡 Usage Tips

### Startup Script Features

- **Intelligent Environment Detection**: Script automatically detects Python and Node.js versions to ensure compatibility
- **Dependency Management**: Automatically installs missing Python packages and npm packages
- **Configuration Wizard**: Guides you through model download and API configuration on first run
- **Service Monitoring**: Automatically monitors frontend and backend service status with auto-restart on exceptions
- **Graceful Shutdown**: Press `Ctrl+C` to safely stop all services

### Troubleshooting

**Q: Startup script reports Python version incompatibility**  
A: Please ensure Python 3.8 or higher is installed

**Q: Node.js dependency installation fails**  
A: Use `python start.py --backend-only` to start backend first, then manually install frontend dependencies

**Q: Model download is slow**  
A: Script supports using existing models. If you've already downloaded JINA CLIP V2, specify the local path during configuration

**Q: API key configuration error**  
A: Use `python start.py --config-only` to re-run configuration initialization

## System Configuration

### Frontend Configuration

Modify the frontend API request address in the `vite.config.ts` file: [vite.config.ts](frontend/vite.config.ts)

### Backend Configuration

The core system configuration is in the `backend/config_files/config.yaml` configuration file:
![backend_config](backend/config_files/config.yaml)
By default, the system configuration file will be loaded. You can also remove the configuration loading from the default file and use the configuration in [config.py](backend/config.py).

## Demo Screenshots

### System Architecture

![System Architecture](assets/images/SmartImageFinder-项目架构图-v3.png)

### Homepage Display

![Homepage](assets/images/首页.png)
![Homepage Image Sidebar](assets/images/首页图片侧边栏展示.png)

### Image Upload and Analysis

![Image Upload](assets/images/图片上传.png)
![Edit Image Analysis During Upload](assets/images/上传的时候可以编辑图片分析内容.png)
![Upload Completion Results](assets/images/上传完成的结果显示.png)
![AI Automatic Image Content Analysis](assets/images/AI自动分析图片内容.png)
![AI Automatic Image Content Analysis Effect](assets/images/AI自动分析图片内容效果.png)

### Tag Management System

![Tag Management](assets/images/标签管理.png)
![Tag Editing](assets/images/标签编辑.png)
![Tag Editing Effect](assets/images/标签编辑效果.png)
![Tag Search and Filtering](assets/images/标签搜索及过滤.png)
![Click Tag to Jump to Corresponding Image Display Section and Filter Images](assets/images/点击标签可以直接跳转到对应的图片展示部分并过滤图片.png)
![Tag-Based Filtering Search](assets/images/基于标签的过滤搜索.png)

### Smart Search Function

![Fuzzy Search Based Image Search](assets/images/基于模糊搜索的图片搜索.png)
![Title Vector Search](assets/images/标题向量搜索.png)
![Title Vector and Description Vector Hybrid Search](assets/images/标题向量和描述向量混合搜索.png)
![Three Hybrid Search Results](assets/images/三种混合搜索的搜索效果.png)
![Search Images Using Images](assets/images/使用图搜索图.png)

### Metadata Management

![Metadata Editing](assets/images/元数据编辑.png)
![Metadata Editing Effect](assets/images/元数据编辑效果.png)
![Image Description Update](assets/images/图片描述更新.png)

### System Management

![System Settings](assets/images/系统设置.png)
![System Status View](assets/images/系统状态查看.png)

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Contact

If you encounter any issues or have any suggestions while using this project, feel free to contact me:

<div align="center">
  <img src="assets/wechat/筱可AI研习社_258.jpg" alt="XiaoKe AI Study Group" width="200">
  <p>Scan the QR code to follow the "XiaoKe AI Study Group" official account</p>
</div>