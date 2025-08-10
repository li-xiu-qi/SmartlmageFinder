import { forwardRef } from 'react';
import { Tooltip, TooltipProps } from 'antd';

/**
 * 安全的 Tooltip 组件，避免 findDOMNode 警告
 * 通过包装子元素在一个 div 中来避免直接引用 antd 组件
 */
const SafeTooltip = forwardRef<HTMLDivElement, TooltipProps>(({ children, ...props }, ref) => {
  return (
    <Tooltip
      {...props}
      getPopupContainer={(trigger) => trigger.parentElement || document.body}
    >
      <div ref={ref} style={{ display: 'inline-block' }}>
        {children}
      </div>
    </Tooltip>
  );
});

SafeTooltip.displayName = 'SafeTooltip';

export default SafeTooltip;
