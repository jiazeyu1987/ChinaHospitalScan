# HBScan API 接口文档

## 服务概述
HBScan 是一个基于大语言模型的医院层级结构自动扫查服务，提供全国范围的省、市、区县、医院四级数据的采集、查询和管理功能。系统具备以下核心能力：

**基础信息：**
- 基础URL: `http://localhost:8000`
- 数据格式: JSON
- 字符编码: UTF-8
- 支持中文字符参数

**核心功能模块：**
- 🏥 医院层级数据管理（省→市→区县→医院）
- 🌐 医院官网自动发现与更新
- 🕷️ 采购信息智能爬取（支持深度爬取）
- 🔄 批量数据处理与更新
- 📊 异步任务管理与监控
- 🔍 全文搜索与分页查询

---

## 系统管理接口

### 1. 清空所有任务记录
**接口：** `DELETE /tasks/clear`

**功能描述：** 删除所有任务记录，用于清理任务历史数据

**请求参数：** 无

**响应示例：**
```json
{
  "code": 200,
  "message": "所有任务记录已成功删除",
  "data": {
    "status": "success",
    "cleared_at": "2025-11-23T15:30:45.123456"
  }
}
```

**使用场景：**
- 定期清理历史任务数据
- 系统维护前重置任务状态
- 测试环境数据清理

---

### 2. 健康检查
**接口：** `GET /health`

**功能描述：** 检查服务运行状态

**请求参数：** 无

**响应示例：**
```json
{
  "status": "healthy"
}
```

**使用场景：**
- 服务监控和健康检查
- 负载均衡器状态探测
- 容器化部署的存活检查

---

## 医院网站管理接口

### 8. 医院官网查询与更新
**接口：** `POST /hospital/website`

**功能描述：** 根据医院名称智能查询官方网站，并更新数据库中的网站字段

**请求参数：**
```json
{
  "hospital_name": "北京协和医院",
  "force_update": false
}
```

**参数说明：**
- `hospital_name` (必需): 医院全称或通用名称
- `force_update` (可选): 是否强制更新已有网站信息，默认false

**响应示例：**
```json
{
  "success": true,
  "data": {
    "hospital_id": 123,
    "hospital_name": "北京协和医院",
    "previous_website": null,
    "new_website": "https://www.pumch.cn",
    "updated": true,
    "llm_response_time": 2.3,
    "database_update_time": 0.05,
    "total_time": 2.35,
    "request_id": "REQ-ABC12345"
  },
  "message": "医院网站信息更新成功",
  "timestamp": "2025-11-25T15:30:00"
}
```

**功能特性：**
- 🤖 使用大语言模型智能识别官网地址
- 🗄️ 自动更新数据库中的website字段
- 📊 详细的性能指标和请求追踪
- 🔍 支持智能跳过已有网站信息
- 📝 完整的操作日志记录

**使用场景：**
- 批量初始化医院网站信息
- 定期更新医院官网地址
- 验证现有网站链接的有效性
- 医院信息完整性补全

---

### 9. 批量更新医院网站
**接口：** `POST /hospitals/websites/batch-update`

**功能描述：** 批量获取医院信息并更新官网地址，支持多种更新模式

**请求参数：**
```json
{
  "update_all": false,
  "hospital_ids": [1, 2, 3, 4, 5],
  "limit": 100,
  "skip_existing": true
}
```

**参数说明：**
- `update_all` (可选): 是否更新所有医院，默认false
- `hospital_ids` (可选): 指定医院ID列表进行更新
- `limit` (可选): 限制更新数量，默认100
- `skip_existing` (可选): 是否跳过已有网站信息的医院，默认true

**响应示例：**
```json
{
  "success": true,
  "data": {
    "total_hospitals": 500,
    "processed_count": 100,
    "updated_count": 45,
    "skipped_count": 40,
    "failed_count": 15,
    "start_time": "2025-11-25T15:00:00",
    "end_time": "2025-11-25T15:30:00",
    "total_time": 1800.5,
    "results": [
      {
        "hospital_id": 1,
        "hospital_name": "北京协和医院",
        "previous_website": null,
        "new_website": "https://www.pumch.cn",
        "success": true,
        "updated": true,
        "error_message": null,
        "total_time": 2.5,
        "request_id": "REQ-001"
      }
    ],
    "request_id": "BATCH-REQ-ABC12345"
  },
  "message": "批量更新完成，成功更新45家医院网站信息",
  "timestamp": "2025-11-25T15:30:00"
}
```

