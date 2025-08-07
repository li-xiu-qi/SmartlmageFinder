import React, { useState } from 'react';
import { Typography, Descriptions, Button, Modal, Form, Input, Space, message } from 'antd';
import { EditOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons';

const { Title } = Typography;

interface MetadataItem {
  key: string;
  value: string;
}

interface MetadataSectionProps {
  metadata: Record<string, any>; // 保持 any 以处理各种可能的元数据值类型
  onMetadataUpdate: (updatedMetadata: Record<string, string>) => Promise<void>; // 修改 Record<string, any> 为 Record<string, string>
  loading?: boolean;
}

/**
 * 元数据展示组件
 */
const MetadataSection: React.FC<MetadataSectionProps> = ({ metadata, onMetadataUpdate, loading }) => {
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [form] = Form.useForm< { metadata: MetadataItem[] }>();

  const showEditModal = () => {
    const currentMetadataArray: MetadataItem[] = Object.entries(metadata || {}).map(([key, value]) => ({ key, value: String(value) }));
    form.setFieldsValue({ metadata: currentMetadataArray });
    setIsEditModalVisible(true);
  };

  const handleCancel = () => {
    setIsEditModalVisible(false);
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      const updatedMetadataObject: Record<string, string> = {}; // 修改 Record<string, any> 为 Record<string, string>
      let hasDuplicateKeys = false;
      const keys = new Set<string>();

      if (values.metadata && Array.isArray(values.metadata)) {
        for (const item of values.metadata) {
          if (item && typeof item.key === 'string' && item.key.trim() !== '') {
            const trimmedKey = item.key.trim();
            if (keys.has(trimmedKey)) {
              hasDuplicateKeys = true;
              break;
            }
            keys.add(trimmedKey);
            updatedMetadataObject[trimmedKey] = typeof item.value === 'undefined' ? '' : String(item.value); // 确保值为字符串
          } else if (item && (typeof item.key !== 'string' || item.key.trim() === '') && typeof item.value !== 'undefined' && String(item.value).trim() !== '') {
            // 如果键为空但值不为空，则校验失败
            // Form.Item 的 rules 应该已经处理了键为空的情况，但这里可以作为额外的保险
            message.error('元数据项的键不能为空。');
            return;
          }
        }
      }

      if (hasDuplicateKeys) {
        message.error('元数据中存在重复的键，请修改后再保存。');
        return;
      }

      await onMetadataUpdate(updatedMetadataObject);
      setIsEditModalVisible(false);
    } catch (errorInfo) {
      // antd Form.validateFields() 会在校验失败时抛出错误，其中包含错误信息
      // 通常不需要额外打印 console.error，除非需要更详细的调试
      // message.error('保存元数据失败，请检查表单输入。');
      console.log('表单校验失败:', errorInfo);
    }
  };

  const metadataEntries = Object.entries(metadata || {});

  return (
    <div className="detail-section">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={5} className="section-title" style={{ marginBottom: metadataEntries.length > 0 ? 'inherit' : 0 }}>元数据</Title>
        <Button
          icon={<EditOutlined />}
          onClick={showEditModal}
          loading={loading}
          size="small"
          type="link"
        >
          编辑
        </Button>
      </div>
      {metadataEntries.length === 0 ? (
        <p>暂无元数据</p>
      ) : (
        <Descriptions bordered column={1} size="small" style={{ marginTop: '8px' }}>
          {metadataEntries.map(([key, value]) => (
            <Descriptions.Item key={key} label={key}>
              {String(value)} {/* 确保值为字符串 */}
            </Descriptions.Item>
          ))}
        </Descriptions>
      )}

      <Modal
        title="编辑元数据"
        open={isEditModalVisible}
        onOk={handleOk}
        onCancel={handleCancel}
        confirmLoading={loading}
        width={600}
        destroyOnHidden // 关闭时销毁 Modal 里的子元素，确保表单状态正确重置
      >
        <Form form={form} name="editable_metadata_form" autoComplete="off">
          <Form.List name="metadata">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                    <Form.Item
                      {...restField}
                      name={[name, 'key']}
                      rules={[
                        { required: true, message: '请输入键' },
                        { whitespace: true, message: '键不能仅由空白字符组成' }, // 替换了原有的 pattern 规则
                        {
                          validator: async (_, value) => {
                            const allItems = form.getFieldValue('metadata') || [];
                            const currentKeys = allItems.map((item: MetadataItem) => item?.key?.trim()).filter(Boolean);
                            if (value && currentKeys.filter((k: string) => k === value.trim()).length > 1) {
                              return Promise.reject(new Error('键不能重复'));
                            }
                            return Promise.resolve();
                          },
                        },
                      ]}
                      style={{ width: '200px' }}
                    >
                      <Input placeholder="键 (Key)" />
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, 'value']}
                      // 允许值为空字符串，所以不需要 required: true
                      style={{ flex: 1 }}
                    >
                      <Input placeholder="值 (Value)" />
                    </Form.Item>
                    <DeleteOutlined onClick={() => remove(name)} style={{ color: 'red', cursor: 'pointer' }}/>
                  </Space>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add({ key: '', value: '' })} block icon={<PlusOutlined />}>
                    添加元数据项
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>
        </Form>
      </Modal>
    </div>
  );
};

export default MetadataSection;
