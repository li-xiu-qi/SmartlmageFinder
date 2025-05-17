import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { message, Spin, Drawer } from 'antd';
import { imageService } from '@/services/api';
import { ImageDetail } from '@/types';
import SharedImageDetail from '@/components/shared/SharedImageDetail';
import '../styles/components.less';

/**
 * 图片详情页面
 */
const ImageDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [image, setImage] = useState<ImageDetail | null>(null);
  const [visible, setVisible] = useState(true);

  // 获取图片详情
  useEffect(() => {
    const fetchImageDetail = async () => {
      if (!id || isNaN(Number(id))) {
        message.error('图片ID无效');
        navigate('/images');
        return;
      }

      try {
        setLoading(true);
        const imageId = Number(id);
        const response = await imageService.getImageDetail({ image_id: imageId });
        if (response.status === 'success' && response.data) {
          setImage(response.data);
        } else {
          message.error('获取图片详情失败');
          navigate('/images');
        }
      } catch (error) {
        console.error('获取图片详情失败:', error);
        message.error('获取图片详情失败');
        navigate('/images');
      } finally {
        setLoading(false);
      }
    };

    fetchImageDetail();
  }, [id, navigate]);

  // 处理图片删除
  const handleDelete = async (imageId: number) => {
    try {
      const response = await imageService.deleteImage({ image_id: imageId });
      if (response.status === 'success') {
        message.success('删除成功');
        closeDrawer();
      }
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  // 处理图片更新
  const handleUpdate = (updatedImage: ImageDetail) => {
    setImage(updatedImage);
  };

  // 关闭抽屉
  const closeDrawer = () => {
    setVisible(false);
    setTimeout(() => navigate('/images'), 300); // 等动画结束后导航
  };

  return (
    <Drawer
      title="图片详情"
      placement="right"
      width={window.innerWidth > 768 ? 600 : '100%'}
      onClose={closeDrawer}
      open={visible}
      styles={{
        body: { padding: 0 },
      }}
      className="image-detail-drawer"
    >
      {loading ? (
        <div style={{ padding: 24, textAlign: 'center' }}>
          <Spin size="large" />
        </div>
      ) : (        image && (
          <SharedImageDetail
            image={image}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
            onClose={closeDrawer}
          />
        )
      )}
    </Drawer>
  );
};

export default ImageDetailPage;

