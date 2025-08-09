import React, { useState } from 'react';
import { Row, Col, Card, Empty, Drawer, Spin, message } from 'antd';
import { RecentImagesProps } from '../../types';
import { imageService } from '@/services/api';
import { ImageDetail } from '@/types/image';
import SharedImageDetail from '@/components/SharedImageDetail';
import './styles.less';

/**
 * 最近上传图片组件
 * 展示最近上传的图片列表
 * 点击图片时直接在当前页面的侧边栏中展示图片详情
 */
const RecentImages: React.FC<RecentImagesProps> = ({ images }) => {
  const [selectedImage, setSelectedImage] = useState<ImageDetail | null>(null);
  const [drawerVisible, setDrawerVisible] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  // 处理图片点击，加载详情
  const handleImageClick = async (imageId: number) => {
    try {
      setLoading(true);
      const response = await imageService.getImageDetail({ image_id: imageId });
      if (response.status === 'success' && response.data) {
        setSelectedImage(response.data);
        setDrawerVisible(true);
      } else {
        message.error('获取图片详情失败');
      }
    } catch (error) {
      console.error('获取图片详情失败:', error);
      message.error('获取图片详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理侧边栏关闭
  const handleDrawerClose = () => {
    setDrawerVisible(false);
  };

  // 处理图片更新
  const handleUpdate = (updatedImage: ImageDetail) => {
    setSelectedImage(updatedImage);
  };

  // 处理图片删除
  const handleDelete = async (imageId: number) => {
    try {
      const response = await imageService.deleteImage({ image_id: imageId });
      if (response.status === 'success') {
        message.success('删除成功');
        handleDrawerClose();
      }
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };  return (
    <div className="recent-images">
      <h2 className="section-title">最近上传图片</h2>
      {images.length > 0 ? (
        <Row gutter={[16, 16]}>
          {/* 遍历images数组，为每个图片创建一个Card组件 */}
          {images.map(image => (
            <Col xs={12} sm={8} md={6} key={image.id}>
              {/* 将Link替换为普通Card，添加onClick事件 */}
              <Card
                hoverable
                onClick={() => handleImageClick(image.id)}
                cover={
                  <div className="image-cover">
                    {/* 图片内容，点击时会触发handleImageClick打开侧边栏 */}
                    <img alt={image.title} src={(image as any).public_url || image.filepath} />
                  </div>
                }
                className="image-card"
              >
                {/* Card.Meta用于展示图片标题和创建日期 */}
                <Card.Meta
                  title={image.title}
                  description={
                    <span className="image-meta">
                      {/* 格式化并显示图片上传的日期 */}
                      {new Date(image.created_at).toLocaleDateString()}
                    </span>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      ) : (
        <Empty description="暂无图片" />
      )}      {/* 添加图片详情侧边栏 */}
      <Drawer
        title="图片详情"
        placement="right"
        width={window.innerWidth > 768 ? 600 : '100%'}
        onClose={handleDrawerClose}
        open={drawerVisible}
        className="image-detail-drawer"
      >{loading ? (
          <div className="loading-container">
            <Spin size="large" />
          </div>
        ) : (
          selectedImage && (
            <SharedImageDetail
              image={selectedImage}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
              onClose={handleDrawerClose}
            />
          )
        )}
      </Drawer>
    </div>
  );
};

export default RecentImages;
