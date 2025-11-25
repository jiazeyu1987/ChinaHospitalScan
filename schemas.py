#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医院层级扫查微服务 - 数据模型
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
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