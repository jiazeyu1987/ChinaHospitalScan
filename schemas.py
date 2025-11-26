#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医院层级扫查微服务 - 数据模型
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum

class DataLevel(str, Enum):
    """数据层级枚举"""
    PROVINCE = "province"
    CITY = "city"
    DISTRICT = "district"
    HOSPITAL = "hospital"

class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, Enum):
    """任务类型枚举"""
    HOSPITAL = "hospital"  # 单个医院扫描
    PROVINCE = "province"  # 省级扫描
    NATIONWIDE = "nationwide"  # 全国扫描

class HospitalLevel(str, Enum):
    """医院等级枚举"""
    TERTIARY_A = "三级甲等"
    TERTIARY_B = "三级乙等"
    TERTIARY_C = "三级丙等"
    SECONDARY_A = "二级甲等"
    SECONDARY_B = "二级乙等"
    SECONDARY_C = "二级丙等"
    PRIMARY = "一级医院"
    UNKNOWN = "未知"

class DepartmentType(str, Enum):
    """科室类型枚举"""
    INTERNAL = "内科"
    SURGERY = "外科"
    GYNECOLOGY = "妇产科"
    PEDIATRICS = "儿科"
    EMERGENCY = "急诊科"
    ORTHOPEDICS = "骨科"
    NEUROLOGY = "神经内科"
    CARDIOLOGY = "心血管内科"
    ONCOLOGY = "肿瘤科"
    TCM = "中医科"
    OTHER = "其他"

class HospitalInfo(BaseModel):
    """医院信息模型"""
    hospital_name: str = Field(..., description="医院全名")
    level: Optional[str] = Field(None, description="医院等级")
    address: Optional[str] = Field(None, description="医院地址")
    phone: Optional[str] = Field(None, description="联系电话")
    departments: List[str] = Field(default_factory=list, description="科室列表")
    beds_count: Optional[int] = Field(None, description="床位数")
    staff_count: Optional[int] = Field(None, description="员工总数")
    specializations: List[str] = Field(default_factory=list, description="特色专科")
    management_structure: Optional[Dict[str, int]] = Field(None, description="管理层级结构")
    operating_hours: Optional[str] = Field(None, description="营业时间")
    website: Optional[str] = Field(None, description="官方网站")
    established_year: Optional[int] = Field(None, description="建院年份")
    certification: Optional[List[str]] = Field(None, description="资质认证")

class ScanTaskRequest(BaseModel):
    """扫查任务请求模型"""
    hospital_name: str = Field(..., description="医院名称")
    query: Optional[str] = Field(None, description="查询需求")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="选项参数")
    task_type: Optional[TaskType] = Field(TaskType.HOSPITAL, description="任务类型")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

class ScanTaskResponse(BaseModel):
    """扫查任务响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    message: str = Field(..., description="响应消息")
    created_at: Optional[datetime] = Field(None, description="创建时间")

class ScanResult(BaseModel):
    """扫查结果模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    hospital_info: Optional[HospitalInfo] = Field(None, description="医院信息")
    report: Optional[str] = Field(None, description="分析报告")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    execution_time: Optional[float] = Field(None, description="执行时间（秒）")
    error_message: Optional[str] = Field(None, description="错误信息")

