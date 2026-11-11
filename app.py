import functools
from runtime.common import device, guarded, image_rgb, model_path, output_path, page_header


@functools.lru_cache(maxsize=1)
def model_and_processor():
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation
    directory = model_path()
    return (AutoModelForDepthEstimation.from_pretrained(directory, use_safetensors=True).to(device()).eval(),
            AutoImageProcessor.from_pretrained(directory, use_fast=False))


@guarded
def estimate(image):
    import numpy as np
    import torch
    from PIL import Image
    image = image_rgb(image, max_pixels=4_000_000)
    model, processor = model_and_processor()
    inputs = processor(images=image, return_tensors="pt").to(device())
    with torch.inference_mode():
        outputs = model(**inputs)
        depth = processor.post_process_depth_estimation(outputs, target_sizes=[(image.height, image.width)])[0]["predicted_depth"]
    raw = depth.detach().float().cpu().numpy()
    if not np.isfinite(raw).all():
        raise RuntimeError("模型未生成有效深度图，请更换图片重试")
    minimum, maximum = float(raw.min()), float(raw.max())
    normalized = np.zeros_like(raw) if maximum <= minimum else np.clip((raw-minimum)/(maximum-minimum), 0, 1)
    preview = Image.fromarray(np.round(normalized*255).astype(np.uint8))
    destination = output_path(".png")
    Image.fromarray(np.round(normalized*65535).astype(np.uint16)).save(destination)
    return preview, str(destination)


def build_ui():
    import gradio as gr
    with gr.Blocks(title="Depth Anything V2 深度估计") as ui:
        page_header()
        gr.Markdown("输出相对深度图，保持原图尺寸；灰度值不代表米制距离。图片最多400万像素。")
        image = gr.Image(type="pil", label="上传图片")
        button = gr.Button("生成深度图", variant="primary")
        preview = gr.Image(type="pil", label="相对深度预览")
        download = gr.File(label="下载16位深度 PNG")
        button.click(estimate, image, [preview, download], api_name="estimate")
    return ui
