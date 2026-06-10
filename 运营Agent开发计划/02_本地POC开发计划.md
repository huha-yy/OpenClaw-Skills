# 阶段 1：本地 POC 开发计划

## 1. 阶段目标

本阶段目标是在本地跑通最小可用闭环：

```text
一个热点输入 → 相关性判断 → 多源摘要 → 三平台内容包 → 风险报告 → 发布包输出
```

第一版 POC 不追求复杂系统架构，优先验证业务流程是否成立、内容输出是否有价值。

## 2. 输入

本地 POC 需要准备：

```text
configs/company_keywords.yaml        # 公司、产品、行业、竞品关键词
configs/brand_guidelines.md          # 品牌口径和禁用表达
configs/hotspot_sources.yaml         # 热点源配置
samples/mock_hotspot.json            # mock 热点输入
samples/reference_contents/          # 历史优秀内容样例
```

## 3. 输出

POC 输出标准发布包：

```text
outputs/
  热点标题/
    sources.json
    event_analysis.md
    risk_report.md
    package_summary.md

    xiaohongshu/
      note.md
      image_storyboard.md
      image_cards.json
      publish_meta.json

    douyin/
      video_script.md
      storyboard.md
      subtitles.srt
      cover.md
      publish_meta.json

    wechat/
      article.md
      cover.md
      inline_images.md
      layout.md
      publish_meta.json
```

## 4. POC 功能拆分

### 4.1 热点输入

第一版可以先用 mock 数据，不必马上接真实平台。

原因：

- 降低外部依赖。
- 优先验证后续内容生成链路。
- 方便反复测试同一个热点。

### 4.2 相关性判断

根据关键词和模型判断热点是否相关。

输出：

```text
相关性分数：
相关类型：直接相关/行业相关/竞品相关/借势相关/不相关
命中关键词：
判断理由：
```

### 4.3 多源摘要

对热点来源进行整理。

第一版输出：

```text
来源链接：
来源媒体：
发布时间：
事实点：
不确定信息：
```

### 4.4 内容策略

生成平台内容角度。

输出：

```text
推荐角度：
适合平台：
不适合平台：
风险提示：
```

### 4.5 三平台内容包

分别生成：

```text
小红书图文内容包
抖音视频内容包
微信公众号图文文章包
```

### 4.6 风险报告

输出风险等级：

```text
low / medium / high
```

并说明是否需要人工审核。

## 5. 验收标准

本阶段验收标准：

```text
1. 输入一个热点后，可以生成完整发布包。
2. 发布包内包含三平台内容。
3. 每个平台内容不是单纯文案，而是包含图文/视频协同结构。
4. 输出包含来源链接和事实摘要。
5. 输出包含风险提示。
6. 运营可以基于发布包进行人工修改和发布。
```

## 6. 本阶段不做

```text
1. 不做真实平台自动发布。
2. 不做自动点赞、评论、转发。
3. 不做复杂前端审核页面。
4. 不做生产级数据库。
5. 不做多账号管理。
```
