import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, Statistic, Row, Col, Tag, Typography, Spin, Alert, Progress, Space, Tooltip } from 'antd';
import { 
  ClockCircleOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  SyncOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import systemService from '@/services/systemService';
import { RuntimeInfo } from '@/types/system';
import './SystemRuntime.css';

const { Text } = Typography;

const SystemRuntime: React.FC = () => {  const [runtime, setRuntime] = useState<RuntimeInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdateTime, setLastUpdateTime] = useState<Date | null>(null);
  const timerRef = useRef<number | null>(null);
  // 定义错误计数状态，用于跟踪连续错误次数
  const [, setErrorCount] = useState(0);
  const [systemStatus, setSystemStatus] = useState<'online' | 'offline' | 'warning'>('online');
  const [responseTime, setResponseTime] = useState<number | null>(null);

  // 使用useCallback包装fetchRuntimeInfo，以便在useEffect中使用
  const fetchRuntimeInfo = useCallback(async () => {
    const startTime = Date.now();
    try {
      const response = await systemService.getRuntime();
      const endTime = Date.now();
      const latency = endTime - startTime;
      setResponseTime(latency);
      
      if (response.status === 'success' && response.data) {
        setRuntime(response.data);
        setLastUpdateTime(new Date());
        setError(null);
        setErrorCount(0);
        
        // 根据响应时间判断系统状态
        if (latency > 1000) {
          setSystemStatus('warning');
        } else {
          setSystemStatus('online');
        }      } else {
        handleError(new Error(response.error?.message || '获取运行时间失败'));
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('未知错误');
      handleError(error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleError = (err: Error) => {
    setError(err.message);
    setErrorCount(prev => {
      const newCount = prev + 1;
      // 如果连续3次错误，将状态设置为离线
      if (newCount >= 3) {
        setSystemStatus('offline');
      } else if (newCount >= 1) {
        setSystemStatus('warning');
      }
      return newCount;
    });
  };

  useEffect(() => {
    // 首次加载时获取数据
    fetchRuntimeInfo();

    // 设置定时器，每秒更新一次
    timerRef.current = setInterval(fetchRuntimeInfo, 1000);

    return () => {
      // 组件卸载时清除定时器
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [fetchRuntimeInfo]);

  // 计算距离上次更新的时间差
  const getTimeSinceLastUpdate = () => {
    if (!lastUpdateTime) return '暂无数据';
    const seconds = Math.floor((new Date().getTime() - lastUpdateTime.getTime()) / 1000);
    return `${seconds}秒前`;
  };

  // 根据响应时间获取性能状态
  const getPerformanceStatus = () => {
    if (!responseTime) return null;
    
    if (responseTime < 300) {
      return { color: 'green', text: '良好', percent: 20 };
    } else if (responseTime < 800) {
      return { color: 'cyan', text: '正常', percent: 50 };
    } else if (responseTime < 1500) {
      return { color: 'orange', text: '较慢', percent: 75 };
    } else {
      return { color: 'red', text: '较差', percent: 95 };
    }
  };

  const performanceStatus = getPerformanceStatus();
  return (
    <Card 
      title={
        <span>
          系统运行状态监控
          <Tooltip 
            title="实时监控系统运行状态和响应时间"
            getPopupContainer={(trigger) => trigger.parentElement || document.body}
          >
            <InfoCircleOutlined className="system-runtime-icon-style" />
          </Tooltip>
        </span>
      } 
      className="system-runtime-card-style"
    >
      {loading && !runtime ? (
        <div className="system-runtime-loading-container">
          <Spin spinning={true}>
            <div style={{ minHeight: 100, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span>获取系统运行状态...</span>
            </div>
          </Spin>
        </div>
      ) : error && systemStatus === 'offline' ? (
        <Alert
          message="系统离线"
          description={`无法连接到系统后端服务: ${error}`}
          type="error"
          showIcon
        />
      ) : (
        <>
          <Space direction="vertical" className="system-runtime-full-width">
            <div>
              <Space>
                <Tag color={
                  systemStatus === 'online' 
                    ? 'success' 
                    : systemStatus === 'warning' 
                    ? 'warning' 
                    : 'error'
                }>
                  {systemStatus === 'online' ? (
                    <><CheckCircleOutlined /> 系统在线</>
                  ) : systemStatus === 'warning' ? (
                    <><SyncOutlined spin /> 响应异常</>
                  ) : (
                    <><CloseCircleOutlined /> 系统离线</>
                  )}
                </Tag>
                {responseTime !== null && (
                  <Tag color={
                    responseTime < 300 
                      ? 'success' 
                      : responseTime < 1000 
                      ? 'blue' 
                      : 'orange'
                  }>
                    响应时间: {responseTime}ms
                  </Tag>
                )}
                <Text type="secondary">
                  最后更新: {getTimeSinceLastUpdate()}
                </Text>
              </Space>
            </div>
            
            {performanceStatus && (
              <Row>
                <Col span={24}>
                  <div className="system-runtime-margin-bottom">
                    <Text>系统响应性能: {performanceStatus.text}</Text>
                  </div>
                  <Progress 
                    percent={performanceStatus.percent} 
                    showInfo={false}
                    strokeColor={performanceStatus.color} 
                    size="small" 
                  />
                </Col>
              </Row>
            )}

            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="运行时间"
                  value={runtime?.app_uptime_formatted || '未知'}
                  prefix={<ClockCircleOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="系统时间"
                  value={runtime ? new Date(runtime.current_time).toLocaleString() : '未知'}
                  prefix={<ClockCircleOutlined />}
                />
              </Col>
            </Row>
          </Space>
        </>
      )}
    </Card>
  );
};

export default SystemRuntime;
