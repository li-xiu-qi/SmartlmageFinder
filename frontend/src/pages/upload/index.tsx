import React, { useState, useEffect } from 'react';
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
  Divider,
  List,
  Modal,
  Tabs
} from 'antd';
import { InboxOutlined, CloudUploadOutlined, DeleteOutlined, EditOutlined, CheckCircleFilled } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { imageService, aiService, tagService } from '@/services/api';
import { useNavigate } from 'react-router-dom';

const { Dragger } = Upload;
const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

interface UploadResult {
  success: number;
  fail: number;
  uploadedImages: any[];
  failedImages: {
    filename: string;
    error: string;
  }[];
}

interface ImageMetadata {
  title?: string;
  description?: string;
  tags: string[];
  location?: string;
  event?: string;
  [key: string]: any;
}

const UploadPage: React.FC = () => {
  const [form] = Form.useForm();
  const [metadataForm] = Form.useForm();
  const navigate = useNavigate();
  
  // 状态管理
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [availableTags, setAvailableTags] = useState<{ label: string; value: string }[]>([]);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [showMetadataModal, setShowMetadataModal] = useState(false);
  const [currentFile, setCurrentFile] = useState<UploadFile | null>(null);
  const [imageMetadataMap, setImageMetadataMap] = useState<Record<string, ImageMetadata>>({});
  // 添加上传状态追踪
  const [hasUploaded, setHasUploaded] = useState(false);
  
  // 通用设置
  const [commonSettings, setCommonSettings] = useState({
    generateMetadata: true,
  });

  // 获取标签数据
  useEffect(() => {
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
    const newList = [...fileList];
    
    // 初始化新添加文件的元数据
    newList.forEach(file => {
      if (!imageMetadataMap[file.uid]) {
        setImageMetadataMap(prev => ({
          ...prev,
          [file.uid]: {
            title: '',
            description: '',
            tags: [],
          }
        }));
      }
    });
    
    setFileList(newList);
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
    // 删除对应的元数据
    setImageMetadataMap(prev => {
      const newMap = {...prev};
      delete newMap[file.uid];
      return newMap;
    });
    return true;
  };

  // 打开编辑元数据模态框
  const openMetadataModal = (file: UploadFile) => {
    setCurrentFile(file);
    
    // 设置表单初始值
    const metadata = imageMetadataMap[file.uid] || {
      title: '',
      description: '',
      tags: [],
      location: '',
      event: '',
    };
    
    metadataForm.setFieldsValue(metadata);
    setShowMetadataModal(true);
  };

  // 保存元数据
  const saveMetadata = () => {
    metadataForm.validateFields().then(values => {
      if (currentFile) {
        // 更新单个文件的元数据
        setImageMetadataMap(prev => ({
          ...prev,
          [currentFile.uid]: {
            ...prev[currentFile.uid],
            ...values,
          }
        }));
        message.success('元数据已更新');
      }
      
      setShowMetadataModal(false);
    });
  };

  // 上传图片
  const handleUpload = async () => {
    try {
      if (fileList.length === 0) {
        message.error('请先选择要上传的图片');
        return;
      }

      // 检查是否已经上传过，防止重复上传
      if (hasUploaded) {
        message.warning('文件已上传，请勿重复上传');
        return;
      }

      setUploading(true);
      setUploadProgress(0);
      
      // 上传成功和失败的记录
      const uploadedImages: any[] = [];
      const failedImages: {filename: string, error: string}[] = [];
      
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.floor(90 / fileList.length);
        });
      }, 500);
      
      // 逐个上传图片
      for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        const metadata = imageMetadataMap[file.uid] || {};
        
        try {
          // 构建元数据对象
          const metadataObj: Record<string, any> = {};
          
          if (metadata.location) {
            metadataObj.location = metadata.location;
          }
          
          if (metadata.event) {
            metadataObj.event = metadata.event;
          }
          
          // 上传单张图片
          const response = await imageService.uploadImages(
            [file.originFileObj as File],
            metadataObj,
            metadata.title,
            metadata.description,
            metadata.tags?.length > 0 ? JSON.stringify(metadata.tags) : undefined,
            commonSettings.generateMetadata
          );
          
          if (response.status === 'success' && response.data) {
            uploadedImages.push(...response.data.uploaded);
          }
        } catch (error) {
          console.error(`上传图片 ${file.name} 失败:`, error);
          failedImages.push({
            filename: file.name,
            error: '上传失败'
          });
        }
        
        // 更新进度
        const progress = Math.floor(((i + 1) / fileList.length) * 90);
        setUploadProgress(progress);
      }
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // 设置上传结果
      setUploadResult({
        success: uploadedImages.length,
        fail: failedImages.length,
        uploadedImages,
        failedImages
      });

      // 标记为已上传
      setHasUploaded(true);
      
      message.success(`成功上传 ${uploadedImages.length} 张图片${failedImages.length > 0 ? `，${failedImages.length} 张上传失败` : ''}`);
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
    setImageMetadataMap({});
    setUploadResult(null);
    setUploadProgress(0);
    // 重置上传状态
    setHasUploaded(false);
  };

  // 更新通用设置
  const handleSettingChange = (key: string, value: boolean) => {
    setCommonSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // 自定义上传列表项
  const customItemRender = (originNode: React.ReactElement, file: UploadFile, fileList: UploadFile[]) => {
    const metadata = imageMetadataMap[file.uid] || {};
    const hasMetadata = metadata.title || metadata.description || (metadata.tags && metadata.tags.length > 0);
    
    return (
      <div className="upload-list-item" style={{ position: 'relative' }}>
        {originNode}
        <div style={{ 
          marginTop: 8, 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'flex-start',
          width: '100%'
        }}>
          {/* 元数据显示区域 - 左对齐 */}
          <div style={{ flex: 1 }}>
            {hasMetadata && (
              <div className="upload-item-metadata-summary" style={{ 
                fontSize: '12px', 
                color: '#666', 
                textAlign: 'left'
              }}>
                {metadata.title && <div><strong>标题:</strong> {metadata.title}</div>}
                {metadata.tags?.length > 0 && (
                  <div><strong>标签:</strong> {metadata.tags.slice(0, 3).join(', ')}{metadata.tags.length > 3 ? '...' : ''}</div>
                )}
              </div>
            )}
          </div>
          
          {/* 编辑按钮 - 右对齐 */}
          <div style={{ marginLeft: 'auto' }}>
            <Button 
              type="link" 
              size="small" 
              icon={<EditOutlined />} 
              onClick={() => openMetadataModal(file)}
              style={{ padding: 0 }}
              disabled={hasUploaded}
            >
              {hasMetadata ? '编辑数据' : '添加数据'}
            </Button>
          </div>
        </div>
      </div>
    );
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
      <Card title="上传图片" className="upload-card">
        <Dragger
          fileList={fileList}
          onChange={handleFileListChange}
          beforeUpload={handleBeforeUpload}
          onRemove={handleFileRemove}
          multiple
          listType="picture"
          className="upload-area"
          disabled={uploading || hasUploaded}
          itemRender={customItemRender}
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

        <div style={{ textAlign: 'right' }}>
          <Space>
            <Button onClick={handleReset} disabled={uploading}>
              重置
            </Button>
            <Button
              type="primary"
              onClick={handleUpload}
              loading={uploading}
              icon={hasUploaded ? <CheckCircleFilled /> : <CloudUploadOutlined />}
              disabled={fileList.length === 0 || hasUploaded}
            >
              {uploading ? '上传中...' : hasUploaded ? '已上传' : '开始上传'}
            </Button>
          </Space>
        </div>

        {uploading && (
          <div style={{ marginTop: 16 }}>
            <Progress percent={uploadProgress} status="active" />
          </div>
        )}

        {/* 元数据编辑模态框 */}
        <Modal
          title={currentFile ? `编辑 ${currentFile.name} 的元数据` : "编辑元数据"}
          open={showMetadataModal}
          onOk={saveMetadata}
          onCancel={() => setShowMetadataModal(false)}
          width={700}
        >
          <Form
            form={metadataForm}
            layout="vertical"
          >
            <Tabs defaultActiveKey="basic">
              <TabPane tab="基本信息" key="basic">
                <Row gutter={16}>
                  <Col span={24}>
                    <Form.Item 
                      label="标题" 
                      name="title"
                    >
                      <Input placeholder="输入图片标题" />
                    </Form.Item>
                  </Col>
                </Row>
                
                <Row gutter={16}>
                  <Col span={24}>
                    <Form.Item 
                      label="描述" 
                      name="description"
                    >
                      <TextArea 
                        rows={4}
                        placeholder="输入图片描述" 
                      />
                    </Form.Item>
                  </Col>
                </Row>
                
                <Row gutter={16}>
                  <Col span={24}>
                    <Form.Item 
                      label="标签" 
                      name="tags"
                    >
                      <Select
                        mode="tags"
                        style={{ width: '100%' }}
                        placeholder="输入或选择标签"
                        options={availableTags}
                      />
                    </Form.Item>
                  </Col>
                </Row>
              </TabPane>
              
              <TabPane tab="额外信息" key="extra">
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item 
                      label="拍摄地点" 
                      name="location"
                    >
                      <Input placeholder="例如：北京、三亚等" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item 
                      label="事件/场合" 
                      name="event"
                    >
                      <Input placeholder="例如：旅行、会议、聚会等" />
                    </Form.Item>
                  </Col>
                </Row>
              </TabPane>
            </Tabs>
          </Form>
        </Modal>
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
    </div>
  );
};

export default UploadPage;