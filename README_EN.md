# SmartImageFinder

An intelligent image search engine and management system built on multimodal vector models and visual multimodal models. It enables precise text-to-image and image-to-image intelligent retrieval methods while providing a complete image management solution. This project uses FastAPI + React tech stack, integrating Jina CLIP V2 and multimodal large language models to provide a one-stop solution for personal image management.

## Features

### Image Management

- Intuitive image browsing interface with grid layout and image preview
- Powerful tag management system supporting multi-tag classification and filtering
- Flexible metadata editing including title, description, and custom tags
- Efficient batch operation support for uploading, analysis, and tag management
- Drag-and-drop upload and multiple file selection support

### Multimodal AI Analysis

- High-precision vector encoding based on CLIP V2 model
- Supports three vector retrieval modes:
  - Text-to-Image matching: Find similar images through natural language descriptions
  - Image-to-Image matching: Find similar content based on reference images
  - Hybrid vector search: Multi-dimensional search combining title, description, and image content
- Integrated multimodal vision model API providing intelligent image analysis:
  - Automatic generation of image titles and detailed descriptions
  - Intelligent key tag extraction
  - Support for batch AI analysis processing

### User Interface

- Modern interface design based on React + Ant Design
- Responsive layout adapting to different screen sizes
- Support for image preview, zoom, and editing operations
- Intuitive tag filtering and search interface
- Real-time processing progress and status indicators
- Support for dark/light theme switching

## Use Cases

- Personal image library management and organization
- Design resource retrieval and management
- Intelligent image classification and retrieval
- Content-based image similarity search
- Intelligent image annotation and description generation

## Technical Architecture

### Backend

- FastAPI framework providing high-performance API services
- SQLite + sqlite-vec for lightweight efficient vector storage and retrieval
- Jina CLIP V2 model for feature vector extraction
- Integrated multimodal large model API for content understanding and generation

### Frontend

- React 18 + TypeScript for building user interface
- Ant Design 5.x for UI component library
- Vite as development and build tool
- Axios for handling HTTP requests
- Support for file drag-and-drop and batch processing

## Core Features Showcase

- Multimodal search: Support text search, image search, and hybrid search
- Intelligent tagging: Automatic generation and management of image tags
- Metadata management: Flexible editing and organization of image information
- AI analysis: Intelligent generation of image descriptions and tags
- Batch processing: Efficient handling of large image files
- System management: Monitor system status and configuration management

## Requirements

- Python 3.8+
- Node.js 16+
- SQLite 3
- CUDA-capable GPU (recommended but not required)
- Sufficient disk space for storing images and vector data

## Quick Start

1. Clone the repository:

\`\`\`bash
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder
\`\`\`

2. Install dependencies:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Configure the system:

\`\`\`bash
# Copy default configuration
cp backend/config/config.example.yaml backend/config/config.yaml
# Edit configuration file as needed
\`\`\`

---

\`\`\`json
AVAILABLE_VISION_MODELS: # List of available vision models, can be extended if supported by the provider
- Qwen/Qwen2.5-VL-32B-Instruct
- Pro/Qwen/Qwen2.5-VL-7B-Instruct 
DB_PATH: ./data/db/smartimagefinder.db # Database path
HOST: 0.0.0.0 # Don't modify this
PORT: 1000 # Backend port number
IMAGE_VECTOR_CACHE_DIR: ./data/caches/image_vector_cache
TEXT_VECTOR_CACHE_DIR: ./data/caches/text_vector_cache
MAX_CACHE_SIZE_GB: 1.5
MODEL_PATH: jinaai/jina-clip-v2 # Recommend downloading the model locally and replacing the path
EMBEDDING_DIMENSION: 1024
OPENAI_API_BASE: https://api.siliconflow.cn/v1 # Modify if using different API provider
OPENAI_API_KEY: # Fill in your OpenAI API key
UPLOAD_DIR: ./data/images # Upload directory for images
TEMP_DIR: ./data/temp # Temporary file directory
USE_CACHE: true # Whether to use cache
VISION_MODEL: Qwen/Qwen2.5-VL-32B-Instruct # Current vision model name
VECTOR_DB_DRIVER: ./backend/config_files/vector_db_driver/vec0.dll # Vector database driver path
\`\`\`

⚠️ Note: The default driver is for Windows computers. For Mac or Linux computers, download the corresponding driver from <https://github.com/asg017/sqlite-vec/releases> and replace the path. You can put it directly in the backend\config_files\vector_db_driver directory and just change the filename, or you can use an absolute path.

4. Start backend service:

\`\`\`bash
python main.py
\`\`\`

The service will run on \`http://localhost:1000\`, and API documentation can be viewed at \`http://localhost:1000/docs\`.

### Frontend Setup

1. Enter frontend directory:

\`\`\`bash
cd frontend
\`\`\`

2. Install dependencies:

\`\`\`bash
npm install
\`\`\`

3. Start development server:

\`\`\`bash
npm run dev
\`\`\`

Frontend will run on <http://localhost:5173>.

## System Configuration

### Frontend Configuration

Modify the frontend API request address in \`vite.config.ts\` file: [vite.config.ts](frontend/vite.config.ts)

### Backend Configuration

Core system configuration is in \`backend/config_files/config.yaml\` configuration file:
![backend_config](backend/config_files/config.yaml)
The system will load the configuration file by default. You can also remove loading from the default file and use the configuration in [config.py](backend/config.py).

## License

This project is licensed under the [Apache License 2.0](LICENSE).