class TaskListItem(BaseModel):
    """任务列表项模型"""
    task_id: str = Field(..., description="任务ID")
    hospital_name: str = Field(..., description="医院名称")
    status: TaskStatus = Field(..., description="任务状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    query: Optional[str] = Field(None, description="查询需求")

class TaskStatistics(BaseModel):
    """任务统计模型"""
    total_tasks: int = Field(..., description="总任务数")
    pending_tasks: int = Field(..., description="待处理任务数")
    running_tasks: int = Field(..., description="运行中任务数")
    completed_tasks: int = Field(..., description="已完成任务数")
    failed_tasks: int = Field(..., description="失败任务数")
    success_rate: float = Field(..., description="成功率")
    average_execution_time: Optional[float] = Field(None, description="平均执行时间")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

class HealthCheck(BaseModel):
    """健康检查模型"""
    status: str = Field(..., description="状态")
    version: str = Field(..., description="版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    uptime: Optional[float] = Field(None, description="运行时间（秒）")
    database_status: Optional[str] = Field(None, description="数据库状态")
    llm_client_status: Optional[str] = Field(None, description="LLM客户端状态")

class HierarchyAnalysis(BaseModel):
    """层级分析模型"""
    task_id: str = Field(..., description="任务ID")
    hospital_name: str = Field(..., description="医院名称")
    analysis_result: Dict[str, Any] = Field(..., description="分析结果")
    confidence_score: Optional[float] = Field(None, description="置信度分数")
    suggestions: List[str] = Field(default_factory=list, description="建议")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

class DepartmentInfo(BaseModel):
    """科室信息模型"""
    name: str = Field(..., description="科室名称")
    type: Optional[DepartmentType] = Field(None, description="科室类型")
    head: Optional[str] = Field(None, description="科室主任")
    staff_count: Optional[int] = Field(None, description="员工数量")
    beds_count: Optional[int] = Field(None, description="床位数")
    specializations: List[str] = Field(default_factory=list, description="专长")
    contact_phone: Optional[str] = Field(None, description="联系电话")

class StaffStructure(BaseModel):
    """人员结构模型"""
    total_staff: int = Field(..., description="总员工数")
    doctors: int = Field(..., description="医生数量")
    nurses: int = Field(..., description="护士数量")
    technicians: int = Field(..., description="技术人员数量")
    administrators: int = Field(..., description="管理人员数量")
    departments: Dict[str, int] = Field(default_factory=dict, description="各科室人员分布")

# 新增的层级数据结构模型
class Province(BaseModel):
    """省份模型"""
    id: Optional[int] = Field(None, description="省份ID")
    name: str = Field(..., description="省份名称")
    code: Optional[str] = Field(None, description="省份代码")
    cities_count: Optional[int] = Field(0, description="城市数量")
    hospitals_count: Optional[int] = Field(0, description="医院数量")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class City(BaseModel):
    """城市模型"""
    id: Optional[int] = Field(None, description="城市ID")
    name: str = Field(..., description="城市名称")
    code: Optional[str] = Field(None, description="城市代码")
    province_id: Optional[int] = Field(None, description="所属省份ID")
    districts_count: Optional[int] = Field(0, description="区县数量")
    hospitals_count: Optional[int] = Field(0, description="医院数量")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class District(BaseModel):
    """区县模型"""
    id: Optional[int] = Field(None, description="区县ID")
    name: str = Field(..., description="区县名称")
    code: Optional[str] = Field(None, description="区县代码")
    city_id: Optional[int] = Field(None, description="所属城市ID")
    hospitals_count: Optional[int] = Field(0, description="医院数量")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class Hospital(BaseModel):
    """医院模型"""
    id: Optional[int] = Field(None, description="医院ID")
    name: str = Field(..., description="医院名称")
    level: Optional[str] = Field(None, description="医院等级")
    district_id: Optional[int] = Field(None, description="所属区县ID")
    address: Optional[str] = Field(None, description="医院地址")
    phone: Optional[str] = Field(None, description="联系电话")
    beds_count: Optional[int] = Field(None, description="床位数")
    staff_count: Optional[int] = Field(None, description="员工数")
    departments: Optional[List[str]] = Field(None, description="科室列表")
    specializations: Optional[List[str]] = Field(None, description="特色专科")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class RefreshTaskRequest(BaseModel):
    """数据刷新任务请求模型"""
    level: DataLevel = Field(..., description="刷新层级")
    parent_id: Optional[int] = Field(None, description="父级ID（省/市/区县）")
    name: Optional[str] = Field(None, description="名称（用于特定省份刷新）")
    force_refresh: bool = Field(False, description="是否强制刷新")

class RefreshTaskResponse(BaseModel):
    """数据刷新任务响应模型"""
    task_id: str = Field(..., description="任务ID")
    message: str = Field(..., description="响应消息")
    created_at: Optional[datetime] = Field(None, description="创建时间")

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Dict[str, Any]] = Field(..., description="数据项列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str = Field(..., description="搜索关键词")
    level: Optional[DataLevel] = Field(None, description="搜索层级")
    limit: int = Field(20, description="结果限制")

# 医院网站查询和更新相关模型
class HospitalWebsiteRequest(BaseModel):
    """医院网站查询请求模型"""
    hospital_name: str = Field(..., description="医院名称", min_length=2, max_length=200)
    force_update: bool = Field(False, description="是否强制更新已有网站信息")

class HospitalWebsiteInfo(BaseModel):
    """医院网站信息模型"""
    hospital_name: str = Field(..., description="医院全名")
    website: Optional[str] = Field(None, description="官方网站URL")
    website_status: Optional[str] = Field(None, description="网站状态：可用/不可用/未知")
    confidence: Optional[str] = Field(None, description="信息可信度：高/中/低")
    alternative_names: Optional[List[str]] = Field(default_factory=list, description="医院的其他可能名称")
    notes: Optional[str] = Field(None, description="备注信息")
    llm_response_time: Optional[float] = Field(None, description="LLM响应时间（秒）")
    request_id: Optional[str] = Field(None, description="请求ID")

class HospitalWebsiteResponse(BaseModel):
    """医院网站查询响应模型"""
    success: bool = Field(..., description="操作是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="返回数据")
    message: str = Field(..., description="响应消息")
    request_id: Optional[str] = Field(None, description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class HospitalWebsiteUpdateResult(BaseModel):
    """医院网站更新结果模型"""
    hospital_id: Optional[int] = Field(None, description="医院ID")
    hospital_name: Optional[str] = Field(None, description="医院名称")
    previous_website: Optional[str] = Field(None, description="更新前网站")
    new_website: Optional[str] = Field(None, description="更新后网站")
    updated: bool = Field(..., description="是否执行了更新")
    llm_response_time: Optional[float] = Field(None, description="LLM响应时间（秒）")
    database_update_time: Optional[float] = Field(None, description="数据库更新时间（秒）")
    total_time: Optional[float] = Field(None, description="总处理时间（秒）")
    request_id: Optional[str] = Field(None, description="请求ID")

# 批量更新医院网站相关模型
class BatchUpdateRequest(BaseModel):
    """批量更新医院网站请求模型"""
    update_all: Optional[bool] = Field(False, description="是否更新所有医院（为true时忽略其他限制参数）")
    limit: Optional[int] = Field(1000, description="每次批量处理的医院数量限制（默认1000，最大10000）", ge=1, le=10000)
    skip_existing: Optional[bool] = Field(False, description="跳过已有网站信息的医院（默认false）")
    hospital_ids: Optional[List[int]] = Field(None, description="指定要更新的医院ID列表（可选，为空则更新所有医院）")
    progress_callback_url: Optional[str] = Field(None, description="进度回调URL（可选）")

class HospitalUpdateResult(BaseModel):
    """单个医院更新结果模型"""
    hospital_id: int
    hospital_name: str
    previous_website: Optional[str]
    new_website: Optional[str]
    success: bool
    updated: bool
    error_message: Optional[str]
    llm_response_time: float
    database_update_time: float
    total_time: float
    request_id: str

class BatchUpdateProgress(BaseModel):
    """批量更新进度模型"""
    total_hospitals: int
    processed_hospitals: int
    successful_updates: int
    failed_updates: int
    skipped_hospitals: int
    current_hospital_name: Optional[str]
    progress_percentage: float
    estimated_remaining_time: Optional[float]

class BatchUpdateResponse(BaseModel):
    """批量更新响应模型"""
    success: bool
    message: str
    task_id: Optional[str] = Field(None, description="批量更新任务ID")
    progress: Optional[BatchUpdateProgress] = Field(None, description="更新进度")
    results: Optional[List[HospitalUpdateResult]] = Field(None, description="详细结果（仅在小批量或完成时返回）")
    total_time: Optional[float] = Field(None, description="总处理时间（秒）")
    request_id: str = Field(..., description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class ProcurementCrawlRequest(BaseModel):
    """采购链接爬取请求模型"""
    base_url: str = Field(..., description="需要爬取的基础URL，例如：https://www.hospital-cqmu.com/gzb_cgxx")
    max_depth: Optional[int] = Field(
        None,
        description="深度优先搜索的最大深度（对应 BFSDeepCrawlStrategy.max_depth，默认 5）",
        ge=1
    )
    max_pages: Optional[int] = Field(
        None,
        description="最多爬取的页面数量（对应 BFSDeepCrawlStrategy.max_pages，默认 27）",
        ge=1
    )
    keywords: Optional[List[str]] = Field(
        default=None,
        description="链接文本关键词列表。如果提供，只有link_text包含至少一个关键词的链接才会被存储。默认使用内置关键词：公告、采购、公开、招标、询价。支持中文关键词，如【公告】、【采购】、【中标】等。",
        example=["公告", "采购", "中标"]
    )
    hospital_id: Optional[int] = Field(
        default=None,
        description="医院ID，如果提供，系统将优先使用该医院的个性化关键词设置。如果医院设置了个性化关键词，将使用医院的关键词；如果未设置，则使用keywords参数或默认关键词。",
        example=123
    )

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        if v is None:
            return v

        # 验证关键词数量
        if len(v) > 20:
            raise ValueError('关键词数量不能超过20个')

        # 验证每个关键词
        for i, keyword in enumerate(v):
            if not keyword or not keyword.strip():
                raise ValueError(f'关键词不能为空字符串（第{i+1}个关键词）')

            keyword = keyword.strip()
            if len(keyword) > 50:
                raise ValueError(f'关键词长度不能超过50个字符（第{i+1}个关键词："{keyword}"）')

        return [kw.strip() for kw in v]


class ProcurementCrawlResponse(BaseModel):
    """采购链接爬取响应模型"""
    base_url: str = Field(..., description="本次爬取的基础URL")
    total_urls: int = Field(..., description="本次采集到的唯一URL数量")
    new_or_updated: int = Field(..., description="新增或更新的记录数量")
    db_path: str = Field(..., description="写入数据的数据库文件路径")


class BaseProcurementLinkRequest(BaseModel):
    """基础采购链接设置请求模型"""
    hospital_name: str = Field(..., description="医院名称", min_length=2, max_length=200)
    base_procurement_link: str = Field(..., description="基础采购链接URL", min_length=1, max_length=500)


class BaseProcurementLinkResponse(BaseModel):
    """基础采购链接设置响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="操作结果描述")
    hospital_id: Optional[int] = Field(None, description="医院ID")
    hospital_name: str = Field(..., description="医院名称")
    base_procurement_link: Optional[str] = Field(None, description="设置的基础采购链接")
    updated: bool = Field(..., description="是否执行了更新操作")
    request_id: str = Field(..., description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class ProcurementSearchRequest(BaseModel):
    """采购信息搜索请求模型"""
    base_url: str = Field(..., description="采购基础URL", example="http://www.procurement.example.com")
    time_start: str = Field(..., description="开始时间 (YYYY-MM-DD 格式)", example="2024-01-01")
    time_end: str = Field(..., description="结束时间 (YYYY-MM-DD 格式)", example="2024-12-31")

class ProcurementLinkItem(BaseModel):
    """采购链接项模型"""
    id: int = Field(..., description="记录ID")
    base_url: str = Field(..., description="采购基础URL")
    url: str = Field(..., description="具体采购链接URL")
    link_text: Optional[str] = Field(None, description="链接文本")
    first_seen_at: str = Field(..., description="首次发现时间")
    last_seen_at: Optional[str] = Field(None, description="最后更新时间")
    is_latest: bool = Field(..., description="是否为最新记录")

class ProcurementSearchResponse(BaseModel):
    """采购信息搜索响应模型"""
    success: bool = Field(..., description="搜索是否成功")
    message: str = Field(..., description="搜索结果描述")
    total_count: int = Field(..., description="匹配的记录总数")
    procurement_links: List[ProcurementLinkItem] = Field(..., description="采购链接列表")
    search_params: ProcurementSearchRequest = Field(..., description="搜索参数")
    request_id: str = Field(..., description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class ProcurementLatestRequest(BaseModel):
    """采购最新信息搜索请求模型"""
    base_url: Optional[str] = Field(None, description="采购基础URL（可选，为空时搜索所有is_latest=1的记录）", example="http://www.procurement.example.com")

class ProcurementLatestResponse(BaseModel):
    """采购最新信息搜索响应模型"""
    success: bool = Field(..., description="搜索是否成功")
    message: str = Field(..., description="搜索结果描述")
    total_count: int = Field(..., description="匹配的记录总数")
    procurement_links: List[ProcurementLinkItem] = Field(..., description="采购链接列表（仅is_latest=1的记录）")
    search_params: ProcurementLatestRequest = Field(..., description="搜索参数")
    request_id: str = Field(..., description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class HospitalKeywordsRequest(BaseModel):
    """医院关键词设置请求模型"""
    hospital_id: int = Field(..., description="医院ID")
    keywords: List[str] = Field(
        default=[],
        description="医院个性化采购关键词列表，空列表表示重置为默认关键词",
        example=["公告", "采购", "医疗设备招标", "药品采购"]
    )

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        if v is None:
            return []

        # 验证关键词数量不超过50个
        if len(v) > 50:
            raise ValueError('关键词数量不能超过50个')

        # 验证每个关键词
        for i, keyword in enumerate(v):
            if not keyword or not keyword.strip():
                raise ValueError(f'关键词不能为空字符串（第{i+1}个关键词）')

            # 验证关键词长度
            if len(keyword.strip()) > 100:
                raise ValueError(f'关键词长度不能超过100个字符（第{i+1}个关键词）')

        # 去重并返回清理后的关键词
        cleaned_keywords = []
        seen = set()
        for keyword in v:
            cleaned_keyword = keyword.strip()
            if cleaned_keyword and cleaned_keyword not in seen:
                cleaned_keywords.append(cleaned_keyword)
                seen.add(cleaned_keyword)

        return cleaned_keywords


class HospitalKeywordsResponse(BaseModel):
    """医院关键词设置响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="操作结果描述")
    hospital_id: int = Field(..., description="医院ID")
    hospital_name: str = Field(..., description="医院名称")
    keywords: List[str] = Field(..., description="当前关键词列表")
    is_custom: bool = Field(..., description="是否为个性化设置（True表示使用医院自定义关键词，False表示使用系统默认关键词）")
    default_keywords: List[str] = Field(..., description="系统默认关键词列表")
    request_id: str = Field(..., description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class HospitalKeywordsDeleteRequest(BaseModel):
    """医院关键词重置请求模型"""
    hospital_id: int = Field(..., description="医院ID")
    confirm: bool = Field(..., description="设置为True确认重置医院关键词为默认值")
