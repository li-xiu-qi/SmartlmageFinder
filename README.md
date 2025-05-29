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

1. Clone the repository:

```bash
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure the system:

```bash
# Copy default configuration
cp backend/config/config.example.yaml backend/config/config.yaml
# Edit configuration file as needed
```

---

```yaml
AVAILABLE_VISION_MODELS: # List of available vision models, you can add your own as long as the corresponding vendor supports them
- Qwen/Qwen2.5-VL-32B-Instruct
- Pro/Qwen/Qwen2.5-VL-7B-Instruct 
DB_PATH: ./data/db/smartimagefinder.db # Database path
HOST: 0.0.0.0 # Don't modify this
PORT: 1000 # Backend port number
IMAGE_VECTOR_CACHE_DIR: ./data/caches/image_vector_cache
TEXT_VECTOR_CACHE_DIR: ./data/caches/text_vector_cache
MAX_CACHE_SIZE_GB: 1.5
MODEL_PATH: jinaai/jina-clip-v2 # I recommend downloading the model locally first, then replacing the path here
EMBEDDING_DIMENSION: 1024
OPENAI_API_BASE: https://api.siliconflow.cn/v1 # If you need to switch to another API provider, modify this
OPENAI_API_KEY: # Enter your OpenAI API key
UPLOAD_DIR: ./data/images # Directory for uploaded images
TEMP_DIR: ./data/temp # Directory for temporary files
USE_CACHE: true # Whether to use cache
VISION_MODEL: Qwen/Qwen2.5-VL-32B-Instruct # Name of the currently used vision model
# Add vector database driver path configuration
VECTOR_DB_DRIVER: ./backend/config_files/vector_db_driver/vec0.dll # Path configuration for vector database driver
```

Note ⚠️: The default driver is for Windows computers. If you're using a Mac or Linux computer, you need to download the corresponding driver from <https://github.com/asg017/sqlite-vec/releases> and replace the path. If you place it directly in the backend\config_files\vector_db_driver directory, you can just change the file name. You can also use an absolute path if you prefer.

4. Start the backend service:

```bash
python main.py
```

The service will run on `http://localhost:1000`, and API documentation can be viewed at `http://localhost:1000/docs`.

### Frontend Setup

1. Enter the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will run on <http://localhost:5173>.

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