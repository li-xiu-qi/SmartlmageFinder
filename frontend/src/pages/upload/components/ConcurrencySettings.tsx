import React from 'react';
import { Card, InputNumber, Switch, Space, Typography, Tooltip } from 'antd';
import { SettingOutlined, InfoCircleOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface ConcurrencySettingsProps {
  concurrentAnalysis: boolean;
  concurrentLimit: number;
  onConcurrentAnalysisChange: (enabled: boolean) => void;
  onConcurrentLimitChange: (limit: number) => void;
  disabled?: boolean;
}

/**
 * 并发分析设置组件
 * 允许用户控制是否启用并发分析以及并发数量限制
 */
const ConcurrencySettings: React.FC<ConcurrencySettingsProps> = ({
  concurrentAnalysis,
  concurrentLimit,
  onConcurrentAnalysisChange,
  onConcurrentLimitChange,
  disabled = false
}) => {
  return (
    <Card
      size="small"
      title={
        <Space>
          <SettingOutlined />
          <Text>AI分析设置</Text>
        </Space>
      }
      style={{ marginBottom: 16 }}
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        {/* 并发分析开关 */}
        <Space align="center">
          <Switch
            checked={concurrentAnalysis}
            onChange={onConcurrentAnalysisChange}
            disabled={disabled}
          />
          <Text>启用并发分析</Text>
          <Tooltip 
            title="启用并发分析可以同时处理多张图片，提高分析速度，但会增加服务器负载"
            getPopupContainer={(trigger) => trigger.parentElement || document.body}
          >
            <InfoCircleOutlined style={{ color: '#1890ff' }} />
          </Tooltip>
        </Space>

        {/* 并发数量设置 */}
        <Space align="center" style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Text>并发数量:</Text>
            <Tooltip 
              title="同时处理的图片数量。建议设置为1-10之间，数量越大速度越快但服务器压力越大"
              getPopupContainer={(trigger) => trigger.parentElement || document.body}
            >
              <InfoCircleOutlined style={{ color: '#1890ff' }} />
            </Tooltip>
          </Space>
          <InputNumber
            min={1}
            max={10}
            value={concurrentLimit}
            onChange={(value) => onConcurrentLimitChange(value || 1)}
            disabled={disabled || !concurrentAnalysis}
            style={{ width: 80 }}
          />
        </Space>

        {/* 说明文本 */}
        <div style={{ fontSize: '12px', color: '#666', marginTop: 8 }}>
          {concurrentAnalysis
            ? `当前设置：同时分析 ${concurrentLimit} 张图片`
            : '当前设置：逐张分析图片（串行模式）'
          }
        </div>
      </Space>
    </Card>
  );
};

export default ConcurrencySettings;
