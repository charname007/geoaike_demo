"""
地理信息AI生成系统 FastAPI服务器
Geographic Information AI Generation System FastAPI Server

提供完整的REST API接口和WebSocket支持
"""


import json
import os
from datetime import datetime
from tkinter import SE
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from config import SERVER_CONFIG
from loguru import logger
from m_workflow import m_graph
from pathlib import Path
from fastapi.staticfiles import StaticFiles


dir_log = "logs"
dir_cache = "cache"


# logger = logging.getLogger(__name__)


# ==================== 生命周期管理 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("LLM_Based_MapS_Pot_Collector系统启动中...")

    # 确保缓存目录存在
    os.makedirs(dir_cache, exist_ok=True)

    # 确保日志目录存在
    os.makedirs(dir_log, exist_ok=True)
# Configure logger
    logger.add(
        "logs/runtime_{time}.log",  # 日志文件路径，支持时间占位符
        rotation="500 MB",          # 日志滚动：每个文件最大 500MB (也可以写 "12:00" 每天中午滚动)
        retention="10 days",        # 日志保留：只保留最近 10 天的日志
        compression="zip",          # 日志压缩：滚动后的文件自动压缩为 zip
        encoding="utf-8",           # 编码
        level="INFO",               # 级别：只记录 INFO 及以上级别的日志
        enqueue=True                # 异步写入：如果在多线程/多进程中使用，建议开启
    )

    logger.info("系统启动完成")

    yield

    # 关闭时清理
    logger.info("系统关闭中...")
    # 这里可以添加清理逻辑
    logger.info("系统关闭完成")


# ==================== FastAPI应用初始化 ====================

app = FastAPI(
    title="基于多Agent的地图数据智能生成服务",
    description="基于多Agent的地图数据智能生成服务",
    version="1.0.0",
    lifespan=lifespan
)

# 【关键步骤】将本地的 "static" 文件夹挂载到 URL 路径 "/static" 下
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount('/cache', StaticFiles(directory='cache'), name='cache')
# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get('/collect_map_data')
async def collect_map_data(user_prompt: str):
    """收集地图数据的端点"""
    logger.info(
        f"Received map data collection request with prompt: {user_prompt}")
    input_state = {"user_prompt": user_prompt}
    try:
        result = m_graph.invoke(input_state)
        logger.info("Map data collection completed successfully.")

        # 存入cache
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cache_filename = f"map_data_{timestamp}.json"
        with open(f"{dir_cache}/{cache_filename}", "w", encoding="utf-8") as f:
            # 在第108行替换为
            final_results = result.get('final_results')
            if final_results and hasattr(final_results, 'model_dump_json'):
                f.write(final_results.model_dump_json(
                    ensure_ascii=False, indent=4))
                logger.info(f"Map data cached to {cache_filename}")

            else:
                json.dump(final_results.dict() if hasattr(final_results, 'dict') else final_results,
                          f, ensure_ascii=False, indent=4)
                logger.info(f"Map data cached to {cache_filename}")


        return result
    except Exception as e:
        logger.error(f"Error during map data collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs")
async def get_logs():
    """获取日志文件列表的端点"""
    try:
        log_files = os.listdir(dir_log)
        log_files = [f for f in log_files if f.startswith(
            "runtime_") and f.endswith(".log")]
        return {"log_files": log_files}
    except Exception as e:
        logger.error(f"Error retrieving log files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/Map_Page')
async def get_map_page():
    """提供地图页面的端点"""
    html_path = Path(__file__).parent / 'front_page' / 'Map_page.html'
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return StreamingResponse(iter([html_content]), media_type="text/html")
    except Exception as e:
        logger.error(f"Error loading map page: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ==================== 启动服务 ====================

if __name__ == "__main__":
    uvicorn.run(
        'server:app',
        host=SERVER_CONFIG['host'],
        port=SERVER_CONFIG['port'],
        reload=True,
        log_level=SERVER_CONFIG.get('log_level', 'info').lower()
    )
    logger.info(
        "Server started at http://{}:{}".format(SERVER_CONFIG['host'], SERVER_CONFIG['port']))
    logger.info("访问地图页面：http://{}:{}/Map_Page".format(
        SERVER_CONFIG['host'], SERVER_CONFIG['port']))