**更新模式：**
1. **全量更新**: `update_all=true` - 更新所有医院
2. **指定ID更新**: 提供`hospital_ids`列表 - 只更新指定医院
3. **限制数量更新**: 设置`limit` - 限制更新医院数量
4. **智能跳过**: `skip_existing=true` - 跳过已有网站信息的医院

**功能特性：**
- 🔄 串行处理避免并发冲突
- 📊 实时进度统计和详细结果
- 🎯 多种更新模式灵活组合
- 🛡️ 完善的错误处理和恢复机制
- ⏱️ 详细的性能指标统计

**使用场景：**
- 系统初始化时批量补充医院网站
- 定期维护医院官网信息
- 特定医院群组的网站更新
- 数据完整性验证和修复

---

## 采购信息爬取接口

### 10. 采购信息链接爬取
**接口：** `POST /procurement/crawl`

**功能描述：** 从指定URL开始深度爬取采购相关页面链接，自动过滤并存储到数据库

**请求参数：**
```json
{
  "base_url": "https://www.hospital-cqmu.com/gzb_cgxx",
  "max_depth": 5,
  "max_pages": 27
}
```

**参数说明：**
- `base_url` (必需): 起始爬取URL，通常是医院采购信息页面
- `max_depth` (可选): 最大爬取深度，默认5
- `max_pages` (可选): 最多爬取页面数，默认27

**响应示例：**
```json
{
  "base_url": "https://www.hospital-cqmu.com/gzb_cgxx",
  "total_urls": 15,
  "new_or_updated": 12,
  "db_path": "data/hospital_scanner_new.db"
}
```

**技术实现：**
- 🚀 **主要方案**: crawl4ai + Playwright (Linux/macOS)
- 🔧 **备用方案**: requests + BeautifulSoup (Windows兼容)
- 🎯 **智能过滤**: 仅保存.html/.htm/.shtml结尾的页面
- 🏗️ **爬取策略**: BFS广度优先搜索
- 📊 **数据存储**: SQLite数据库procurement_links表

**功能特性：**
- 🌐 跨平台兼容性（Windows/Linux/macOS）
- 🎯 智能HTML页面识别和过滤
- 📈 深度爬取与页面数量限制
- 💾 自动去重和增量更新
- 📝 详细的爬取过程日志

**爬取流程：**
1. 从base_url开始，使用BFS策略遍历页面
2. 仅保存同域名的HTML页面链接
3. 过滤图片、CSS、JS等静态资源
4. 自动解析相对链接为绝对链接
5. 结果存储到数据库procurement_links表

**使用场景：**
- 医院采购信息收集和分析
- 政府采购数据挖掘
- 招投标信息监控系统
- 供应链数据分析

**注意事项：**
- ⚠️ 该接口为实时执行，可能需要数十秒完成
- 🔄 Windows环境自动切换到备用爬取方案
- ⏱️ 建议在前端设置较长的超时时间
- 📊 爬取结果可通过数据库查询

---

## 数据查询接口

### 11. 获取省份列表
**接口：** `GET /provinces`

**功能描述：** 获取全国省级行政区划列表，支持分页

**请求参数：**
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20

**请求示例：**
```
GET /provinces?page=1&page_size=20
```

**响应示例：**
```json
{
  "items": [
    {
      "id": 1,
      "name": "北京市",
      "code": "110000",
      "created_at": "2025-11-23T10:00:00"
    },
    {
      "id": 2,
      "name": "上海市",
      "code": "310000",
      "created_at": "2025-11-23T10:00:01"
    }
  ],
  "total": 34,
  "page": 1,
  "page_size": 20,
  "pages": 2,
  "has_next": true,
  "has_prev": false
}
```

**使用场景：**
- 获取全国省份列表用于下拉选择
- 省份数据统计分析
- 地理信息系统基础数据

---

### 12. 获取城市列表
**接口：** `GET /cities`

**功能描述：** 获取指定省份下的城市列表，支持分页

**请求参数：**
- `province` (可选): 省份名称（中文），支持URL编码
- `province_id` (可选): 省份ID（数字）
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20

**请求示例：**
```
GET /cities?province=广东省&page=1&page_size=20
GET /cities?province_id=19&page=1&page_size=50
```

