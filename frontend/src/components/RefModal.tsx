import React from 'react';
import { Modal, ModalProps } from 'antd';

/**
 * 带有引用的Modal组件，用于解决React 18中的findDOMNode警告
 * 这是一个包装组件，它使用forwardRef来正确传递引用
 */
const RefModal: React.FC<ModalProps> = (props) => {
  return <Modal {...props} />;
};

export default RefModal;
