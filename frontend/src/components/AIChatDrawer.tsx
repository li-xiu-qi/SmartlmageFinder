import React, { useState } from 'react';
import { Drawer, Input, Button, Space, Typography, List, Avatar, Tag, Alert, Spin, message, Collapse, Badge } from 'antd';
import ReactMarkdown from 'react-markdown';
import { RobotOutlined, SendOutlined, StopOutlined } from '@ant-design/icons';
import { useChatRecommendation } from '@/hooks/useChatRecommendation';
import SharedImageDetail from '@/components/SharedImageDetail';
import imageService from '@/services/imageService';
import { ImageModel } from '@/types/models';

const { TextArea } = Input;
const { Text } = Typography;

interface AIChatDrawerProps {
  open: boolean;
  onClose: () => void;
}

const AIChatDrawer: React.FC<AIChatDrawerProps> = ({ open, onClose }) => {
  const { conversationId, messages, loading, error, start, cancel } = useChatRecommendation();
  const [input, setInput] = useState('');
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailImage, setDetailImage] = useState<ImageModel | null>(null);

  const openDetail = async (id: number) => {
    try {
      setDetailLoading(true);
      setDetailOpen(true);
      const resp = await imageService.getImageDetail({ image_id: id });
      if (resp.status === 'success' && resp.data) {
        setDetailImage(resp.data as ImageModel);
      } else {
        message.error(resp.message || '获取图片详情失败');
      }
    } catch (e:any) {
      message.error(e.message || '加载失败');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDetailUpdate = (img: ImageModel) => {
    setDetailImage(img);
  };

  const handleDetailDelete = (_id: number) => {
    // 简单处理：关闭详情抽屉
    setDetailOpen(false);
    setDetailImage(null);
    message.success('图片已删除');
  };

  const handleSend = () => {
    if (!input.trim()) return;
    start(input.trim());
    setInput('');
  };

  return (
    <Drawer
      title={<Space><RobotOutlined />AI 对话推荐 {conversationId && <Text type="secondary" style={{ fontSize:12 }}>#{conversationId.slice(0,8)}</Text>}</Space>}
      placement="right"
      width={520}
      onClose={onClose}
      open={open}
      destroyOnClose
      extra={
        loading ? <Button size="small" icon={<StopOutlined />} onClick={cancel}>取消</Button> : null
      }
    >
      <div style={{ display:'flex', flexDirection:'column', height:'100%' }}>
        <div style={{ flex:1, overflowY:'auto', paddingRight:8 }}>
          <List
            dataSource={messages}
            renderItem={(m, idx) => (
              <List.Item key={idx} style={{ alignItems:'flex-start' }}>
                <div style={{ width:'100%' }}>
                  <div style={{ fontSize:12, marginBottom:4 }}>
                    <Tag color={m.role === 'user' ? 'blue' : m.role === 'assistant' ? 'green' : 'default'}>{m.role}</Tag>
                  </div>
                  <div style={{ lineHeight:1.5 }}>
                    {m.role === 'assistant' ? (
                      <ReactMarkdown
                        components={{
                          img: (props:any) => <img {...props} style={{ maxWidth:'100%', borderRadius:4 }} />,
                          p: (props:any) => <p style={{ marginBottom:8 }} {...props} />,
                          li: (props:any) => <li style={{ marginBottom:4 }} {...props} />,
                        }}
                      >{m.content}</ReactMarkdown>
                    ) : (
                      <div style={{ whiteSpace:'pre-wrap' }}>{m.content}</div>
                    )}
                  </div>
                  {m.image_ids && m.image_ids.length > 0 && (
                    <div style={{ marginTop:6 }}>
                      <Text type="secondary" style={{ fontSize:12 }}>选中图片: {m.image_ids.join(', ')}</Text>
                    </div>
                  )}
                </div>
              </List.Item>
            )}
          />
          {error && <Alert type="error" message={error} showIcon style={{ marginTop:8 }} />}
          {/* 每轮 assistant 消息自带可折叠图片推荐 */}
          <div style={{ marginTop:12 }}>
            {messages.filter(m=>m.role==='assistant' && m.images_brief && m.images_brief.length>0).map((m,idx)=> {
              const panelKey = `rec-${idx}-${m.image_ids?.join('-')||''}`;
              return (
                <Collapse
                  key={panelKey}
                  style={{ marginBottom:8, background:'#fafafa' }}
                  items={[{
                    key: '1',
                    label: <Space size={6}><span>本轮推荐图片</span><Badge count={m.images_brief!.length} style={{ backgroundColor:'#52c41a' }} /></Space>,
                    children: (
                      <List
                        size="small"
                        dataSource={m.images_brief}
                        renderItem={(img:any) => {
                          const url = img.public_url || (img.filepath ? img.filepath.replace(/\\/g,'/') : undefined);
                          return (
                            <List.Item key={img.id} style={{ cursor:'pointer' }} onClick={()=> openDetail(img.id)}>
                              <List.Item.Meta
                                avatar={<Avatar shape="square" size={48} src={url} style={{ objectFit:'cover' }} />}
                                title={<span>{img.title || `图片#${img.id}`} {img.score !== undefined && <Text type="secondary" style={{ fontSize:12 }}>({(img.score*100).toFixed(1)}%)</Text>}</span>}
                                description={img.tags && img.tags.length > 0 && img.tags.slice(0,4).map((t:string)=> <Tag key={t}>{t}</Tag>)}
                              />
                            </List.Item>
                          );
                        }}
                      />
                    )
                  }]} 
                  size="small"
                  bordered={false}
                  collapsible="icon"
                  defaultActiveKey={[]}
                />
              );
            })}
          </div>
        </div>
        <div style={{ marginTop:12 }}>
          <TextArea
            rows={3}
            placeholder="输入你的需求，例如：找一些有海滩日落的照片"
            value={input}
            onChange={(e)=>setInput(e.target.value)}
            onPressEnter={(e)=>{ if(!e.shiftKey){ e.preventDefault(); handleSend(); } }}
          />
          <div style={{ marginTop:8, textAlign:'right' }}>
            <Space>
              <Button type="primary" icon={<SendOutlined />} loading={loading} onClick={handleSend}>发送</Button>
            </Space>
          </div>
        </div>
      </div>
      <Drawer
        title={detailImage ? detailImage.title || '图片详情' : '图片详情'}
        open={detailOpen}
        width={600}
        destroyOnClose
        onClose={()=> { setDetailOpen(false); setDetailImage(null); }}
      >
        {detailLoading && <Spin />}
        {!detailLoading && detailImage && (
          <SharedImageDetail
            image={detailImage}
            onUpdate={handleDetailUpdate as any}
            onDelete={handleDetailDelete}
            onClose={()=> { setDetailOpen(false); setDetailImage(null); }}
          />
        )}
      </Drawer>
    </Drawer>
  );
};

export default AIChatDrawer;
