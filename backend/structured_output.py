from typing import List, Dict, Any, Literal, Union, Optional
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

# --- 编排器相关类 ---

ALLOWED_RESEARCHERS = Literal[
    "HistoricalResearcher",
    "GeographicalResearcher",
    "CulturalResearcher",
    "ScientificResearcher"
]

class Task(BaseModel):
    """任务格式"""
    # researcher: str = Field(description="研究员名称")
    task_name: str = Field(description="任务名称")
    task_description: str = Field(description="任务描述")
    # parameters: Dict[str, Any] = Field(description="任务参数")
    
    
class OrchestratorResponse(BaseModel):
    """编排器响应格式"""

    task_analysis: str = Field(description="对于用户prompt的任务分析结果")
    theme:str=Field(description="地图的主题")
    selected_researchers: List[ALLOWED_RESEARCHERS] = Field(
        description="选择的研究员列表: HistoricalResearcher, GeographicalResearcher, CulturalResearcher, ScientificResearcher")
    task_allocation: Dict[ALLOWED_RESEARCHERS, Task] = Field(
        description="任务分配策略,格式为{研究员名称: 任务}")
    # coordination_strategy: str = Field(description="协调策略")
    # estimated_time: int = Field(description="预估完成时间（分钟）")
    # parallel_tasks: List[Dict[str, Any]] = Field(description="并行任务列表，包含任务和负责研究员：HistoricalResearcher, GeographicalResearcher, CulturalResearcher, ScientificResearcher")


# --- GeoJSON 标准基础类 ---


class Geometry(BaseModel):
    """地理坐标结构 (GeoJSON Geometry)"""
    type: Literal["Point", "LineString", "Polygon"] = Field(description="几何类型")
    coordinates: Union[List[float], List[List[float]]] = Field(
        description="经纬度坐标。Point为[lon, lat]，LineString为[[lon, lat], ...]"
    )


class GeoFeature(BaseModel):
    """单点地理要素 (GeoJSON Feature)"""
    type: Literal["Feature"] = "Feature"
    geometry: Geometry
    # 关键：将各研究员的特有数据（历史、文化、地理细节）放入 properties
    properties: Dict[str, Any] = Field(
        description="包含具体属性，如：name(地点名), description(描述), year(年份), quote(诗词), terrain(地形) 等"
    )


