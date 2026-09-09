import React, { useEffect, useMemo } from 'react';
import { Card, Form, Select, Row, Col, Tooltip, Skeleton, Input, FormInstance } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { SystemStatusData } from '@/types/system';

const { Option } = Select;

interface ModelSettingsProps {
  systemStatus: SystemStatusData | null;
  loading?: boolean;
  form: FormInstance; // 必须传入父组件表单实例
}

const ModelSettings: React.FC<ModelSettingsProps> = ({ systemStatus, loading = false, form }) => {
  // 从系统状态获取可用的模型列表和当前向量模型
  const availableModels = useMemo(() => {
    return systemStatus?.components.multimodal_api.available_models || [];
  }, [systemStatus?.components.multimodal_api.available_models]);
  
  const hasAvailableModels = availableModels.length > 0;
  
  // 获取当前使用的视觉模型
  const currentVisionModel = systemStatus?.components.multimodal_api.model || '';
  
  // 仅在开发环境下输出调试信息
  if (import.meta.env.DEV) {
    console.log('ModelSettings 组件中的 systemStatus:', systemStatus);
    console.log('当前视觉模型:', currentVisionModel);
  }

  // 获取当前使用的向量模型路径和维度
  const currentVectorModel = systemStatus?.models?.embedding_model || '';
  const embeddingDimension = systemStatus?.models?.embedding_dimension;

  // 当模型信息变化时更新表单字段值
  useEffect(() => {
    if (!loading) {
      // 如果向量模型路径存在且不在加载中，更新表单字段值
      if (currentVectorModel) {
        form.setFieldValue(['model', 'vectorModel'], currentVectorModel);
      }
      
      // 如果视觉模型存在，设置视觉模型字段的值
      if (currentVisionModel) {
        form.setFieldValue(['model', 'visionModel'], currentVisionModel);
      }
      
      // 设置可用模型列表的值
      if (availableModels && availableModels.length > 0) {
        form.setFieldValue(['model', 'availableModels'], availableModels);
      } else {
        // 如果没有可用模型，设置默认值
        form.setFieldValue(['model', 'availableModels'], [
          'Qwen/Qwen2.5-VL-32B-Instruct',
          'Pro/Qwen/Qwen2.5-VL-7B-Instruct'
        ]);
      }
    }
  }, [currentVectorModel, currentVisionModel, availableModels, form, loading]);

  return (
    <Card
      title={
        <span>
          模型设置
          <Tooltip 
            title="配置用于图像分析和向量嵌入的AI模型"
            getPopupContainer={(trigger) => trigger.parentElement || document.body}
          >
            <InfoCircleOutlined style={{ marginLeft: 8, color: 'hsl(var(--primary))' }} />
          </Tooltip>
        </span>
      }
      style={{ marginBottom: 16 }}
    >
      {/* 移除调试信息在页面上的直接显示 */}
      
      {loading ? (
        <Skeleton active paragraph={{ rows: 3 }} />
      ) : (
        <>
          <Row gutter={24}>
            <Col span={24}>
              <Form.Item
                label="向量模型路径"
                name={['model', 'vectorModel']}
                initialValue={currentVectorModel}
                rules={[{ required: true, message: '请输入向量模型路径' }]}
                tooltip="用于生成文本和图像嵌入的模型的路径，支持本地路径或Hugging Face模型ID"
                extra={embeddingDimension ? `当前模型嵌入维度：${embeddingDimension}` : null}
              >
                <Input
                  placeholder="输入向量模型路径或模型ID"
                  disabled={loading}
                  title={currentVectorModel}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                label="视觉模型"
                name={['model', 'visionModel']}
                initialValue={currentVisionModel}
                rules={[{ required: true, message: '请选择视觉模型' }]}
                tooltip="用于图像识别和多模态处理的模型，影响图像分析的准确度"
              >
                <Select
                  placeholder="选择视觉模型"
                  disabled={loading}
                  loading={loading}
                  notFoundContent={!hasAvailableModels ? "目前无可用模型" : null}
                >
                  {/* 优先显示当前选中的模型 */}
                  {currentVisionModel && (
                    <Option key={`current-${currentVisionModel}`} value={currentVisionModel}>{currentVisionModel}</Option>
                  )}
                  
                  {/* 显示其他可用模型 */}
                  {hasAvailableModels && 
                    availableModels
                      .filter(model => model !== currentVisionModel)
                      .map((model: string) => (
                        <Option key={model} value={model}>{model}</Option>
                      ))
                  }
                  
                  {/* 如果没有可用模型且当前也没有选中模型，显示默认选项 */}
                  {!hasAvailableModels && !currentVisionModel && (
                    <>
                      <Option value="Qwen/Qwen2.5-VL-32B-Instruct">Qwen2.5-VL-32B-Instruct</Option>
                      <Option value="Pro/Qwen/Qwen2.5-VL-7B-Instruct">Qwen2.5-VL-7B-Instruct</Option>
                    </>
                  )}
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                label="可用视觉模型列表"
                name={['model', 'availableModels']}
                initialValue={availableModels}
                tooltip="可供选择的视觉模型列表。根据您使用的API提供商不同，可用模型也会有所不同。"
                extra="输入模型ID并按回车添加，点击标签可删除模型"
              >
                <Select
                  mode="tags"
                  placeholder="输入模型ID并按回车添加，例如: Qwen/Qwen2.5-VL-32B-Instruct"
                  disabled={loading}
                  style={{ width: '100%' }}
                  tokenSeparators={[',']}
                />
              </Form.Item>
            </Col>
          </Row>
        </>
      )}
    </Card>
  );
};

export default ModelSettings;
