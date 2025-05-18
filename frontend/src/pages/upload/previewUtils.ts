/**
 * 上传页工具函数
 */

/**
 * 从文件获取图片预览URL
 * @param file 图片文件
 * @returns 预览URL Promise
 */
export const getImagePreviewUrl = (file: File): Promise<string> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
  });
};
