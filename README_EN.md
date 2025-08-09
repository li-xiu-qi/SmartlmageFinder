<div align="center">
  <img src="assets/logo/logo.png" alt="SmartImageFinder Logo" width="200">
  <h1>SmartImageFinder</h1>

  <p>Intelligent image search / management with integrated AI conversational recommendation</p>

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

SmartImageFinder is a modern intelligent image search engine and management system featuring a dual-layer microservice architecture design, providing high-performance image management and intelligent retrieval capabilities. The system integrates advanced vector search technology and AI analysis capabilities to offer users a one-stop image management solution.

## 🏗️ System Architecture

### Architecture Overview

Current version uses a unified backend (FastAPI) + frontend (React) architecture. The conversational AI recommendation agent lives in `backend/ai_func/recommendation`, leveraging sqlite-vec vector search and SSE streaming without a separate AI microservice.

## Features

### 🖼️ Image Management

- **Image Browsing** - Intuitive grid layout and image preview functionality
- **Tag System** - Powerful multi-tag classification and filtering management
- **Metadata Editing** - Flexible title, description, and custom tag management
- **Batch Operations** - Efficient batch upload, analysis, and tag management
- **Drag-and-Drop Upload** - Support for multi-file selection and drag-and-drop upload

### 🔍 Intelligent Search

- **Text Search** - Image retrieval based on natural language descriptions
- **Image Search** - Find similar images using reference images
- **Vector Search** - Multi-dimensional search based on title, description, and image content
- **Similarity Search** - Similarity retrieval based on reference images
- **Filter Search** - Support for combined tag and time filtering

### 🤖 AI Analysis Features

- **Automatic Analysis** - Image content understanding based on CLIP model
- **Smart Annotation** - Automatic generation of image titles, descriptions, and tags
- **Batch Processing** - Support for large-scale batch AI analysis of images
- **API Integration** - Support for various multimodal vision model APIs

### 🎨 User Interface

- **Modern Design** - Beautiful interface based on React 18 + Ant Design 5
- **Responsive Layout** - Perfect adaptation for desktop and mobile devices
- **Real-time Interaction** - Support for image preview, zoom, and editing operations
- **Status Monitoring** - Real-time display of processing progress and system status
- **System Management** - Comprehensive configuration management and monitoring interface

## 🎯 Core Technical Features

- **🧠 Conversational Recommendation Agent** - Multi-turn (64K rolling window) + tool calls
- **🛡️ Vector Target Whitelist** - Prevents invalid table access / injection
- **🔌 Streaming SSE Output** - Incremental events (rewrite, search, results) improve UX
- **⚡ High-Performance Vector Retrieval** - SQLite + sqlite-vec lightweight vector database with millisecond search response
- **🧠 Advanced AI Models** - Integration with Jina CLIP V2 model providing precise multimodal search capabilities
- **🎨 Modern Technology Stack** - React 18 + TypeScript + FastAPI ensuring code quality and development experience
- **🔧 Smart Startup Management** - One-click startup script with automatic environment configuration and dependency management


## 🚀 Quick Start

### Environment Initialization

First-time use requires environment initialization:

```bash
# Clone the project
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder

# Environment initialization (automatically installs dependencies, downloads models, generates configuration)
python start.py init
```

### Start Services

```bash
# Start main services (frontend and backend)
python start.py

# Start backend service only
python start.py --backend-only

# Start frontend service only
python start.py --frontend-only
```

The startup script will automatically:
✅ Check environment dependencies  ✅ Install required packages  ✅ Download AI models  ✅ Start services

## Application Scenarios

- **Personal Image Management** - Intelligent organization and retrieval of personal photo libraries
- **Design Asset Management** - Efficient management and search of design resources
- **Content Creation** - Providing intelligent image retrieval services for creators
- **Enterprise Asset Management** - Enterprise-level image resource management solutions
- **AI Research Applications** - Research and application platform for multimodal AI technology

## 🛠️ Technical Architecture

### Main Service Technology Stack

