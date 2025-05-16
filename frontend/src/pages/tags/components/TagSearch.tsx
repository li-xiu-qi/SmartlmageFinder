import React from 'react';
import { Input, Typography } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import '../styles.less';

const { Text } = Typography;

interface TagSearchProps {
  value: string;
  onChange: (value: string) => void;
}

const TagSearch: React.FC<TagSearchProps> = ({ value, onChange }) => {  return (
    <div className="tag-search-container">
      <Input
        placeholder="搜索标签..."
        prefix={<SearchOutlined />}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="tag-search-input"
      />
      <Text type="secondary" className="tag-search-hint">
        输入关键词搜索标签
      </Text>
    </div>
  );
};

export default TagSearch;