**响应示例：**
```json
{
  "items": [
    {
      "id": 201,
      "name": "广州市",
      "province_id": 19,
      "created_at": "2025-11-23T10:05:00"
    },
    {
      "id": 202,
      "name": "深圳市",
      "province_id": 19,
      "created_at": "2025-11-23T10:05:01"
    }
  ],
  "total": 21,
  "page": 1,
  "page_size": 20,
  "pages": 2,
  "has_next": true,
  "has_prev": false
}
```

**使用场景：**
- 根据省份获取下属城市列表
- 级联选择器的城市数据源
- 区域性数据分析

---

### 13. 获取区县列表
**接口：** `GET /districts`

**功能描述：** 获取指定城市下的区县列表，支持分页

**请求参数：**
- `city` (可选): 城市名称（中文），支持URL编码
- `city_id` (可选): 城市ID（数字）
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20

**请求示例：**
```
GET /districts?city=广州市&page=1&page_size=20
GET /districts?city_id=201&page=1&page_size=30
```

**响应示例：**
```json
{
  "items": [
    {
      "id": 3001,
      "name": "越秀区",
      "city_id": 201,
      "created_at": "2025-11-23T10:10:00"
    },
    {
      "id": 3002,
      "name": "海珠区",
      "city_id": 201,
      "created_at": "2025-11-23T10:10:01"
    }
  ],
  "total": 11,
  "page": 1,
  "page_size": 20,
  "pages": 1,
  "has_next": false,
  "has_prev": false
}
```

**使用场景：**
- 获取城市下属区县信息
- 精确定位到医院所在区域
- 城市规划和区域分析

---

### 14. 获取医院列表
**接口：** `GET /hospitals`

**功能描述：** 获取指定区县下的医院列表，支持分页

**请求参数：**
- `district` (可选): 区县名称（中文），支持URL编码
- `district_id` (可选): 区县ID（数字）
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20

**请求示例：**
```
GET /hospitals?district=越秀区&page=1&page_size=20
GET /hospitals?district_id=3001&page=1&page_size=50
```

**响应示例：**
```json
{
  "items": [
    {
      "id": 10001,
      "name": "广东省人民医院",
      "district_id": 3001,
      "level": "三级甲等",
      "address": "广州市越秀区中山二路106号",
      "phone": "020-83827812",
      "website": "www.gdph.org.cn",
      "beds_count": 2800,
      "departments": ["内科", "外科", "妇产科", "儿科"],
      "created_at": "2025-11-23T10:15:00"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20,
  "pages": 1,
  "has_next": false,
  "has_prev": false
}
```

**使用场景：**
- 区域医疗资源查询
- 医院信息统计分析
- 就医指南和导航服务

---

### 15. 搜索医院
**接口：** `GET /hospitals/search`

**功能描述：** 根据关键词搜索医院，支持医院名称模糊匹配

**请求参数：**
- `q` (必需): 搜索关键词
- `limit` (可选): 返回结果数量限制，默认20

**请求示例：**
```
GET /hospitals/search?q=人民医院&limit=10
GET /hospitals/search?q=广州医院&limit=50
```

**响应示例：**
```json
{
  "query": "人民医院",
  "limit": 10,
  "results": [
    {
      "id": 10001,
      "name": "广东省人民医院",
      "district_id": 3001,
      "level": "三级甲等",
      "address": "广州市越秀区中山二路106号",
      "phone": "020-83827812"
    }
  ],
  "count": 1
}
```

**使用场景：**
- 快速查找特定医院
- 医院名称模糊搜索
- 移动端医院查询功能

---

## 数据刷新接口

### 16. 完整数据刷新
**接口：** `POST /refresh/all`

**功能描述：** 执行全国范围的完整数据刷新，包括所有省份、城市、区县和医院的层级数据

**执行流程：**
1. 调用LLM获取全国所有省级行政区划
2. 对每个省份自动调用省份数据刷新接口
3. 获取每个省份下的所有城市数据
4. 获取每个城市下的所有区县数据
5. 确保完整层级关系的正确性

**请求参数：** 无

