#!/usr/bin/env python3
"""
文生图功能测试脚本
测试text2imager函数是否能正常工作
"""

import os
import sys
from pathlib import Path

# 添加backend目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from structured_output import ValidatorSynthesizerResponse, GeoJSONData, GeoFeature, Geometry
from m_workflow import text2imager
from loguru import logger

def create_test_output_state():
    """创建模拟的OutputState用于测试"""
    
    # 创建测试用的GeoFeature
    test_features = [
        GeoFeature(
            geometry=Geometry(
                type="Point",
                coordinates=[116.3974, 39.9093]  # 北京坐标
            ),
            properties={
                "name": "北京",
                "description": "中国首都，历史文化名城",
                "type": "城市"
            }
        ),
        GeoFeature(
            geometry=Geometry(
                type="Point", 
                coordinates=[120.1551, 30.2741]  # 杭州坐标
            ),
            properties={
                "name": "杭州",
                "description": "江南水乡，西湖美景",
                "type": "城市"
            }
        )
    ]
    
    # 创建GeoJSONData
    map_data = GeoJSONData(features=test_features)
    
    # 创建ValidatorSynthesizerResponse
    final_results = ValidatorSynthesizerResponse(
        theme="历史文化名城",
        summary="测试中国历史文化名地图",
        quality_assessment={"confidence": 0.9, "completeness": "good"},
        map_data=map_data
    )
    
    # 创建OutputState
    output_state = {"final_results": final_results}
    
    logger.info("测试数据创建完成")
    logger.info(f"测试包含 {len(test_features)} 个地理特征")
    
    return output_state

def test_text2imager():
    """测试text2imager函数"""
    logger.info("开始测试text2imager函数...")
    
    try:
        # 创建测试数据
        test_state = create_test_output_state()
        
        # 调用text2imager函数
        logger.info("调用text2imager函数...")
        result = text2imager(test_state)
        
        # 检查结果
        logger.info("检查执行结果...")
        
        final_results = result.get("final_results")
        if not final_results:
            logger.error("错误：final_results为空")
            return False
        
        # 检查map_data
        map_data = getattr(final_results, 'map_data', None)
        if not map_data:
            logger.error("错误：map_data为空")
            return False
        
        # 检查features
        if not hasattr(map_data, 'features') or not map_data.features:
            logger.error("错误：features为空")
            return False
        
        # 检查每个feature是否有url属性
        success_count = 0
        for i, feature in enumerate(map_data.features):
            logger.info(f"检查特征 {i+1}: {feature.properties.get('name', 'Unknown')}")
            
            if feature.properties and "url" in feature.properties:
                url = feature.properties["url"]
                logger.info(f"✓ 图片路径已添加: {url}")
                
                # 检查文件是否存在
                if os.path.exists(url):
                    file_size = os.path.getsize(url)
                    logger.info(f"✓ 图片文件存在，大小: {file_size} bytes")
                    success_count += 1
                else:
                    logger.error(f"✗ 图片文件不存在: {url}")
            else:
                logger.error(f"✗ 特征缺少url属性: {feature.properties}")
        
        # 检查images文件夹
        images_dir = Path("images")
        if images_dir.exists():
            image_files = list(images_dir.glob("*"))
            logger.info(f"images文件夹包含 {len(image_files)} 个文件")
            for img_file in image_files:
                logger.info(f"  - {img_file.name}")
        else:
            logger.error("images文件夹不存在")
            return False
        
        # 总结测试结果
        total_features = len(map_data.features)
        logger.info(f"测试完成: {success_count}/{total_features} 个特征成功生成图片")
        
        if success_count == total_features:
            logger.info("✓ 所有测试通过！text2imager函数工作正常")
            return True
        else:
            logger.warning(f"⚠ 部分测试通过: {success_count}/{total_features}")
            return False
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("文生图功能测试")
    print("=" * 50)
    
    # 切换到backend目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 运行测试
    success = test_text2imager()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ 测试结果: 成功")
    else:
        print("✗ 测试结果: 失败")
    print("=" * 50)