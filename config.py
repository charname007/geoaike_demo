from asyncio import Server
import os
from re import S
from dotenv import load_dotenv
# from h11 import SERVER
from loguru import logger
from regex import D
# 加载 .env 文件中的环境变量
# 这行代码会在你的应用启动时，将 .env 文件中的键值对加载到操作系统的环境变量中
load_dotenv()
logger.info("Environment variables loaded from .env file")

DEEPSEEK_CONFIG={
    'model': os.getenv('MODEL_NAME', 'deepseek-chat'),
    'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
    'base_url': os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1'),
    'temperature': float(os.getenv('TEMPERATURE', '0.7')),
}
if not DEEPSEEK_CONFIG['api_key']:
    logger.error("DEEPSEEK_API_KEY is not set. Please set it in the .env file or environment variables.")

logger.info(f"DeepSeek configuration: {DEEPSEEK_CONFIG}")

DOUBAO_CONFIG={
    'api_key': os.getenv('DOUBAO_API_KEY', ''),
    'base_url': os.getenv('DOUBAO_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3'),
    'image_model': os.getenv('Image_Model', 'doubao-seedream-4-0-250828'),
}
if not DOUBAO_CONFIG['api_key']:
    logger.warning("DOUBAO_API_KEY is not set. Please set it in the .env file or environment variables.")

SERVER_CONFIG={
    'host': os.getenv('SERVER_HOST', 'localhost'),
    'port': int(os.getenv('SERVER_PORT', '8000')),
    'name': os.getenv('SERVER_NAME', 'GeoAI_Server'),
    
}
logger.info(f"Server configuration: {SERVER_CONFIG}")
if __name__ == "__main__":
    # 测试配置是否正确加载
    print(DEEPSEEK_CONFIG)
    