**响应示例：**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "完整数据刷新任务已创建，正在后台处理中...",
  "created_at": "2025-11-23T15:00:00"
}
```

**特点：**
- 覆盖全国所有省级行政区划
- 自动化批量处理
- 完整的四级数据体系（省→市→区县→医院）
- 支持断点续传，失败的省份可以单独重试

**使用场景：**
- 初始化系统数据
- 定期全量数据更新
- 数据修复和完整性检查

**注意事项：**
- 这是一个长时间运行的后台任务
- 建议在系统负载较低时执行
- 可以通过 task_id 查询任务进度

---

### 17. 省份数据刷新
**接口：** `POST /refresh/province/{province_name}`

**功能描述：** 根据省份名称刷新该省份下的城市数据

**路径参数：**
- `province_name`: 省份名称（中文），如"广东省"、"浙江省"等

**执行流程：**
1. 调用LLM获取指定省份下的所有地级市、自治州、地区等
2. 检查省份是否存在，不存在则创建新省份记录
3. 批量创建获取到的所有城市记录
4. 确保数据的完整性和正确性

**请求示例：**
```
POST /refresh/province/广东省
POST /refresh/province/浙江省
```

**响应示例：**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "message": "省份 广东省 数据刷新任务已创建，正在后台处理中...",
  "created_at": "2025-11-23T15:05:00"
}
```

**特点：**
- 仅处理省份和城市数据，不处理区县和医院
- 自动去重：避免重复创建相同城市记录
- 详细日志记录每个步骤的执行情况

**使用场景：**
- 新增省份的数据采集
- 特定省份的城市数据更新
- 省级行政区划变更后的数据同步

---

### 18. 区县医院数据刷新
**接口：** `POST /refresh/district/{district_name}`

**功能描述：** 根据区县名称刷新该区县内的所有医院数据

**路径参数：**
- `district_name`: 区县名称（中文），如"朝阳区"、"海淀区"等

**执行流程：**
1. 验证区县是否存在于数据库中
2. 调用LLM获取区县内所有医院的详细信息
3. 自动识别医院等级（三甲、三乙、二甲等）
4. 获取医院联系方式（地址、电话、网站）
5. 智能去重，避免重复创建相同医院记录

**请求示例：**
```
POST /refresh/district/朝阳区
POST /refresh/district/海淀区
```

**响应示例：**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440002",
  "message": "区县 朝阳区 医院数据刷新任务已创建，正在后台处理中...",
  "created_at": "2025-11-23T15:10:00"
}
```

**功能特性：**
- 调用阿里百炼LLM获取区县内所有医院的详细信息
- 自动识别医院等级和类型
- 获取完整的联系方式信息
- 智能去重机制
- 异步后台处理

**使用场景：**
- 特定区域医疗资源普查
- 医院信息定期更新
- 新开发区域的医疗数据采集

---

### 19. 省份城市区县级联刷新
**接口：** `POST /refresh/province-cities-districts/{province_name}`

**功能描述：** 根据省份名称级联刷新该省份下所有城市、区县数据，为医院数据采集做准备

**路径参数：**
- `province_name`: 省份名称（中文）

**执行流程：**
1. 获取指定省份下的所有城市列表
2. 对每个城市检查是否存在，不存在则创建
3. 获取每个城市下的所有区县
4. 创建区县记录并建立完整的层级关系
5. 验证数据的完整性和一致性

**请求示例：**
```
POST /refresh/province-cities-districts/广东省
POST /refresh/province-cities-districts/江苏省
```

**响应示例：**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440003",
  "message": "省份 广东省 的城市、区县及医院数据级联刷新任务已创建，正在后台处理中...",
  "created_at": "2025-11-23T15:15:00"
}
```

**特性：**
- 不对输入省份名称进行验证，支持任意省份名称
- 自动去重：避免重复创建相同记录
- 详细日志：记录每个步骤的执行情况
- 异步处理：后台执行级联刷新任务

**与省份数据刷新的区别：**
- 本接口处理完整的省份→城市→区县数据链
- 省份数据刷新接口仅处理省份和城市数据

**使用场景：**
- 完整省份的行政区划数据采集
- 为后续医院数据采集建立基础框架
- 省级数据完整性检查和修复

---

### 20. 全国扫描 - 所有省份级联刷新
**接口：** `POST /refresh/all-provinces`

**功能描述：** 启动全国范围的医院数据扫描，级联刷新所有省份的城市、区县和医院数据

**执行逻辑：**
1. 首先从LLM获取全国所有省份列表
2. 依次对每个省份执行级联刷新（包含城市、区县、医院）
3. 使用串行处理避免过度并发导致API限流
4. 提供详细的进度日志和错误处理

**请求参数：** 无