#### Backend (`backend/`)

- **FastAPI** - High-performance asynchronous web framework
- **SQLite + sqlite-vec** - Lightweight vector database
- **Jina CLIP V2** - Multimodal vector encoding model
- **Connection Pool Management** - Efficient database connection management
- **Vector Cache** - Vector cache system implemented with diskcache

#### Frontend (`frontend/`)

- **React 18 + TypeScript** - Modern frontend framework
- **Ant Design 5.25** - Enterprise-grade UI component library
- **Vite** - Fast build tool
- **React Router 7.5** - Route management
- **Axios** - HTTP client

### AI Service Technology Stack

#### AI Backend (`ai_backend/`)

- **FastAPI** - AI service API framework
- **Recommendation Algorithms** - Intelligent image recommendation engine
- **Multimodal Analysis** - Image content understanding and analysis

#### AI Frontend (`ai_frontend/`)

- **React 18 + TypeScript** - AI interaction interface
- **Ant Design 5.4** - UI component library
- **Intelligent Search** - AI-driven search experience

### Core Components

- **Vector Search Engine** - Support for multiple search modes (text, image, vector, similarity)
- **AI Analysis Engine** - Automatic image content analysis and annotation
- **Tag Management System** - Intelligent tag classification and management
- **Cache System** - High-performance vector caching mechanism
- **Configuration Management** - Flexible system configuration management

## 🖥️ System Requirements

### Supported Platforms

- **Windows**: x86_64
- **Linux**: x86_64, aarch64  
- **macOS**: x86_64 (Intel), aarch64 (Apple Silicon)

### Software Requirements

- **Python**: 3.8+
- **Node.js**: 16+
- **Memory**: Recommended 4GB+
- **Storage**: Sufficient space for storing images and vector data
- **Network**: Internet connection required for first-time AI model download

## 📁 Project Structure

```
SmartImageFinder/
├── backend/                 # Main backend service
│   ├── routers/            # API route modules
│   ├── db_func/           # Database operations
│   ├── ai_func/           # AI analysis functions
│   └── config_files/      # Configuration files
├── frontend/               # Main frontend service
│   ├── src/pages/         # Page components
│   ├── src/components/    # Common components
│   └── src/services/      # API service layer
├── backend/ai_func/recommendation/  # Chat recommendation & tool calling logic
├── models/                # AI model files
├── data/                  # Data storage
│   ├── db/               # Database files
│   ├── images/           # Image storage
│   └── caches/           # Vector cache
├── scripts/               # Startup and management scripts
├── requirements.txt       # Python dependencies
└── start.py              # Startup entry point
```

## 🔧 Detailed Configuration

### Service Ports

- **Backend**: 10050 (from config.yaml)
- **Frontend**: 5173 (Vite default)

### Configuration Files

Main configuration file is located at `backend/config_files/config.yaml`:

```yaml
MODEL_PATH: ./models/yizhixiaoke/xiaoke-jina-clip-v2  # Model path
VECTOR_DB_DRIVER_DIR: ./backend/config_files/vector_db_driver  # Vector database driver
UPLOAD_DIR: ./data/images  # Image upload directory
DB_PATH: ./data/db/smartimagefinder.db  # Database path
HOST: 0.0.0.0  # Service listening address
PORT: 10050  # Service port
```

### Environment Variables

Support overriding configuration through environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://api.openai.com/v1"
```

### 💡 Usage Tips

#### Service Access URLs

- **Main Frontend Interface**: <http://localhost:5173>
- **Main Backend API**: <http://localhost:10050>  
- **API Documentation**: <http://localhost:10050/docs>
- **AI Frontend**: Requires starting AI services separately before access

## 📊 System Monitoring & Management

### System Status Monitoring

Through the system settings page, you can monitor in real-time:

- **System Information** - CPU, memory, disk usage
- **Database Status** - Connection pool status, table statistics
- **Storage Information** - Image count, tag count, storage usage
- **Cache Status** - Cache usage information
- **Vector Database** - Driver status, index information

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