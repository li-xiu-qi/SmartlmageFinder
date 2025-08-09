import React, { useState, useCallback, useRef } from 'react';
import { Drawer, Input, Button, Space, Typography, List, Avatar, Tag, Alert, Spin, message, Collapse, Badge, Modal } from 'antd';
import ReactMarkdown from 'react-markdown';
import { RobotOutlined, SendOutlined, StopOutlined, ReloadOutlined } from '@ant-design/icons';
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
  const { conversationId, messages, loading, error, start, cancel, reset } = useChatRecommendation();
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

  // 已刷新过的消息索引集合，防止重复请求
  const refreshedRef = useRef<Set<number>>(new Set());
  const [refreshingMsgIndex, setRefreshingMsgIndex] = useState<number | null>(null);
  const [refreshedBriefMap, setRefreshedBriefMap] = useState<Record<number, any[]>>({});

  const refreshImagesBrief = useCallback(async (msgIndex: number, imageIds: number[]|undefined, originalBrief: any[]|undefined) => {
    if (!imageIds || imageIds.length === 0) return;
    if (refreshedRef.current.has(msgIndex)) return; // 已刷新
    setRefreshingMsgIndex(msgIndex);
    try {
      const updated: any[] = [];
      for (const id of imageIds) {
        try {
          const resp = await imageService.getImageDetail({ image_id: id });
          const fallback = originalBrief?.find(b=> b.id === id);
          if ((resp as any).status === 'success' && (resp as any).data) {
            const detail = (resp as any).data;
            updated.push({ ...detail, score: fallback?.score ?? detail.score });
          } else if ((resp as any).data) {
            const detail = (resp as any).data;
            updated.push({ ...detail, score: fallback?.score ?? detail.score });
          } else if (fallback) {
            updated.push(fallback);
          }
        } catch (e) {
          // 回退到原始 brief 中的该条
          const fallback = originalBrief?.find(b=> b.id === id);
          if (fallback) updated.push(fallback);
        }
      }
      if (updated.length > 0) {
        setRefreshedBriefMap(prev => ({ ...prev, [msgIndex]: updated }));
      }
      refreshedRef.current.add(msgIndex);
    } finally {
      setRefreshingMsgIndex(null);
    }
  }, []);

  return (
    <Drawer
      title={<Space><RobotOutlined />AI 对话推荐 {conversationId && <Text type="secondary" style={{ fontSize:12 }}>#{conversationId.slice(0,8)}</Text>}</Space>}
      placement="right"
      width={520}
      onClose={onClose}
      open={open}
      destroyOnClose
      extra={
        <Space>
          <Button size="small" icon={<ReloadOutlined />} disabled={loading} onClick={()=>{
            if(messages.length===0){ reset(); return; }
            Modal.confirm({
              title: '确认新建会话',
              content: '将清空当前对话记录，确定要继续吗？',
              okText: '确定',
              cancelText: '取消',
              onOk: () => { reset(); }
            });
          }}>新建会话</Button>
          {loading && <Button size="small" icon={<StopOutlined />} onClick={cancel}>取消</Button>}
        </Space>
      }
    >
      <div style={{ display:'flex', flexDirection:'column', height:'100%' }}>
        <div style={{ flex:1, overflowY:'auto', paddingRight:8 }}>
          <List
            dataSource={messages}
            renderItem={(m, idx) => {
              const brief = refreshedBriefMap[idx] || m.images_brief;
              return (
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
                    {m.role==='assistant' && brief && brief.length>0 && (
                      <div style={{ marginTop:8 }}>
                        <Collapse
                          key={`rec-${idx}`}
                          style={{ background:'#fafafa', borderRadius:4 }}
                          items={[{
                            key:'1',
                            label:(
                              <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',width:'100%',padding:'4px 4px',cursor:'pointer'}}>
                                <Space size={6} wrap>
                                  <span style={{ fontWeight:500 }}>本轮推荐图片</span>
                                  <Badge count={brief.length} style={{ backgroundColor:'#52c41a' }} />
                                  {/* 每条图片自身会展示相似度，在标题不再单独显示 */}
                                  {refreshingMsgIndex===idx && <Spin size="small" />}
                                </Space>
                              </div>
                            ),
                            children:(
                              <List
                                size="small"
                                dataSource={brief}
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
                          defaultActiveKey={[]}
                          expandIconPosition="end"
                          onChange={(keys)=>{ if(keys.length>0){ refreshImagesBrief(idx, m.image_ids, m.images_brief);} }}
                        />
                      </div>
                    )}
                  </div>
                </List.Item>
              );
            }}
          />
          {error && <Alert type="error" message={error} showIcon style={{ marginTop:8 }} />}
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
