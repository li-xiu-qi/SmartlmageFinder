import requests
import base64
import os

def generate_image(
    prompt: str,
    model: str = "Kwai-Kolors/Kolors",
    image_size: str = "1024x1024",
    batch_size: int = 1,
    num_inference_steps: int = 20,
    guidance_scale: float = 7.5,
    negative_prompt: str | None = None,
    seed: int | None = None,
    image: str | None = None,  # base64，如："data:image/png;base64,XXX"
    api_key: str | None = None,
    base_url: str | None = None,  # 形如 https://api.xxx.com/v1
    timeout: int = 120,
    return_format: str = "url",  # "url" | "download"
    download_path: str | None = None,  # 当 return_format="download" 时必填
):
    """
    直接调用图片生成接口：POST {base_url}/images/generations。

    返回：
    - return_format="url"：返回第一张图片 URL（URL 有效期 1 小时，请及时下载）
    - return_format="download"：下载第一张图片到 download_path 并返回保存路径
    """
    if return_format == "download" and not download_path:
        raise RuntimeError("return_format=download 时必须提供 download_path")
    if not base_url:
        raise RuntimeError("必须提供 base_url，例如：https://api.xxx.com/v1")
    if not api_key:
        raise RuntimeError("必须提供 api_key 用于 Authorization: Bearer 认证")

    url_endpoint = base_url.rstrip("/") + "/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body: dict = {
        "model": model,
        "prompt": prompt,
        "image_size": image_size,
        "batch_size": batch_size,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
    }
    if negative_prompt:
        body["negative_prompt"] = negative_prompt
    if seed is not None:
        body["seed"] = seed
    if image:
        body["image"] = image

    resp = requests.post(url_endpoint, headers=headers, json=body, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()

    images = payload.get("images") or payload.get("data")
    if not images or not isinstance(images, list):
        raise RuntimeError("响应中未包含 images/data 列表")
    first = images[0]
    if hasattr(first, "__dict__"):
        first = dict(first.__dict__)

    # 统一处理返回第一张图片
    url = first.get("url")
    b64 = first.get("b64_json")
    if return_format == "url":
        if not url:
            raise RuntimeError("未获得有效的图像 URL（接口可能未返回 url 字段）")
        return url
    else:  # download
        save_path = download_path
        if url:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(r.content)
            print(f"Downloaded and saved to {save_path} (from url)")
            return save_path
        if b64:
            img_bytes = base64.b64decode(b64)
            with open(save_path, "wb") as f:
                f.write(img_bytes)
            print(f"Saved base64 image to {save_path}")
            return save_path
        raise RuntimeError("第一张图片既无 url 也无 b64_json，无法保存")
