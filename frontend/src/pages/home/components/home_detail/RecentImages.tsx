import React from 'react';
import { Row, Col, Card, Empty } from 'antd';
import { Link } from 'react-router-dom';
import { RecentImagesProps } from '../../types';

/**
 * 最近上传图片组件
 * 展示最近上传的图片列表
 */
const RecentImages: React.FC<RecentImagesProps> = ({ images }) => {
  return (
    <div className="recent-images">
      <h2 className="section-title">最近上传图片</h2>
      {images.length > 0 ? (
        <Row gutter={[16, 16]}>
          {images.map(image => (
            <Col xs={12} sm={8} md={6} key={image.id}>
              <Link to={`/images/${image.id}`}>
                <Card
                  hoverable
                  cover={
                    <div className="image-cover">
                      <img alt={image.title} src={image.filepath} />
                    </div>
                  }
                  className="image-card"
                >
                  <Card.Meta
                    title={image.title}
                    description={
                      <span className="image-meta">
                        {new Date(image.created_at).toLocaleDateString()}
                      </span>
                    }
                  />
                </Card>
              </Link>
            </Col>
          ))}
        </Row>
      ) : (
        <Empty description="暂无图片" />
      )}
    </div>
  );
};

export default RecentImages;
