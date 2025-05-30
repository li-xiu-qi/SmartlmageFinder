import React from 'react';
import { Radio, Space, Select, Button, Divider, Popconfirm } from 'antd';
import { AppstoreOutlined, BarsOutlined, CheckSquareOutlined, DeleteOutlined } from '@ant-design/icons';

const { Option } = Select;

export type ViewMode = 'grid' | 'list';

interface ViewControlsProps {
  total: number;
  viewMode: ViewMode;
  gridColumns: number;
  onViewModeChange: (mode: ViewMode) => void;
  onGridColumnsChange: (columns: number) => void;
  // 多选功能相关
  multiSelectMode?: boolean;
  selectedCount?: number;
  onToggleMultiSelect?: () => void;
  onSelectAll?: () => void;
  onBatchDelete?: () => void;
  batchDeleting?: boolean;
}

/**
 * 视图控制组件
 */
const ViewControls: React.FC<ViewControlsProps> = ({
  total,
  viewMode,
  gridColumns,
  onViewModeChange,
  onGridColumnsChange,
  multiSelectMode = false,
  selectedCount = 0,
  onToggleMultiSelect,
  onSelectAll,
  onBatchDelete,
  batchDeleting = false
}) => {  return (
    <div className="view-controls" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, alignItems: 'center' }}>
      <div>
        <span>共 {total} 张图片</span>
        {multiSelectMode && selectedCount > 0 && (
          <span style={{ marginLeft: 16, color: '#1890ff' }}>
            已选择 {selectedCount} 张图片
          </span>
        )}
      </div>
      <Space>
        {/* 多选功能按钮 */}
        <Button
          type={multiSelectMode ? 'primary' : 'default'}
          icon={<CheckSquareOutlined />}
          onClick={onToggleMultiSelect}
        >
          {multiSelectMode ? '退出多选' : '批量操作'}
        </Button>

        {multiSelectMode && (
          <>
            <Button onClick={onSelectAll}>
              {selectedCount === total ? '取消全选' : '全选'}
            </Button>
            <Popconfirm
              title="确定要删除选中的图片吗？"
              description="此操作不可撤销"
              onConfirm={onBatchDelete}
              okText="确定"
              cancelText="取消"
              disabled={selectedCount === 0}
            >
              <Button
                type="primary"
                danger
                icon={<DeleteOutlined />}
                disabled={selectedCount === 0}
                loading={batchDeleting}
              >
                批量删除 ({selectedCount})
              </Button>
            </Popconfirm>
            <Divider type="vertical" />
          </>
        )}

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
