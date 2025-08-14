import React, { useState } from 'react';
import { Typography, Button, Input, Space } from 'antd';
import { EditOutlined, SaveOutlined, CloseOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

interface EditableFieldProps {
  value: string;
  onSave: (newValue: string) => Promise<void>;
  title?: boolean;
  loading?: boolean;
}

/**
 * 可编辑字段组件
 */
const EditableField: React.FC<EditableFieldProps> = ({
  value,
  onSave,
  title = false,
  loading = false
}) => {
  const [editing, setEditing] = useState(false);
  const [inputValue, setInputValue] = useState(value);

  const handleSave = async () => {
    if (title && inputValue.trim() === '') {
      return; // 如果是标题且为空，不保存
    }
    
    await onSave(inputValue);
    setEditing(false);
  };

  const handleCancel = () => {
    setInputValue(value);
    setEditing(false);
  };

  if (editing) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: title ? 'row' : 'column', 
        gap: 8, 
        marginBottom: 16,
        alignItems: title ? 'center' : 'start'
      }}>
        {title ? (
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            style={{ marginRight: 8 }}
          />
        ) : (
          <Input.TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            rows={4}
          />
        )}
        
        <Space>
          <Button 
            icon={<SaveOutlined />} 
            type="primary" 
            onClick={handleSave}
            loading={loading}
          />
          <Button 
            icon={<CloseOutlined />} 
            onClick={handleCancel}
          />
        </Space>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', alignItems: title ? 'center' : 'start', marginBottom: 16 }}>
      {title ? (
        <Title level={4} style={{ margin: 0, flex: 1 }}>
          {value}
        </Title>
      ) : (
        <Paragraph style={{ flex: 1, margin: 0 }}>
          {value || '暂无描述'}
        </Paragraph>
      )}
      <Button 
        icon={<EditOutlined />} 
        type="link" 
        onClick={() => setEditing(true)}
        disabled={loading}
      />
    </div>
  );
};

export default EditableField;
