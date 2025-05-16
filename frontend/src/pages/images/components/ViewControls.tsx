import React from 'react';
import { Radio, Space, Select } from 'antd';
import { AppstoreOutlined, BarsOutlined } from '@ant-design/icons';

const { Option } = Select;

export type ViewMode = 'grid' | 'list';

interface ViewControlsProps {
  total: number;
  viewMode: ViewMode;
  gridColumns: number;
  onViewModeChange: (mode: ViewMode) => void;
  onGridColumnsChange: (columns: number) => void;
}

/**
 * 视图控制组件
 */
const ViewControls: React.FC<ViewControlsProps> = ({
  total,
  viewMode,
  gridColumns,
  onViewModeChange,
  onGridColumnsChange
}) => {
  return (
    <div className="view-controls" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, alignItems: 'center' }}>
      <div>
        <span>共 {total} 张图片</span>
      </div>
      <Space>
        <Radio.Group 
          value={viewMode} 
          onChange={e => onViewModeChange(e.target.value)}
        >
          <Radio.Button value="grid"><AppstoreOutlined /> 网格</Radio.Button>
          <Radio.Button value="list"><BarsOutlined /> 列表</Radio.Button>
        </Radio.Group>
        
        {viewMode === 'grid' && (
          <Select 
            value={gridColumns} 
            onChange={onGridColumnsChange} 
            style={{ width: 120 }}
          >
            <Option value={1}>1 列</Option>
            <Option value={2}>2 列</Option>
            <Option value={3}>3 列</Option>
            <Option value={4}>4 列</Option>
          </Select>
        )}
      </Space>
    </div>
  );
};

export default ViewControls;