class GeoJSONData(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[GeoFeature] = Field(description="所有的地理要素列表")
    
# --- 各研究员响应格式 ---
# class HistoricalResearcherResponse(BaseModel):
#     """历史研究员响应格式"""
#     historical_events: List[Dict[str, Any]] = Field(description="相关历史事件列表")
#     timeline: List[Dict[str, Any]] = Field(description="历史时间线")
#     dynastic_background: str = Field(description="朝代背景")
#     historical_significance: str = Field(description="历史意义分析")
#     location_evolution: Dict[str, str] = Field(description="地名演变过程")
#     sources: List[str] = Field(description="史料来源")
#     confidence_score: float = Field(description="置信度评分")


# class GeographicalResearcherResponse(BaseModel):
#     """地理研究员响应格式"""
#     coordinates: Dict[str, List[float]] = Field(description="精确地理坐标")
#     terrain_analysis: Dict[str, str] = Field(description="地形地貌分析")
#     climate_impact: str = Field(description="气候环境影响")
#     spatial_relationships: Dict[str, List[str]] = Field(description="地理位置关系")
#     topographical_features: List[str] = Field(description="地形特征列表")
#     environmental_factors: Dict[str, Any] = Field(description="环境因素分析")
#     map_data: Dict[str, Any] = Field(description="地图数据")
#     coordinate_precision: str = Field(description="坐标准确度说明")


# class CulturalResearcherResponse(BaseModel):
#     """文化研究员响应格式"""
#     literary_references: List[Dict[str, str]] = Field(description="文学作品引用")
#     poetry_citations: List[Dict[str, str]] = Field(description="诗词引用和解析")
#     cultural_significance: str = Field(description="文化意义阐释")
#     folk_traditions: List[str] = Field(description="民俗传统")
#     artistic_value: str = Field(description="艺术价值分析")
#     symbolic_meanings: Dict[str, str] = Field(description="象征意义")
#     cultural_heritage: str = Field(description="文化传承描述")
#     aesthetic_appreciation: str = Field(description="审美价值")


# class ScientificResearcherResponse(BaseModel):
#     """科学研究员响应格式"""
#     scientific_principles: List[Dict[str, str]] = Field(description="相关科学原理")
#     data_analysis: Dict[str, Any] = Field(description="数据分析结果")
#     environmental_science: Dict[str, Any] = Field(description="环境科学分析")
#     modeling_results: Dict[str, Any] = Field(description="数据建模结果")
#     technical_feasibility: str = Field(description="技术可行性评估")
#     scientific_controversies: List[str] = Field(description="科学争议点")
#     research_methodology: str = Field(description="研究方法论")
#     empirical_evidence: List[Dict[str, Any]] = Field(description="经验证据")
#     theoretical_framework: str = Field(description="理论框架")

class HistoricalResearcherResponse(BaseModel):
    """历史研究员：侧重于时间、事件与地点的关联"""
    analysis: str = Field(description="宏观的历史背景、朝代演变和历史意义分析")
    # 这里的 properties 应包含: event_name, year, dynasty, source
    features: List[GeoFeature] = Field(description="包含历史事件发生的地点列表")


class GeographicalResearcherResponse(BaseModel):
    """地理研究员：侧重于地形、地貌与环境"""
    analysis: str = Field(description="地形地貌、气候环境及其对人类活动的影响分析")
    # 这里的 properties 应包含: terrain_type, climate, altitude
    features: List[GeoFeature] = Field(description="包含关键地理地标和自然特征的地点列表")


class CulturalResearcherResponse(BaseModel):
    """文化研究员：侧重于文学、民俗与象征意义"""
    analysis: str = Field(description="文化传承、艺术价值及文学作品背景分析")
    # 这里的 properties 应包含: poetry_quote, author, folklore, symbolic_meaning
    features: List[GeoFeature] = Field(description="包含文化遗址、诗词创作地等文化地标")


class ScientificResearcherResponse(BaseModel):
    """科学研究员：侧重于数据、成因与技术分析"""
    analysis: str = Field(description="科学原理、成因分析及技术可行性评估")
    # 这里的 properties 应包含: scientific_principle, data_value, environmental_factor
    features: List[GeoFeature] = Field(description="包含具有科学考察价值的地点列表")

# --- 验证-综合器响应格式 ---
# class ValidatorSynthesizerResponse(BaseModel):
    # """验证-综合器响应格式"""
    # theme: str = Field(description="主题名称")
    # generated_locations: List[Dict[str, Any]] = Field(description="生成的地点信息列表")
    # quality_assessment: Dict[str, Any] = Field(description="质量评估")
    # research_summary: Dict[str, Any] = Field(description="研究总结")
    # verification_results: Dict[str, bool] = Field(description="验证结果")
    # consistency_check: Dict[str, Any] = Field(description="一致性检查")
    # confidence_scores: Dict[str, float] = Field(description="各维度置信度")
    # source_reliability: Dict[str, str] = Field(description="信息来源可靠性")
    # final_recommendations: List[str] = Field(description="最终建议")


# class ValidatorSynthesizerResponse(BaseModel):
    # """最终输出：标准的 GeoJSON FeatureCollection"""
    # type: Literal["FeatureCollection"] = "FeatureCollection"
    # theme: str = Field(description="地图主题")
    # summary: str = Field(description="最终的研究总结和综合分析")

    # # 这是一个包含所有研究员成果的集合，并经过了去重和验证
    # features: List[GeoFeature] = Field(
    #     description="合并并验证后的所有地理要素列表"
    # )

    # # 如果需要保留一些元数据，可以加一个 metadata 字段
    # metadata: Dict[str, Any] = Field(
    #     description="验证报告，包含：confidence_score(总置信度), data_sources(来源列表)"
    # )


class ValidatorSynthesizerResponse(BaseModel):
    """验证-综合器响应格式"""

    # --- 第一部分：文本分析报告 ---
    theme: str = Field(description="地图主题")
    summary: str = Field(description="最终的研究总结和综合分析")
    quality_assessment: Dict[str, Any] = Field(description="数据质量和置信度评估")

    # --- 第二部分：geojson地图数据 ---
    map_data: GeoJSONData = Field(
        description="标准的GeoJSON格式数据，用于直接渲染地图"
    )
