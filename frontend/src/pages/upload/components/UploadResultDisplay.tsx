import React from 'react';
import { Card, Button, Result, Typography, List, Badge, Space } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, FileImageOutlined } from '@ant-design/icons';
import { UploadResult } from '../types';

const { Text, Paragraph } = Typography;

interface UploadResultDisplayProps {
  result: UploadResult | null; // 上传结果数据
  onViewUploaded: () => void; // 查看已上传图片的回调
  onReset: () => void; // 重置上传状态的回调
}

/**
 * 上传结果显示组件
 * 展示批量上传操作的最终结果，包括成功和失败的统计信息
 */
const UploadResultDisplay: React.FC<UploadResultDisplayProps> = ({
  result,
  onViewUploaded,
  onReset
}) => {
  // 如果没有上传结果，不显示任何内容
  if (!result) {
    return null;
  }

  // 根据上传结果的整体状态呈现不同的视觉展示
  const renderResultStatus = () => {
    switch (result.overallStatus) {
      case 'success':
        return {
          status: 'success' as const,
          title: '图片上传成功',
          icon: <CheckCircleOutlined />,
          subTitle: `共上传 ${result.successCount} 张图片`,
        };
      case 'partial':
        return {
          status: 'warning' as const,
          title: '部分图片上传成功',
          icon: null, // 使用默认图标
          subTitle: `成功: ${result.successCount} 张，失败: ${result.failureCount} 张`,
        };
      case 'failure':
        return {
          status: 'error' as const,
          title: '图片上传失败',
          icon: <CloseCircleOutlined />,
          subTitle: `所有 ${result.failureCount} 张图片上传均失败`,
        };
      default:
        return {
          status: 'info' as const,
          title: '上传完成',
          icon: null,
          subTitle: '请查看详细结果',
        };
    }
  };

  const statusInfo = renderResultStatus();

  return (
    <Card title="上传结果" className="upload-result-card" style={{ marginTop: 16 }}>
      <Result
        status={statusInfo.status}
        title={statusInfo.title}
        subTitle={statusInfo.subTitle}
        icon={statusInfo.icon}
        extra={[
          <Button 
            type="primary" 
            key="view" 
            onClick={onViewUploaded}
            disabled={result.successCount === 0}
          >
            查看已上传图片
          </Button>,
          <Button 
            key="reset" 
            onClick={onReset}
          >
            重新上传
          </Button>,
        ]}
      >
        {/* 显示每个文件的上传结果 */}
        {result.items.length > 0 && (
          <div className="upload-result-details">
            <Paragraph>详细结果：</Paragraph>
            <List
              size="small"
              bordered
              dataSource={result.items}
              renderItem={item => (
                <List.Item>
                  <Space>
                    <FileImageOutlined />
                    <Text>{item.fileName}</Text>
                    {item.success ? (
                      <Badge status="success" text="上传成功" />
                    ) : (
                      <Badge status="error" text={`上传失败: ${item.message || '未知错误'}`} />
                    )}
                  </Space>
                </List.Item>
              )}
            />
          </div>
        )}
      </Result>
    </Card>
  );
};

export default UploadResultDisplay;