**响应示例：**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440004",
  "message": "全国扫描任务已启动，将依次扫描所有省份的城市、区县和医院数据",
  "created_at": "2025-11-23T15:20:00"
}
```

**特性：**
- 🌍 覆盖全国所有省级行政区
- 📊 实时进度跟踪和详细日志记录
- 🔁 自动重试机制和错误恢复
- ⚡ 智能任务队列管理
- 🛡️ API限流保护和并发控制

**使用示例：**
```python
# 启动全国扫描
response = client.post("/refresh/all-provinces")
task_id = response.json()["task_id"]

# 查询进度
status = client.get(f"/tasks/{task_id}")
progress = status.json()["data"]["progress"]
```

**使用场景：**
- 系统初始化时的全国数据采集
- 定期全量数据更新（建议月度或季度）
- 全国医疗资源普查
- 数据完整性验证和修复

**注意事项：**
- 这是耗时最长的操作，可能需要数小时完成
- 建议在系统负载较低的时间段执行
- 任务过程中可以实时查询进度
- 失败的省份会记录详细错误信息，可单独重试

### 21. 单医院扫描
**接口：** `POST /scan`

**功能描述：** 创建单个医院的详细扫描任务，获取全面的医院信息

**请求参数：**
```json
{
  "hospital_name": "北京协和医院",
  "url": "https://www.pumch.cn"
}
```

**参数说明：**
- `hospital_name` (必需): 医院名称
- `url` (可选): 医院官网URL，用于辅助信息采集

**响应示例：**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440005",
  "message": "医院扫描任务已创建，正在后台处理中...",
  "created_at": "2025-11-25T16:00:00"
}
```

---

### 22. 城市医院数据刷新
**接口：** `POST /refresh/city/{city_name}`

**功能描述：** 根据城市名称刷新该城市下所有区县的医院数据

**路径参数：**
- `city_name`: 城市名称（中文），如"广州市"、"深圳市"等

**执行流程：**
1. 获取指定城市下的所有区县列表
2. 对每个区县调用医院数据刷新接口
3. 批量处理医院信息的创建和更新
4. 提供详细的处理进度和结果统计

**请求示例：**
```
POST /refresh/city/广州市
POST /refresh/city/深圳市
```

