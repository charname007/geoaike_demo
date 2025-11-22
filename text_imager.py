from config import DOUBAO_CONFIG

import os
import requests
import uuid
import asyncio
import aiohttp
from urllib.parse import urlparse
# 通过 pip install 'volcengine-python-sdk[ark]' 安装方舟SDK
from volcenginesdkarkruntime import Ark
from loguru import logger



# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url=DOUBAO_CONFIG['base_url'],
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=DOUBAO_CONFIG['api_key'],
)

dir_image="images"
os.makedirs(dir_image, exist_ok=True)
system_prompt = '''你是一个符号设计专家，你能根据用户提供的关于某个地点的描述，结合你自己的印象，
                提取该地点最核心的 1到2个视觉主体，生成符合该地点特色的符号设计图像。
                你的风格：
                是扁平化（Flat）： 拒绝写实照片风格，拒绝复杂光影。
                几何化（Geometric）： 使用圆形、方形、线条等基础几何图形来概括物体。
                矢量感（Vector）： 线条流畅，边缘清晰，类似 APP 图标或 UI 界面元素。，
                你能够根据不同的地点特征生成符号设计图像，充分表现这个地方的地理，人文，历史，科技，文化特征。'''
                



# imagesResponse = client.images.generate(
#     model=DOUBAO_CONFIG['image_model'],
#     prompt="星际穿越，黑洞，黑洞里冲出一辆快支离破碎的复古列车，抢视觉冲击力，电影大片，末日既视感，动感，对比色，oc渲染，光线追踪，动态模糊，景深，超现实主义，深蓝，画面通过细腻的丰富的色彩层次塑造主体与场景，质感真实，暗黑风背景的光影效果营造出氛围，整体兼具艺术幻想感，夸张的广角透视效果，耀光，反射，极致的光影，强引力，吞噬",
#     sequential_image_generation="disabled",
#     response_format="url",
#     size="2K",
#     stream=False,
#     watermark=True
# )

# print(imagesResponse.data[0].url)
def build_image_prompt(location_description: str,theme: str) -> str:
    prompt = f"""{system_prompt}
    请根据以下地点描述，生成符号设计图像的提示词：
    地点描述：{location_description}
    主题：{theme}
    符号设计图像提示词："""
    return prompt

def generate_symbol_image(location_description: str,theme: str) -> str:
    prompt = build_image_prompt(location_description, theme)
    imagesResponse = client.images.generate(
        model=DOUBAO_CONFIG['image_model'],
        prompt=prompt,
        sequential_image_generation="disabled",
        response_format="url",
        size="2K",
        stream=False,
        watermark=False
    )
    url=imagesResponse.data[0].url
    # url = download_image(url)
    return imagesResponse.data[0].url

def download_image(image_url: str) -> str:
    """从URL下载图片并保存到images文件夹
    
    Args:
        image_url: 图片URL
        
    Returns:
        str: 本地图片路径
    """
    try:
        # 生成唯一文件名
        file_extension = ".jpg"  # 默认扩展名
        parsed_url = urlparse(image_url)
        if parsed_url.path:
            path_parts = parsed_url.path.split('.')
            if len(path_parts) > 1:
                file_extension = "." + path_parts[-1].lower()
        
        filename = f"{uuid.uuid4().hex}{file_extension}"
        local_path = os.path.join(dir_image, filename)
        
        # 下载图片
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
            
        logger.info(f"图片下载成功: {local_path}")
        return local_path
        
    except Exception as e:
        logger.error(f"图片下载失败: {e}")
        raise

# 异步版本的图片下载
async def download_image_async(image_url: str) -> str:
    """异步从URL下载图片并保存到images文件夹
    
    Args:
        image_url: 图片URL
        
    Returns:
        str: 本地图片路径
    """
    try:
        # 生成唯一文件名
        file_extension = ".jpg"
        parsed_url = urlparse(image_url)
        if parsed_url.path:
            path_parts = parsed_url.path.split('.')
            if len(path_parts) > 1:
                file_extension = "." + path_parts[-1].lower()
        
        filename = f"{uuid.uuid4().hex}{file_extension}"
        local_path = os.path.join(dir_image, filename)
        
        # 异步下载图片
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(image_url) as response:
                response.raise_for_status()
                content = await response.read()
                
                with open(local_path, 'wb') as f:
                    f.write(content)
                
        logger.info(f"图片下载成功: {local_path}")
        return local_path
        
    except Exception as e:
        logger.error(f"图片下载失败: {e}")
        raise

# 异步版本的图片生成（包装同步API调用）
async def generate_symbol_image_async(location_description: str, theme: str) -> str:
    """异步包装同步的图片生成API调用"""
    import concurrent.futures
    
    # 使用线程池执行同步函数，避免事件循环冲突
    with concurrent.futures.ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            generate_symbol_image,  # 原来的同步函数
            location_description,
            theme
        )

# 异步处理单个特征
async def process_single_feature_async(feature, theme: str) -> tuple:
    """异步处理单个特征
    
    Returns:
        tuple: (feature, description, local_path_or_error)
    """
    # 提取properties作为描述
    description = ""
    if feature.properties:
        desc_parts = []
        for key, value in feature.properties.items():
            if value:
                desc_parts.append(f"{key}: {value}")
        description = ", ".join(desc_parts)
    
    if not description:
        description = "地理特征符号"
    
    try:
        # 异步生成图片
        image_url = await generate_symbol_image_async(description, theme)
        
        # 异步下载图片
        local_path = await download_image_async(image_url)
        
        # 将本地图片路径作为url属性添加到feature的properties中
        if not feature.properties:
            feature.properties = {}
        feature.properties["url"] = local_path
        
        logger.info(f"为特征生成图片完成: {description} -> {local_path}")
        return feature, description, local_path
        
    except Exception as e:
        logger.error(f"为特征生成图片失败: {description}, 错误: {e}")
        return feature, description, None

# 异步批处理所有特征
async def process_features_async(features,theme:str) -> list:
    """异步批处理所有特征"""
    # 创建所有异步任务
    tasks = [process_single_feature_async(feature, theme) for feature in features]
    
    # 并发执行所有任务
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 统计结果
    successful_count = sum(1 for result in results if isinstance(result, tuple) and result[2] is not None)
    failed_count = len(results) - successful_count
    
    logger.info(f"异步处理完成: 成功 {successful_count} 个，失败 {failed_count} 个")
    
    return results

if __name__ == "__main__":
    test_description = "长城，蜿蜒在群山之间，象征着中国古代的军事防御工程和文化遗产"
    image_url = generate_symbol_image(test_description,"长城符号")
    local_image_path = download_image(image_url)
    logger.info(f"生成的图片已保存到: {local_image_path}")