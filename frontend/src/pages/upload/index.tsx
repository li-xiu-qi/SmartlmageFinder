import React, { useState } from 'react';
import {
  Upload,
  Button,
  Card,
  Form,
  Input,
  Select,
  Switch,
  message,
  Row,
  Col,
  Space,
  Typography,
  Progress,
  Table,
  Divider
} from 'antd';
import { InboxOutlined, CloudUploadOutlined, DeleteOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { imageService, aiService, tagService } from '@/services/api';
import { useNavigate } from 'react-router-dom';

const { Dragger } = Upload;
const { Title, Text } = Typography;
const { Option } = Select;

interface UploadResult {
  success: number;
  fail: number;
  uploadedImages: any[];
  failedImages: {
    filename: string;
    error: string;
  }[];
}

const UploadPage: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  
  // 状态管理
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [tags, setTags] = useState<string[]>([]);
  const [availableTags, setAvailableTags] = useState<{ label: string; value: string }[]>([]);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);

  // 获取标签数据
  React.useEffect(() => {
    const fetchTags = async () => {
      try {
        const response = await tagService.getTags();
        if (response.status === 'success' && response.data) {
          const tagOptions = response.data.tags.map(tag => ({
            label: `${tag.name} (${tag.count})`,
            value: tag.name
          }));
          setAvailableTags(tagOptions);
        }
      } catch (error) {
        console.error('获取标签失败:', error);
      }
    };

    fetchTags();
  }, []);

  // 处理文件列表变化
  const handleFileListChange: UploadProps['onChange'] = ({ fileList }) => {
    setFileList(fileList);
  };

  // 处理文件上传前的检查
  const handleBeforeUpload = (file: File) => {
    // 检查文件类型
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error(`${file.name} 不是有效的图片文件`);
      return Upload.LIST_IGNORE;
    }

    // 检查文件大小
    const isLt50M = file.size / 1024 / 1024 < 50;
    if (!isLt50M) {
      message.error(`图片大小不能超过 50MB，${file.name} 大小超出限制`);
      return Upload.LIST_IGNORE;
    }

    // 返回 false 以阻止自动上传，我们将使用自定义上传按钮
    return false;
  };

  // 处理文件删除
  const handleFileRemove = (file: UploadFile) => {
    setFileList(prev => prev.filter(item => item.uid !== file.uid));
    return true;
  };

  // 上传图片
  const handleUpload = async () => {
    try {
      // 验证表单
      await form.validateFields();
      const values = form.getFieldsValue();
      
      if (fileList.length === 0) {
        message.error('请先选择要上传的图片');
        return;
      }

      setUploading(true);
      setUploadProgress(0);
      
      // 构建上传的文件列表
      const files = fileList.map(file => file.originFileObj as File);
      
      // 构建元数据对象
      const metadata: Record<string, any> = {};
      
      // 添加标签
      if (values.tags && values.tags.length > 0) {
        metadata.tags = values.tags;
      }
      
      // 添加其他元数据
      if (values.location) {
        metadata.location = values.location;
      }
      
      if (values.event) {
        metadata.event = values.event;
      }
      
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 300);

      // 调用上传API
      const response = await imageService.uploadImages(
        files, 
        metadata, 
        values.generateMetadata
      );

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.status === 'success' && response.data) {
        const { uploaded, failed } = response.data;
        setUploadResult({
          success: uploaded.length,
          fail: failed.length,
          uploadedImages: uploaded,
          failedImages: failed
        });
        
        message.success(`成功上传 ${uploaded.length} 张图片${failed.length > 0 ? `，${failed.length} 张上传失败` : ''}`);
      }
    } catch (error) {
      console.error('上传图片失败:', error);
      message.error('上传图片失败');
    } finally {
      setUploading(false);
    }
  };

  // 查看上传结果
  const handleViewUploaded = () => {
    navigate('/images');
  };

  // 重置上传表单
  const handleReset = () => {
    setFileList([]);
    form.resetFields();
    setUploadResult(null);
    setUploadProgress(0);
  };

  // 上传成功的失败列表列定义
  const failedColumns = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
    },
    {
      title: '错误原因',
      dataIndex: 'error',
      key: 'error',
    }
  ];

  return (
    <div className="upload-page">
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          generateMetadata: true,
          detectDuplicates: true,
        }}
      >
        <Card title="上传图片" className="upload-card">
          <Dragger
            fileList={fileList}
            onChange={handleFileListChange}
            beforeUpload={handleBeforeUpload}
            onRemove={handleFileRemove}
            multiple
            listType="picture"
            className="upload-area"
            disabled={uploading}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持单个或批量上传图片，每个文件大小不超过50MB
            </p>
          </Dragger>

          <Divider />

          <Row gutter={16} className="gutter-row">
            <Col xs={24} md={12}>
              <Form.Item 
                label="标签" 
                name="tags"
                tooltip="为所有上传图片添加标签，方便后续管理和搜索"
              >
                <Select
                  mode="tags"
                  style={{ width: '100%' }}
                  placeholder="输入或选择标签"
                  options={availableTags}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item 
                label="拍摄地点" 
                name="location"
                tooltip="为所有上传图片添加拍摄地点信息"
              >
                <Input placeholder="例如：北京、三亚等" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16} className="gutter-row">
            <Col xs={24} md={12}>
              <Form.Item 
                label="事件/场合" 
                name="event"
                tooltip="为所有上传图片添加相关事件信息"
              >
                <Input placeholder="例如：旅行、会议、聚会等" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Form.Item 
                  label="自动分析" 
                  name="generateMetadata" 
                  valuePropName="checked"
                  tooltip="启用后，系统会自动分析图片内容并生成标题、描述和标签"
                >
                  <Switch />
                </Form.Item>
                <Form.Item 
                  label="检测重复" 
                  name="detectDuplicates" 
                  valuePropName="checked"
                  tooltip="启用后，系统会检测上传的图片是否已存在于库中"
                >
                  <Switch />
                </Form.Item>
              </Space>
            </Col>
          </Row>

          <Divider />

          <div style={{ textAlign: 'right' }}>
            <Space>
              <Button onClick={handleReset} disabled={uploading}>
                重置
              </Button>
              <Button
                type="primary"
                onClick={handleUpload}
                loading={uploading}
                icon={<CloudUploadOutlined />}
                disabled={fileList.length === 0}
              >
                {uploading ? '上传中...' : '开始上传'}
              </Button>
            </Space>
          </div>

          {uploading && (
            <div style={{ marginTop: 16 }}>
              <Progress percent={uploadProgress} status="active" />
            </div>
          )}
        </Card>

        {/* 上传结果 */}
        {uploadResult && (
          <Card title="上传结果" style={{ marginTop: 16 }}>
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <Title level={4}>
                共上传 {uploadResult.success + uploadResult.fail} 张图片，
                成功 {uploadResult.success} 张，
                失败 {uploadResult.fail} 张
              </Title>
              
              {uploadResult.failedImages.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <Title level={5}>失败图片列表：</Title>
                  <Table 
                    dataSource={uploadResult.failedImages} 
                    columns={failedColumns} 
                    pagination={false}
                    size="small"
                    rowKey="filename"
                  />
                </div>
              )}
              
              <div style={{ marginTop: 16 }}>
                <Space>
                  <Button type="primary" onClick={handleViewUploaded}>
                    查看所有已上传图片
                  </Button>
                  <Button onClick={handleReset} icon={<DeleteOutlined />}>
                    继续上传
                  </Button>
                </Space>
              </div>
            </div>
          </Card>
        )}
      </Form>
    </div>
  );
};

export default UploadPage;