**响应示例：**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440006",
  "message": "城市 广州市 医院数据刷新任务已创建，正在后台处理中...",
  "created_at": "2025-11-25T16:05:00"
}
```

**使用场景：**
- 城市级医疗资源全面普查
- 区域医疗数据更新和维护
- 新增城市的医院信息采集

---

## 任务管理接口

### 23. 任务状态查询
**接口：** `GET /task/{task_id}`

**功能描述：** 查询指定任务的执行状态和详细结果

**路径参数：**
- `task_id`: 任务ID，由其他接口返回

**响应示例：**
```json
{
  "code": 200,
  "message": "获取任务状态成功",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "type": "NATIONWIDE",
    "status": "running",
    "progress": "正在处理第 15/34 个省份：湖北省",
    "result": null,
    "error": null,
    "created_at": "2025-11-25T15:00:00",
    "updated_at": "2025-11-25T15:45:30",
    "completed_at": null
  }
}
```

**任务状态说明：**
- `pending`: 等待执行
- `running`: 正在执行
- `completed`: 执行完成
- `failed`: 执行失败
- `cancelled`: 已取消

**任务类型说明：**
- `HOSPITAL`: 单医院扫描
- `PROVINCE`: 省份数据刷新
- `NATIONWIDE`: 全国扫描

---

### 24. 任务列表查询
**接口：** `GET /tasks`

**功能描述：** 获取所有任务的列表，支持分页和状态过滤

**请求参数：**
- `status` (可选): 按状态过滤 (pending/running/completed/failed)
- `type` (可选): 按类型过滤 (HOSPITAL/PROVINCE/NATIONWIDE)
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20

**请求示例：**
```
GET /tasks?status=running&page=1&page_size=10
GET /tasks?type=NATIONWIDE&page=1
```

**响应示例：**
```json
{
  "code": 200,
  "message": "获取任务列表成功",
  "data": {
    "items": [
      {
        "task_id": "550e8400-e29b-41d4-a716-446655440000",
        "type": "NATIONWIDE",
        "status": "running",
        "progress": "正在处理第 15/34 个省份：湖北省",
        "created_at": "2025-11-25T15:00:00",
        "updated_at": "2025-11-25T15:45:30"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

### 25. 任务清理
**接口：** `POST /tasks/cleanup`

**功能描述：** 清理已完成的任务记录，支持指定时间范围

**请求参数：**
- `hours` (可选): 清理多少小时前完成的任务，默认1小时

**请求示例：**
```
POST /tasks/cleanup
POST /tasks/cleanup/24  # 清理24小时前完成的任务
```

**响应示例：**
```json
{
  "code": 200,
  "message": "任务清理完成",
  "data": {
    "cleaned_count": 15,
    "cleaned_time": "2025-11-25T16:10:00"
  }
}
```

---

### 26. 删除所有任务记录
**接口：** `DELETE /tasks/clear`

**功能描述：** 删除所有任务记录，用于测试或重置

**响应示例：**
```json
{
  "code": 200,
  "message": "所有任务记录已成功删除",
  "data": {
    "status": "success",
    "cleared_at": "2025-11-25T16:15:00",
    "deleted_count": 150
  }
}
```

---

## 数据管理接口

### 27. 清空数据库
**接口：** `DELETE /database/clear`

**功能描述：** 清空所有业务数据（省、市、区县、医院），保留表结构

**响应示例：**
```json
{
  "code": 200,
  "message": "数据库已清空，表结构保留",
  "data": {
    "status": "success",
    "cleared_at": "2025-11-25T16:20:00",
    "tables_cleared": ["provinces", "cities", "districts", "hospitals"]
  }
}
```

**使用场景：**
- 系统重置和重新初始化
- 测试环境数据清理
- 数据迁移前准备

---

## 系统监控接口

### 28. 服务信息
**接口：** `GET /`

**功能描述：** 获取服务基本信息和统计数据

**响应示例：**
```json
{
  "service": "HBScan (医院层级扫查微服务)",
  "version": "1.0.0",
  "status": "running",
  "uptime": "2 days, 5 hours, 30 minutes",
  "statistics": {
    "provinces_count": 34,
    "cities_count": 450,
    "districts_count": 3200,
    "hospitals_count": 28000,
    "tasks_total": 1250,
    "tasks_running": 2,
    "tasks_completed": 1200
  }
}
```

---

## 任务状态查询详解

所有数据刷新接口都会返回一个 `task_id`，可以通过以下方式查询任务执行状态：

**查询接口：** `GET /task/{task_id}`

**响应示例：**
```json
{
  "code": 200,
  "message": "获取任务状态成功",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "running",
    "progress": "正在处理第 15/34 个省份：湖北省",
    "created_at": "2025-11-23T15:00:00",
    "updated_at": "2025-11-23T15:45:30"
  }
}
```

**任务状态说明：**
- `pending`: 等待执行
- `running`: 正在执行
- `completed`: 执行完成
- `failed`: 执行失败
- `cancelled`: 已取消

---

## 错误处理

### 通用错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

### 常见错误码
- `400`: 请求参数错误
- `404`: 资源不存在
- `409`: 任务冲突（如重复的全国扫描任务）
- `500`: 服务器内部错误

### 中文参数编码
所有支持中文参数的接口都已正确处理URL编码，可以直接使用中文字符：

```
# 正确的请求示例
GET /cities?province=广东省
GET /districts?city=广州市
GET /hospitals?district=越秀区
POST /refresh/province/广东省
POST /refresh/district/朝阳区
```

---

## 开发和测试接口

### 29. 测试区县接口
**接口：** `POST /test/district`

**功能描述：** 测试区县接口注册和路由，用于开发调试

**使用场景：**
- API路由测试
- 开发环境调试
- 接口连通性验证

---

### 30. 测试城市接口
**接口：** `POST /test/city`

**功能描述：** 测试城市接口注册和路由，用于开发调试

**使用场景：**
- API路由测试
- 开发环境调试
- 接口连通性验证

---

## 技术特性与架构

### 🌐 跨平台兼容性
- **Windows环境**: 自动切换到requests+BeautifulSoup备用爬取方案
- **Linux/macOS**: 使用crawl4ai+Playwright完整功能
- **智能降级**: 确保核心功能在所有环境下稳定运行

### 🔄 异步任务管理
- **TaskManager**: 企业级任务调度和管理系统
- **双存储**: 内存+SQLite双重持久化
- **状态追踪**: 完整的任务生命周期管理
- **并发控制**: 基于信号量的资源限制

### 🤖 智能数据采集
- **LLM集成**: 支持阿里百炼、OpenAI等多种LLM服务
- **结构化提取**: JSON格式的数据解析和验证
- **智能去重**: 基于名称和URL的重复检测
- **错误恢复**: 完善的重试和降级机制

### 📊 数据库架构
- **层级设计**: 省→市→区县→医院四级关联结构
- **索引优化**: 基于查询场景的性能优化
- **事务支持**: ACID特性的数据一致性保证
- **WAL模式**: 高并发的读写性能优化

---

## 部署和配置

### 环境要求
- Python 3.8+
- SQLite 3.x (默认) / PostgreSQL (可选)
- LLM服务API Key (阿里百炼/DeepSeek/OpenAI等)

### 核心依赖
```bash
# Web框架
fastapi==0.104.1
uvicorn[standard]==0.24.0

# LLM和爬取
requests==2.31.0
crawl4ai>=0.3.0
playwright>=1.40.0

# 数据处理
pydantic==2.5.0
beautifulsoup4==4.12.2

# 系统兼容
nest-asyncio==1.6.0  # Windows兼容性
```

### 配置示例
```bash
# LLM服务配置
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://dashscope.aliyuncs.com/api/v1/
LLM_MODEL=qwen-turbo

# 数据库配置
DATABASE_URL=sqlite:///data/hospital_scanner.db

# 性能配置
MAX_CONCURRENT_TASKS=10
MAX_CONCURRENT_DISTRICT_REFRESHES=3
```

---

## 使用建议

### 🚀 最佳实践

#### 数据初始化流程
```bash
# 1. 获取省份数据
POST /refresh/all

# 2. 完整层级数据采集
POST /refresh/all-provinces

# 3. 批量补充医院网站
POST /hospitals/websites/batch-update
{
  "update_all": true,
  "skip_existing": false
}
```

#### 增量更新策略
```bash
# 特定省份更新
POST /refresh/province-cities-districts/广东省

# 城市医院数据更新
POST /refresh/city/广州市

# 区县医院详细扫描
POST /refresh/district/朝阳区
```

#### 任务监控和管理
```bash
# 查询任务进度
GET /task/{task_id}

# 获取运行中任务
GET /tasks?status=running

# 清理历史任务
POST /tasks/cleanup/24
```

### ⚡ 性能优化建议

#### 1. 任务调度优化
- 避免同时执行多个全国扫描任务
- 合理设置并发限制参数
- 在系统负载较低时执行大规模操作

#### 2. 分页查询优化
```bash
# 推荐的分页参数
GET /provinces?page=1&page_size=50
GET /cities?province=广东省&page=1&page_size=100
GET /hospitals?district=朝阳区&page=1&page_size=200
```

#### 3. 批量操作优化
```bash
# 分批处理大量医院
POST /hospitals/websites/batch-update
{
  "limit": 50,
  "skip_existing": true
}
```

### 🛡️ 错误处理和故障恢复

#### 常见错误处理
- **网络超时**: 增加请求超时时间，检查网络连接
- **LLM限流**: 降低请求频率，考虑多个API Key轮换
- **数据库锁定**: 使用WAL模式，避免长时间事务

#### 任务失败恢复
```bash
# 检查失败原因
GET /task/{task_id}

# 重新执行失败任务
POST /refresh/province/{省份名称}
```

### 📝 监控和日志

#### 日志文件位置
- **主日志**: `logs/scanner.log`
- **LLM调试**: `logs/llm_debug.log`

#### 关键监控指标
- 任务执行状态和进度
- LLM API调用频率和响应时间
- 数据库连接池使用情况
- 系统资源使用率

---

## API版本信息

- **当前版本**: v1.0.0
- **文档版本**: 2025-11-25
- **兼容性**: 支持Python 3.8+，Windows/Linux/macOS
- **数据格式**: JSON (UTF-8编码)
- **认证方式**: 暂无（内网部署）

---

## 技术支持

如遇到问题，请检查：
1. 系统日志文件中的错误信息
2. 任务执行状态和错误详情
3. 网络连接和API Key配置
4. 系统资源使用情况

**更新日志**:
- 2025-11-25: 新增医院网站管理接口和采购信息爬取功能
- 2025-11-25: 优化Windows兼容性和跨平台支持
- 2025-11-25: 完善任务管理和错误处理机制