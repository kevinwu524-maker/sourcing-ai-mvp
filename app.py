# -*- coding: utf-8 -*-
"""
Client Profile & Route Recommender - 三轴就绪度重构版
运行方式：python3 -m streamlit run app.py
"""

import re
import csv
import io
from datetime import datetime
from typing import Dict, List, Tuple, Any

import streamlit as st

# ============================================================
# CONFIG：运营可直接改这里，不需要改下方逻辑
# ============================================================
CONFIG: Dict[str, Any] = {
    "weights": {
        "supply_stability": 20,
        "paid_marketing_willingness": 25,
        "private_traffic": 15,
        "ecommerce_foundation": 15,
        "existing_sales": 15,
        "materials_readiness": 10,
    },
    "axis": {
        "Sourcing": {
            "label": "Sourcing轴：货源稳定性",
            "max": 20,
            "components": ["supply_stability"],
            "ready_min": 15,
            "not_ready_max": 0,
        },
        "Marketing": {
            "label": "Marketing轴：付费营销意愿 + 私域规模 + 原渠道销售表现",
            "max": 55,
            "components": ["paid_marketing_willingness", "private_traffic", "existing_sales"],
            "ready_min": 38,
            "not_ready_max": 14,
            "paid_zero_force_not_ready": True,
        },
        "Build": {
            "label": "建站自助轴：建站电商基础 + 电子物料完备度",
            "max": 25,
            "components": ["ecommerce_foundation", "materials_readiness"],
            "ready_min": 20,
            "not_ready_max": 7,
        },
    },
    "readiness_labels": {
        "ready": "Ready",
        "need_evidence": "待补证据",
        "not_ready": "Not Ready",
    },
    "component_options": {
        "supply_stability": [
            (20, "自有稳定供应链/资深电商自带货"),
            (15, "无货源，但品类可做"),
            (10, "无货源，风险中等，需要进一步评估"),
            (0, "风险高，做不了，直接归零"),
        ],
        "paid_marketing_willingness": [
            (25, "有明确预算≥$2,000，或投过付费广告"),
            (15, "有兴趣，愿意小额测试"),
            (0, "只要免费工具/不投营销，服务封顶L2自助"),
        ],
        "private_traffic": [
            (15, "成规模私域，互动率ER≥3%"),
            (8, "少量私域"),
            (7, "无私域，中性"),
            (0, "完全无线上流量"),
        ],
        "ecommerce_foundation": [
            (15, "做过Amazon/Shopify/TikTok Shop"),
            (8, "做过其他电商平台"),
            (0, "纯新手"),
        ],
        "existing_sales": [
            (15, "近半年稳定GMV≥$5,000"),
            (8, "少量/偶发销售"),
            (7, "不适用，如纯网红转电商，中性"),
            (0, "无销售记录"),
        ],
        "materials_readiness": [
            (10, "产品图 + 视频/素材齐全"),
            (5, "部分齐全"),
            (0, "几乎没有"),
        ],
    },
    "compliance": {
        "red": {
            "label": "红线",
            "keywords": [
                "违禁药", "违禁药品", "毒品", "麻醉品", "麻醉药品", "精神药品", "冰毒", "海洛因", "可卡因",
                "narcotic", "psychotropic", "cocaine", "heroin", "meth", "methamphetamine",
                "weapon", "gun", "firearm", "ammo", "弹药", "枪支", "knife", "管制刀具", "武器",
                "烟草", "电子烟", "电子烟油", "烟油", "烟弹", "雾化器", "一次性电子烟", "尼古丁", "尼古丁盐",
                "vape", "vapes", "vaping", "vape pen", "e-cigarette", "e-cig", "ecig", "disposable vape", "nicotine",
                "成人内容", "赌博", "casino", "博彩", "老虎机", "slot machine",
                "仿牌", "高仿", "山寨", "盗版", "counterfeit", "replica", "knockoff",
                "大麻", "cbd", "thc", "金融理财", "unauthorized finance",
                "危化品", "hazardous chemical", "steroid", "类固醇", "合成代谢", "controlled substance",
            ],
            "action": "直接否决，不进入付款、广告或sourcing流程。",
        },
        "gray": {
            "label": "灰色",
            "keywords": [
                "膳食补剂", "supplement", "保健品", "美容仪", "医疗器械", "medical device", "成人非露骨",
                "博彩周边", "烟具", "smoking accessory", "功效护肤", "祛痘", "减肥", "减脂", "美白", "丰胸",
                "下火", "排毒", "壮阳", "补肾", "增高", "处方药", "prescription drug",
                "治疗", "疗效", "anti-aging", "weight loss", "health claim",
            ],
            "action": "只能走CPL；CPC/CPS需要审批后再判断。",
        },
        "green": {
            "label": "合规",
            "keywords": [
                "服装", "鞋", "帽", "家居", "美妆", "3c配件", "手机壳", "宠物", "母婴", "运动户外", "饰品", "箱包", "食品",
                "fashion", "home", "beauty", "phone case", "pet", "baby", "outdoor", "jewelry", "bag", "accessories",
            ],
            "action": "CPC/CPS/CPL三渠道都可做。",
        },
    },
    "marketing_subtypes": {
        "AI社媒矩阵号": "内容蓄水冷启动，反哺其他渠道。",
        "CPS网红营销": "强展示、可寄样、佣金空间足的商品。",
        "CPL分销员": "渠道型/私域型分销驱动。",
        "CPL Leads": "B2B批发/OEM/工厂/询盘型高客单、长决策链，需要24h跟单。",
        "CPC投放": "页面、Pixel、Tracking、预算ready，适合快速测品放量。",
    },
    "value_gate": {
        "free_caps_priority": "L2自助",
        "high_budget_min": 2000,
        "high_budget_lift": 1,
    },
    "service_rules": {
        "all_ready": {
            "combo": ["Sourcing", "建站自助", "营销"],
            "main": "全链路服务",
            "aux": "按里程碑分阶段推进",
            "rhythm": "长周期",
        },
        "nurture": {
            "combo": ["Nurture"],
            "main": "待培育",
            "aux": "先补基础信息和证据，不进入重投入流程",
            "rhythm": "待培育",
        },
    },
    "priority_order": ["L2自助", "L1低", "M中", "H高"],
    "lark_fields": [
        "客户编号", "ClientType", "PainPoint", "Sourcing就绪度", "营销就绪度", "建站就绪度", "服务组合", "主方案",
        "营销子类型", "合规档", "价值档", "节奏", "证据置信度", "SystemRoute", "归因说明", "AM阶段状态", "Status",
    ],
    "keywords": {
        "ecommerce": ["shopify", "amazon", "亚马逊", "tiktok shop", "etsy", "depop", "whatnot", "店铺", "电商", "独立站", "订单", "gmv", "sku", "上架", "listing", "产品", "商品", "供应链", "采购", "分销", "达人", "佣金", "moq", "广告", "pixel", "ga4", "whatsapp", "站点", "store"],
        "sourcing_pain": ["sourcing", "找货", "货源", "供应商", "factory", "工厂", "supplier", "moq", "采购", "打样", "定制"],
        "traffic_pain": ["traffic", "流量", "获客", "ads", "广告", "曝光", "cpc", "放量", "投放"],
        "affiliate_pain": ["affiliate", "creator", "网红", "达人", "kol", "koc", "佣金", "cps", "带货"],
        "distributor_pain": ["distributor", "reseller", "分销", "代理", "批发", "wholesale", "渠道"],
        # 注意：不要放裸词"工厂"，会让"自有工厂供应链"这类现有卖家被误判出B2B Leads痛点。
        "leads_pain": ["lead", "leads", "询盘", "表单", "b2b", "oem", "odm", "manufacturer", "报价", "代工", "贴牌"],
        "store_pain": ["store setup", "建站", "独立站", "网站", "shopify", "product page", "listing", "上架"],
        "conversion_pain": ["conversion", "转化", "checkout", "页面", "落地页", "详情页", "客单价", "aov", "ltv"],
        "logistics_pain": ["logistics", "fulfillment", "shipping", "物流", "履约", "发货"],
        # 注意：不要放裸词 "tiktok"，会被 "tiktok shop"（销售渠道）子串命中，导致内容平台/销售渠道误判。
        "content_pain": ["content", "ugc", "素材", "视频", "拍摄", "社媒", "instagram", "youtube", "抖音", "小红书"],
    },
}

# ============================================================
# 文本处理与信号识别
# ============================================================

def _t(text: str) -> str:
    return (text or "").lower()


def has_any(text: str, keywords: List[str]) -> bool:
    """纯ASCII字母数字的短关键词（如 wa/gmv）用边界正则匹配，避免命中 want/software 等误触发；
    中文关键词及包含空格/标点的英文短语按子串匹配即可。
    注意：不用Python原生\\b——Python的\\b把中文字符当作\\w，导致"whatsapp群"这种中英文
    紧贴的情况反而匹配不到，所以这里手写只把ASCII字母数字当"词字符"的边界判断。"""
    low = _t(text)
    for k in keywords:
        kw = k.lower()
        if re.fullmatch(r"[a-z0-9]+", kw):
            pattern = r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])"
            if re.search(pattern, low):
                return True
        elif kw in low:
            return True
    return False


def matched_keywords(text: str, keywords: List[str]) -> List[str]:
    low = _t(text)
    return [k for k in keywords if k.lower() in low]


def _scale_by_unit(num: float, unit: str) -> float:
    if unit == "k":
        return num * 1_000
    if unit == "m":
        return num * 1_000_000
    if unit == "万":
        return num * 10_000
    if unit == "亿":
        return num * 100_000_000
    return num


def extract_money_values(text: str) -> List[float]:
    """提取 $2,000 / 2000 dollars / $5k / 35万美金 / 月销售额8000 等金额，支持中文万/亿数量词。"""
    low = _t(text).replace(",", "")
    values: List[float] = []
    for m in re.finditer(r"\$\s*(\d+(?:\.\d+)?)\s*(k|m|万|亿)?", low):
        values.append(_scale_by_unit(float(m.group(1)), m.group(2) or ""))
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(k|m|万|亿)?\s*(?:usd|dollars|dollar|美金|美元)", low):
        values.append(_scale_by_unit(float(m.group(1)), m.group(2) or ""))
    # GMV / 月销 / 客单价等中文表述，允许没有显式货币单位（如"月销售额35万"）
    for m in re.finditer(r"(?:gmv|月销售额|月销|销售额|营业额|客单价|aov)\s*[:：]?\s*\$?\s*(\d+(?:\.\d+)?)\s*(k|m|万|亿)?", low):
        values.append(_scale_by_unit(float(m.group(1)), m.group(2) or ""))
    return values


def max_money(text: str) -> float:
    vals = extract_money_values(text)
    return max(vals) if vals else 0


def extract_percent_values(text: str) -> List[float]:
    vals = []
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*%", text or ""):
        try:
            vals.append(float(m.group(1)))
        except ValueError:
            pass
    return vals


def extract_followers(text: str) -> float:
    low = _t(text).replace(",", "")
    max_followers = 0.0
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(k|m|万|亿)?\s*(?:followers|fans|粉丝)",
        r"(?:followers|fans|粉丝)\s*(\d+(?:\.\d+)?)\s*(k|m|万|亿)?",
    ]
    for pat in patterns:
        for m in re.finditer(pat, low):
            num = _scale_by_unit(float(m.group(1)), m.group(2) or "")
            max_followers = max(max_followers, num)
    return max_followers


def extract_order_count(text: str) -> float:
    low = _t(text).replace(",", "")
    max_orders = 0.0
    for pat in [r"(\d+)\s*(orders|订单)", r"月\s*(\d+)\s*(单|订单)"]:
        for m in re.finditer(pat, low):
            max_orders = max(max_orders, float(m.group(1)))
    return max_orders


def detect_client_type(text: str) -> str:
    low = _t(text)
    # 明确规则：先看是否有具体电商店铺/GMV证据（现有卖家），避免"自有工厂供应链"这类
    # 供应链侧描述被"工厂"关键词误判为工厂B2B；工厂B2B需要更明确的B2B/批发/OEM证据。
    if has_any(low, ["shopify", "amazon", "亚马逊", "tiktok shop", "etsy", "depop", "whatnot", "store", "店铺", "独立站", "月销售额", "月销", "订单", "gmv", "上架"]):
        return "现有卖家"
    if has_any(low, ["factory", "manufacturer", "oem", "odm", "b2b", "询盘", "代工", "贴牌", "工厂直营", "出口工厂"]) or (
        has_any(low, ["工厂", "厂家"]) and has_any(low, ["批发", "wholesale", "对外", "出口", "代工"])
    ):
        return "工厂B2B"
    if has_any(low, ["distributor", "reseller", "代理", "分销商", "渠道商", "批发商", "批发"]):
        return "分销商"
    if has_any(low, ["creator", "influencer", "kol", "koc", "粉丝", "followers", "content creator", "博主", "达人", "网红"]):
        return "创作者"
    if has_any(low, ["new", "beginner", "新手", "刚开始", "idea", "想法", "还没开始"]):
        return "新手"
    return "待确认"


def detect_compliance(text: str, override: str = "Auto") -> Tuple[str, str]:
    if override != "Auto":
        mapping = {
            "Green normal": "合规",
            "Gray needs approval": "灰色",
            "Red not allowed": "红线",
        }
        label = mapping.get(override, "合规")
        action = next((v["action"] for v in CONFIG["compliance"].values() if v["label"] == label), "")
        return label, f"人工选择：{label}。{action}"

    low = _t(text)
    for level in ["red", "gray", "green"]:
        cfg = CONFIG["compliance"][level]
        if has_any(low, cfg["keywords"]):
            return cfg["label"], f"系统识别到相关品类/关键词，判断为{cfg['label']}。{cfg['action']}"
    return "合规", "未识别到明显红线或灰色品类关键词，暂按合规处理；如有敏感宣称仍需人工复核。"


def detect_pain_points(text: str) -> List[str]:
    pain_map = {
        "Sourcing": CONFIG["keywords"]["sourcing_pain"],
        "Traffic / Ads": CONFIG["keywords"]["traffic_pain"],
        "Affiliate / Creator Sales": CONFIG["keywords"]["affiliate_pain"],
        "Distributor / Reseller": CONFIG["keywords"]["distributor_pain"],
        "B2B Leads": CONFIG["keywords"]["leads_pain"],
        "Store Setup": CONFIG["keywords"]["store_pain"],
        "Conversion": CONFIG["keywords"]["conversion_pain"],
        "Logistics": CONFIG["keywords"]["logistics_pain"],
        "Content / UGC": CONFIG["keywords"]["content_pain"],
    }
    pains = [name for name, kws in pain_map.items() if has_any(text, kws)]
    return pains or ["Not clear"]


def detect_page_data_foundation(text: str) -> Dict[str, bool]:
    low = _t(text)
    return {
        "站点": has_any(low, ["website", "site", "shopify", "independent store", "独立站", "网站", "店铺"]),
        "Pixel": has_any(low, ["pixel", "meta pixel", "tiktok pixel", "facebook pixel"]),
        "GA4": has_any(low, ["ga4", "google analytics", "analytics"]),
        "表单": has_any(low, ["form", "lead form", "表单", "询盘表"]),
        "WhatsApp": has_any(low, ["whatsapp", "wa"]),
        "归因": has_any(low, ["tracking", "utm", "attribution", "归因", "追踪"]),
    }


def detect_product_features(text: str) -> Dict[str, bool]:
    low = _t(text)
    return {
        "强展示": has_any(low, ["fashion", "beauty", "jewelry", "home decor", "streetwear", "accessories", "视觉", "展示", "穿搭", "美妆", "饰品", "家居"]),
        "强解释": has_any(low, ["how to", "tutorial", "complex", "education", "解释", "教程", "功能", "使用方法", "技术", "b2b", "oem"]),
        "可寄样": has_any(low, ["sample", "seeding", "寄样", "样品", "测评", "review", "unboxing", "开箱"]),
        "可标准化": has_any(low, ["sku", "standard", "标准", "现货", "ready stock", "库存", "同款"]),
        # 注意：不能只靠裸"工厂/factory"判断B2B长决策，否则"自有工厂供应链"这类现有卖家会被误判成B2B。
        "B2B长决策": has_any(low, ["b2b", "oem", "odm", "manufacturer", "wholesale", "批发", "询盘", "报价", "采购决策", "代工", "贴牌"])
        or (has_any(low, ["factory", "工厂", "厂家"]) and has_any(low, ["批发", "wholesale", "对外", "出口", "代工", "manufacturer"])),
    }


def detect_aov_ltv(text: str) -> str:
    low = _t(text)
    values = extract_money_values(text)
    if has_any(low, ["aov", "客单价"]):
        return f"已提到客单价/AOV，金额线索：{', '.join(['$'+str(int(v)) for v in values[:3]]) or '未给金额'}"
    if has_any(low, ["ltv", "复购", "repeat purchase", "retention", "留存"]):
        return "已提到LTV/复购/留存线索"
    if values:
        return f"访谈中出现金额线索：{', '.join(['$'+str(int(v)) for v in values[:3]])}，需确认是客单价、预算还是GMV"
    return "未确认"


def evidence_confidence(text: str, component_scores: Dict[str, int]) -> Tuple[str, str]:
    low = _t(text)
    evidence_hits = 0
    reasons = []
    if extract_money_values(text):
        evidence_hits += 1
        reasons.append("有金额/预算/GMV数字")
    if has_any(low, ["screenshot", "截图", "proof", "证明", "后台", "dashboard", "link", "链接"]):
        evidence_hits += 1
        reasons.append("提到截图/链接/后台证明")
    if has_any(low, ["shopify", "amazon", "tiktok shop", "etsy", "website", "独立站", "店铺"]):
        evidence_hits += 1
        reasons.append("有明确销售渠道")
    if extract_followers(text) > 0 or has_any(low, ["community", "社群", "名单", "email list", "discord", "telegram", "whatsapp group"]):
        evidence_hits += 1
        reasons.append("有私域/粉丝/社群线索")
    if has_any(low, ["product photo", "video", "素材", "产品图", "listing", "图片", "视频"]):
        evidence_hits += 1
        reasons.append("有素材或上架资料线索")

    if evidence_hits >= 4:
        return "高", "；".join(reasons)
    if evidence_hits >= 2:
        return "中", "；".join(reasons)
    return "低", "访谈中可验证信息较少，建议补Missing Info后重跑。"


def detect_signals(text: str) -> List[str]:
    """标签必须来自访谈内容。禁止无粉丝/私域时输出strong_audience。"""
    signals = []
    low = _t(text)
    if has_any(low, ["shopify", "amazon", "tiktok shop", "etsy", "depop", "whatnot", "独立站", "店铺"]):
        signals.append("有明确销售渠道")
    if max_money(text) >= 5000 or has_any(low, ["gmv", "sales", "销售额"]):
        signals.append("有GMV/销售额线索")
    if max_money(text) >= 2000 or has_any(low, ["paid ads", "广告预算", "投放", "meta ads", "google ads", "tiktok ads"]):
        signals.append("有付费营销线索")
    followers = extract_followers(text)
    er_values = extract_percent_values(text)
    if followers > 0 or has_any(low, ["私域", "社群", "customer list", "email list", "whatsapp group", "discord", "telegram"]):
        if followers >= 10000 or any(v >= 3 for v in er_values):
            signals.append("有成规模私域/粉丝线索")
        else:
            signals.append("有少量私域/粉丝线索")
    if has_any(low, ["sample", "seeding", "寄样", "样品", "review", "unboxing"]):
        signals.append("有寄样/种草线索")
    if has_any(low, ["pixel", "ga4", "tracking", "utm", "归因"]):
        signals.append("有页面追踪/数据基础线索")
    return signals

# ============================================================
# 评分：严格按参考数据
# ============================================================

def score_supply(text: str) -> Tuple[int, str]:
    low = _t(text)
    stable_kws = [
        "stable supplier", "own supplier", "own factory", "in-house factory", "factory direct",
        "自有供应链", "自有工厂", "自营工厂", "自建供应链", "工厂直营", "长期合作供应商",
        "稳定供应链", "资深电商", "自带货",
    ]
    if has_any(low, stable_kws):
        return 20, "客户有自有稳定供应链或属于资深电商自带货。"

    no_supply_kws = [
        "need sourcing", "looking for supplier", "sourcing support", "no supplier",
        "找货", "无货源", "需要供应商", "没有供应商", "没有货源", "还没有货源", "尚无货源",
    ]
    high_risk_kws = ["hard to source", "high risk", "restricted", "找不到", "风险高", "做不了", "违禁", "限制类目"]
    uncertain_kws = ["need evaluate", "uncertain", "quality risk", "不确定", "需评估", "交期"]
    workable_kws = ["easy to source", "品类可做", "容易找货", "好找货", "已有替代供应商", "有替代供应商"]

    # 先判否定/没有货源的表述，再决定给分；"无货源"本身不再默认给15分。
    if has_any(low, no_supply_kws):
        if has_any(low, high_risk_kws):
            return 0, "客户无货源且品类/供应链风险高。"
        if has_any(low, workable_kws):
            return 15, "客户无货源，但品类明确可做（有替代供应商或找货难度低）。"
        if has_any(low, uncertain_kws):
            return 10, "客户无货源，且供应链风险中等，需要进一步评估。"
        return 0, "客户目前无货源，且未提供品类可做的证据，暂按0分处理，需先确认品类可行性（待补证据）。"

    if has_any(low, high_risk_kws):
        return 0, "客户供应链/品类风险高。"
    if has_any(low, uncertain_kws):
        return 10, "客户供应链风险中等，需要进一步评估。"
    return 10, "访谈未充分说明货源稳定性，暂按中等风险处理，需要补充证据。"


def score_paid(text: str) -> Tuple[int, str]:
    low = _t(text)
    money = max_money(text)
    if money >= CONFIG["value_gate"]["high_budget_min"] or has_any(low, ["paid ads", "facebook ads", "google ads", "tiktok ads", "meta ads", "广告预算", "投过广告", "投放"]):
        return 25, "客户有明确预算≥$2,000，或有过付费广告经验。"
    if has_any(low, ["small test", "小额测试", "willing to test", "愿意测试", "try ads", "试投", "先试"]):
        return 15, "客户有兴趣，愿意先做小额测试。"
    if has_any(low, ["free only", "only free", "不投", "免费", "no budget", "没有预算", "不想花钱", "只要免费"]):
        return 0, "客户只要免费工具或明确不投营销，服务优先级封顶L2自助。"
    return 0, "访谈未提及预算或付费营销意愿，暂无证据评分，需先补充预算信息（待补证据）。"


def score_private(text: str) -> Tuple[int, str]:
    low = _t(text)
    followers = extract_followers(text)
    er_values = extract_percent_values(text)
    if (followers >= 10000 and any(v >= 3 for v in er_values)) or has_any(low, ["er 3%", "互动率3", "成规模私域", "large community", "strong community"]):
        return 15, "客户有成规模私域，且互动率达到或接近ER≥3%。"
    if followers > 0 or has_any(low, ["少量私域", "some community", "small community", "微信群", "discord", "telegram", "email list", "customer list", "社群", "私域"]):
        return 8, "客户有少量私域或社群资源。"
    if has_any(low, ["no traffic", "没有流量", "无流量", "完全没有", "no audience"]):
        return 0, "客户完全无线上流量。"
    return 0, "访谈未提及私域/粉丝相关信息，暂无证据评分，需先补充私域信息（待补证据）。"


def score_ecommerce(text: str) -> Tuple[int, str]:
    low = _t(text)
    if has_any(low, ["amazon", "亚马逊", "shopify", "tiktok shop"]):
        return 15, "客户做过Amazon/Shopify/TikTok Shop。"
    if has_any(low, ["etsy", "depop", "whatnot", "ebay", "walmart", "temu", "其他平台", "marketplace", "独立站", "自建站", "官网商城"]):
        return 8, "客户做过其他电商平台或独立站。"
    if has_any(low, ["beginner", "new to ecommerce", "新手", "没做过", "first time"]):
        return 0, "客户属于纯新手。"
    return 0, "访谈未体现明确电商/建站经验，暂按纯新手处理。"


def score_sales(text: str) -> Tuple[int, str]:
    low = _t(text)
    money = max_money(text)
    orders = extract_order_count(text)
    if has_any(low, ["gmv", "monthly sales", "月gmv", "销售额"]) and money >= 5000:
        return 15, "客户近半年或近期有稳定GMV≥$5,000线索。"
    if money >= 5000 and has_any(low, ["monthly", "每月", "month", "月"]):
        return 15, "客户提到月度金额≥$5,000，按稳定销售线索处理。"
    if orders > 0 or has_any(low, ["few orders", "test orders", "少量订单", "偶发销售", "some sales"]):
        return 8, "客户有少量或偶发销售。"
    if detect_client_type(text) == "创作者":
        return 7, "客户像纯网红/创作者转电商，原渠道销售表现暂按不适用中性处理。"
    if has_any(low, ["no sales", "没有销售", "没卖过", "0 sales", "无销售"]):
        return 0, "客户没有销售记录。"
    return 7, "访谈未明确销售记录，暂按中性处理。"


def score_materials(text: str) -> Tuple[int, str]:
    low = _t(text)
    has_photo = has_any(low, ["photo", "image", "产品图", "图片"])
    has_video = has_any(low, ["video", "视频", "ugc", "素材"])
    has_listing = has_any(low, ["listing", "selling point", "卖点", "description", "标题", "价格表"])
    if (has_photo and has_video) or (has_photo and has_listing) or has_any(low, ["materials ready", "素材齐全", "图文视频齐全"]):
        return 10, "客户产品图和素材较完整。"
    if has_photo or has_video or has_listing:
        return 5, "客户有部分素材，但还不完整。"
    return 0, "客户几乎没有可直接用于上架或营销的素材。"


def calculate_scores(text: str) -> Tuple[Dict[str, int], Dict[str, str], Dict[str, Dict[str, Any]]]:
    scorers = {
        "supply_stability": score_supply,
        "paid_marketing_willingness": score_paid,
        "private_traffic": score_private,
        "ecommerce_foundation": score_ecommerce,
        "existing_sales": score_sales,
        "materials_readiness": score_materials,
    }
    scores: Dict[str, int] = {}
    reasons: Dict[str, str] = {}
    for key, fn in scorers.items():
        score, reason = fn(text)
        scores[key] = score
        reasons[key] = reason

    axes: Dict[str, Dict[str, Any]] = {}
    for axis_key, cfg in CONFIG["axis"].items():
        axis_score = sum(scores[c] for c in cfg["components"])
        max_score = cfg["max"]
        pct = round(axis_score / max_score * 100, 1) if max_score else 0
        status = CONFIG["readiness_labels"]["need_evidence"]
        status_reason = "需要补充证据后再确认。"
        if cfg.get("paid_zero_force_not_ready") and scores.get("paid_marketing_willingness", 0) == 0:
            status = CONFIG["readiness_labels"]["not_ready"]
            status_reason = "付费营销意愿为0，营销服务不Ready。"
        elif axis_score >= cfg["ready_min"]:
            status = CONFIG["readiness_labels"]["ready"]
            status_reason = "该轴关键条件已基本具备。"
        elif axis_score <= cfg["not_ready_max"]:
            status = CONFIG["readiness_labels"]["not_ready"]
            status_reason = "该轴核心条件不足。"
        axes[axis_key] = {
            "label": cfg["label"],
            "score": axis_score,
            "max": max_score,
            "pct": pct,
            "status": status,
            "reason": status_reason,
            "components": {c: scores[c] for c in cfg["components"]},
        }
    return scores, reasons, axes

# ============================================================
# 服务组合、营销子类型、优先级
# ============================================================

def readiness_not_ready_count(axes: Dict[str, Dict[str, Any]]) -> int:
    return sum(1 for a in axes.values() if a["status"] == "Not Ready")


def determine_marketing_subtypes(text: str, compliance: str, scores: Dict[str, int]) -> Tuple[List[str], List[str]]:
    low = _t(text)
    pains = detect_pain_points(text)
    features = detect_product_features(text)
    page_data = detect_page_data_foundation(text)
    subtypes: List[str] = []
    reasons: List[str] = []

    if compliance == "红线":
        return [], ["红线品类不进入营销服务判断。"]

    # AI矩阵号：真正的冷启动（私域弱 且 原渠道销售也弱），不能只因私域为0/中性就默认冷启动
    cold_start = scores.get("private_traffic", 0) in [0, 7] and scores.get("existing_sales", 0) <= 7
    if ("Traffic / Ads" in pains or "Content / UGC" in pains or cold_start) and scores.get("paid_marketing_willingness", 0) > 0:
        subtypes.append("AI社媒矩阵号")
        reasons.append("客户存在冷启动、内容蓄水或流量基础不足的问题。")

    # CPS：强展示、可寄样、达人/佣金/内容带货
    if (features["强展示"] or features["可寄样"]) and ("Affiliate / Creator Sales" in pains or has_any(low, ["commission", "佣金", "creator", "kol", "koc", "网红", "带货"])):
        subtypes.append("CPS网红营销")
        reasons.append("产品具备展示/寄样条件，且客户有达人带货或佣金诉求。")

    # CPL分销员：渠道私域/分销驱动
    if "Distributor / Reseller" in pains or has_any(low, ["分销员", "代理", "reseller", "distributor", "渠道", "私域分销"]):
        subtypes.append("CPL分销员")
        reasons.append("客户诉求偏渠道型/私域型分销。")

    # CPL Leads：B2B/OEM/工厂/批发/长决策链
    if "B2B Leads" in pains or features["B2B长决策"]:
        subtypes.append("CPL Leads")
        reasons.append("客户更像B2B、批发、OEM或高客单询盘型需求。")

    # CPC：页面+数据基础+预算ready，快速测品放量
    page_ready = page_data["站点"] and (page_data["Pixel"] or page_data["GA4"] or page_data["归因"])
    if page_ready and scores.get("paid_marketing_willingness", 0) == 25:
        subtypes.append("CPC投放")
        reasons.append("客户页面和追踪基础较完整，并且预算或投放经验明确。")

    # 灰色只能CPL，CPC/CPS待审批
    if compliance == "灰色":
        allowed = [s for s in subtypes if s in ["CPL分销员", "CPL Leads"]]
        if not allowed:
            allowed = ["CPL Leads"] if features["B2B长决策"] else ["CPL分销员"]
        return allowed, ["灰色品类默认只能走CPL；CPC/CPS需审批后再判断。"]

    # 去重保序
    unique = []
    for s in subtypes:
        if s not in unique:
            unique.append(s)
    return unique, reasons or ["访谈中营销诉求不够明确，建议先补问预算、页面基础和获客目标。"]


def determine_service_combo(text: str, axes: Dict[str, Dict[str, Any]], evidence: str, compliance: str, scores: Dict[str, int]) -> Dict[str, Any]:
    if compliance == "红线":
        return {
            "combo": ["合规否决"],
            "main": "合规否决",
            "aux": "不进入付款、广告或sourcing流程",
            "rhythm": "待培育",
            "reason": "该客户/商品命中红线合规风险，需先停止推进。",
        }

    axis_status = {k: v["status"] for k, v in axes.items()}
    not_ready = [k for k, s in axis_status.items() if s == "Not Ready"]
    ready = [k for k, s in axis_status.items() if s == "Ready"]
    need_evidence = [k for k, s in axis_status.items() if s == "待补证据"]

    service_map = {"Sourcing": "Sourcing", "Marketing": "营销", "Build": "建站自助"}
    axis_cn = {"Sourcing": "货源稳定性", "Marketing": "营销", "Build": "建站/素材"}

    if len(ready) == 3:
        return {
            "combo": ["Sourcing", "建站自助", "营销"],
            "main": "全链路服务",
            "aux": "按里程碑分阶段推进：先确认商品与合规，再建站上架，最后进入营销测试。",
            "rhythm": "长周期",
            "reason": "三轴均Ready，适合做sourcing、建站和营销联动，但应按阶段推进。",
        }

    if len(not_ready) == 1 and len(ready) >= 2:
        missing_axis = not_ready[0]
        combo = [service_map[x] for x in ready] + [f"精准补齐{axis_cn[missing_axis]}"]
        return {
            "combo": combo,
            "main": f"精准补齐{axis_cn[missing_axis]}",
            "aux": f"其余已就绪项：{ '、'.join(service_map[x] for x in ready) }。",
            "rhythm": "快转化" if scores.get("paid_marketing_willingness", 0) > 0 else "待培育",
            "reason": f"只有{axis_cn[missing_axis]}为Not Ready，其余关键条件已具备，应精准补短板。",
        }

    if len(not_ready) >= 2 and evidence == "低":
        return {
            "combo": ["Nurture"],
            "main": "待培育",
            "aux": "先补基础信息和证据，不进入重投入流程。",
            "rhythm": "待培育",
            "reason": "两轴以上Not Ready且证据不足，当前不适合进入正式服务流程。",
        }

    combo = [service_map[x] for x in ready]
    if need_evidence:
        combo.append("补证据后重跑")
    if not_ready:
        combo.extend([f"补齐{axis_cn[x]}" for x in not_ready])
    if not combo:
        combo = ["Nurture"]
    return {
        "combo": combo,
        "main": "先补证据再推进" if need_evidence else "轻量验证",
        "aux": "高就绪但低置信时，不直接降级；先补Missing Info后重跑。",
        "rhythm": "待培育" if len(not_ready) >= 2 else "快转化",
        "reason": "客户存在部分Ready和部分待确认项，建议先补关键信息后再分配资源。",
    }


def determine_value_and_priority(scores: Dict[str, int], axes: Dict[str, Dict[str, Any]], service: Dict[str, Any], evidence: str) -> Tuple[str, str, str]:
    paid = scores.get("paid_marketing_willingness", 0)
    if paid == 0:
        return "低", "待培育", "付费意愿为0，优先级封顶L2自助，不因其他轴齐备而进入高优先级。"
    if service["main"] == "全链路服务":
        value = "高" if paid == 25 else "中"
        return value, "长周期", "三轴均Ready，属于长周期客户，应按里程碑推进，不因周期长被误杀。"
    if paid == 25:
        return "高", service.get("rhythm", "快转化"), "付费意愿高或预算≥$2,000，整体优先级上抬一档。"
    if evidence == "低":
        return "中", "待培育", "客户有一定意向但证据不足，先补证据后再确认节奏。"
    return "中", service.get("rhythm", "快转化"), "客户具备一定服务价值，可按当前主方案推进。"

# ============================================================
# 动作、Missing Info、AM Checklist
# ============================================================

def missing_info(text: str, axes: Dict[str, Dict[str, Any]], service: Dict[str, Any], marketing_subtypes: List[str]) -> Tuple[List[str], List[str]]:
    low = _t(text)
    needed = []
    not_applicable = []
    combo_text = " ".join(service.get("combo", []))

    if "Sourcing" in combo_text or "货源" in combo_text:
        checks = [
            ("目标采购价/目标零售价", ["target price", "采购价", "零售价", "retail price"]),
            ("可接受MOQ和首单预算", ["moq", "起订量", "首单预算"]),
            ("是否现货、轻定制或全定制", ["custom", "定制", "logo", "packaging", "现货"]),
            ("参考链接/图片/样品", ["reference", "链接", "图片", "sample", "样品"]),
        ]
        for item, kws in checks:
            if not has_any(low, kws):
                needed.append(item)
    else:
        not_applicable.append("当前主方案不涉及深度sourcing，暂不需要MOQ/打样细节。")

    if "建站" in combo_text:
        checks = [
            ("产品图、视频、卖点、价格表", ["产品图", "video", "素材", "卖点", "price list"]),
            ("站点/域名/收款方式是否已有", ["website", "domain", "stripe", "站点", "域名", "收款"]),
        ]
        for item, kws in checks:
            if not has_any(low, kws):
                needed.append(item)
    else:
        not_applicable.append("当前主方案不以建站为核心，可暂不补完整上架素材。")

    if "营销" in combo_text or marketing_subtypes:
        if "CPC投放" in marketing_subtypes:
            checks = [
                ("广告预算和见效预期", ["budget", "预算", "roas", "cpa"]),
                ("Pixel/GA4/UTM/归因是否ready", ["pixel", "ga4", "utm", "tracking", "归因"]),
                ("落地页/商品页是否ready", ["landing page", "product page", "页面", "website"]),
            ]
            for item, kws in checks:
                if not has_any(low, kws):
                    needed.append(item)
        if "CPS网红营销" in marketing_subtypes:
            checks = [
                ("可寄样数量和样品成本", ["sample", "寄样", "样品"]),
                ("佣金比例/毛利空间", ["commission", "佣金", "margin", "毛利"]),
                ("达人内容要求和禁忌", ["creator brief", "内容要求", "禁忌"]),
            ]
            for item, kws in checks:
                if not has_any(low, kws):
                    needed.append(item)
        if "CPL分销员" in marketing_subtypes:
            checks = [
                ("目标分销员画像", ["distributor", "reseller", "分销员", "代理"]),
                ("分销佣金/价格体系", ["commission", "佣金", "price tier", "价格体系"]),
            ]
            for item, kws in checks:
                if not has_any(low, kws):
                    needed.append(item)
        if "CPL Leads" in marketing_subtypes:
            checks = [
                ("Lead跟进SOP和24小时负责人", ["24h", "follow up", "跟单", "负责人"]),
                ("询盘表单字段和报价模板", ["lead form", "表单", "报价模板", "quote template"]),
                ("客单价/LTV或批发MOQ", ["aov", "ltv", "客单价", "moq", "批发"]),
            ]
            for item, kws in checks:
                if not has_any(low, kws):
                    needed.append(item)
        if "AI社媒矩阵号" in marketing_subtypes:
            checks = [
                ("3-5个核心卖点和内容方向", ["selling point", "卖点", "content angle", "内容方向"]),
                ("可持续输出素材的来源", ["素材", "video", "图片", "ugc"]),
            ]
            for item, kws in checks:
                if not has_any(low, kws):
                    needed.append(item)
    else:
        not_applicable.append("当前主方案不涉及营销测试，可暂不补Pixel/达人/广告预算细节。")

    # 去重
    needed_unique = []
    for item in needed:
        if item not in needed_unique:
            needed_unique.append(item)
    not_app_unique = []
    for item in not_applicable:
        if item not in not_app_unique:
            not_app_unique.append(item)
    return needed_unique, not_app_unique


def next_actions_by_pain(text: str, service: Dict[str, Any], marketing_subtypes: List[str]) -> List[Dict[str, str]]:
    pains = detect_pain_points(text)
    combo_text = " ".join(service.get("combo", []))
    rows: List[Dict[str, str]] = []

    templates = {
        "Sourcing": {
            "内部动作": "先让BD确认目标价、MOQ、定制范围和可接受交期；Sourcing只做轻量初筛，不先深度开发。",
            "对客户说的动作": "我们先把商品需求确认清楚，包括目标价格、MOQ、是否定制和参考款式，再判断能否进入报价或样品阶段。",
        },
        "Traffic / Ads": {
            "内部动作": "先检查页面、Pixel/GA4、预算和素材是否ready，再判断用CPC还是AI社媒矩阵号冷启动。",
            "对客户说的动作": "如果目标是拉新或放量，我们需要先确认页面和追踪是否准备好，再决定是先做内容蓄水还是直接投放测试。",
        },
        "Affiliate / Creator Sales": {
            "内部动作": "确认产品是否可寄样、佣金空间、达人brief和履约能力，再判断CPS网红营销是否可做。",
            "对客户说的动作": "如果想让达人帮你卖货，我们需要先确认样品、佣金比例和产品卖点，这样才能匹配合适的创作者。",
        },
        "Distributor / Reseller": {
            "内部动作": "明确目标分销员画像、价格体系和佣金规则，优先走CPL分销员而不是普通广告。",
            "对客户说的动作": "如果你想找分销员或代理，我们会先帮你把目标人群、佣金和价格体系确认清楚，再设计获客表单。",
        },
        "B2B Leads": {
            "内部动作": "确认Lead表单字段、报价模板、客单价/LTV和24小时跟单负责人，优先走CPL Leads。",
            "对客户说的动作": "如果你的客户决策链比较长，我们建议先用询盘型线索收集，再用固定模板快速跟进报价。",
        },
        "Store Setup": {
            "内部动作": "检查产品图、视频、卖点、价格、库存和收款方式；先做能上线的最小店铺版本。",
            "对客户说的动作": "我们可以先帮你确认上架需要的素材和价格信息，优先把基础店铺跑通，再接后续营销。",
        },
        "Conversion": {
            "内部动作": "先看商品页、价格、信任背书和转化路径，不直接加大投放。",
            "对客户说的动作": "如果目前有流量但转化不理想，我们建议先优化页面、卖点和购买路径，再考虑加预算。",
        },
        "Content / UGC": {
            "内部动作": "先整理3-5个内容角度和素材来源，适合AI社媒矩阵号或KOL/KOC种草。",
            "对客户说的动作": "我们可以先从内容角度切入，把产品卖点转成短视频/社媒内容，再看是否进入达人或投放测试。",
        },
        "Not clear": {
            "内部动作": "先不要分配重资源；用closing questions补齐客户品类、渠道、预算、供应链和推广目标。",
            "对客户说的动作": "我先帮你把当前情况整理一下，再确认几个关键点，这样后续才能匹配到最合适的支持方式。",
        },
    }

    for p in pains:
        tpl = templates.get(p)
        if tpl:
            rows.append({"Pain Point": p, **tpl})

    # 如果服务组合命中了但pain没有识别，补服务导向动作
    if "Sourcing" in combo_text and all(r["Pain Point"] != "Sourcing" for r in rows):
        rows.append({"Pain Point": "Sourcing", **templates["Sourcing"]})
    if "建站" in combo_text and all(r["Pain Point"] != "Store Setup" for r in rows):
        rows.append({"Pain Point": "Store Setup", **templates["Store Setup"]})
    if "营销" in combo_text and all(r["Pain Point"] not in ["Traffic / Ads", "Affiliate / Creator Sales", "Distributor / Reseller", "B2B Leads", "Content / UGC"] for r in rows):
        if marketing_subtypes:
            subtype = marketing_subtypes[0]
            p = {
                "AI社媒矩阵号": "Content / UGC",
                "CPS网红营销": "Affiliate / Creator Sales",
                "CPL分销员": "Distributor / Reseller",
                "CPL Leads": "B2B Leads",
                "CPC投放": "Traffic / Ads",
            }.get(subtype, "Traffic / Ads")
            rows.append({"Pain Point": p, **templates[p]})
    return rows


def build_am_checklist(service: Dict[str, Any], marketing_subtypes: List[str]) -> List[Dict[str, str]]:
    combo = service.get("combo", [])
    tasks: List[Dict[str, str]] = []
    if any("Sourcing" in c or "货源" in c for c in combo):
        tasks.extend([
            {"服务": "Sourcing", "阶段": "需求确认", "任务": "确认品类、目标价、MOQ、定制范围、交期", "状态": "待跟进"},
            {"服务": "Sourcing", "阶段": "合规初筛", "任务": "确认是否红线/灰色/合规", "状态": "待跟进"},
            {"服务": "Sourcing", "阶段": "供应商初筛", "任务": "轻量匹配2-3个可行供应商或替代款", "状态": "待跟进"},
            {"服务": "Sourcing", "阶段": "报价/MOQ", "任务": "输出报价区间、MOQ、样品/定制成本", "状态": "待跟进"},
        ])
    if any("建站" in c for c in combo):
        tasks.extend([
            {"服务": "建站自助", "阶段": "素材收集", "任务": "收集产品图、视频、卖点、价格、库存", "状态": "待跟进"},
            {"服务": "建站自助", "阶段": "页面准备", "任务": "确认商品页结构、FAQ、信任背书", "状态": "待跟进"},
            {"服务": "建站自助", "阶段": "收款/数据", "任务": "确认Stripe/收款、Pixel/GA4/表单/WhatsApp", "状态": "待跟进"},
            {"服务": "建站自助", "阶段": "上线检查", "任务": "完成上架、下单路径和归因检查", "状态": "待跟进"},
        ])
    if any("营销" in c for c in combo) or marketing_subtypes:
        for subtype in marketing_subtypes or ["营销待定"]:
            if subtype == "AI社媒矩阵号":
                tasks.append({"服务": subtype, "阶段": "内容方向", "任务": "确认3-5个核心卖点、内容角度和素材来源", "状态": "待跟进"})
            elif subtype == "CPS网红营销":
                tasks.append({"服务": subtype, "阶段": "达人带货准备", "任务": "确认样品、佣金、达人brief、履约能力", "状态": "待跟进"})
            elif subtype == "CPL分销员":
                tasks.append({"服务": subtype, "阶段": "分销招募", "任务": "确认分销员画像、佣金、价格体系和申请表单", "状态": "待跟进"})
            elif subtype == "CPL Leads":
                tasks.append({"服务": subtype, "阶段": "Lead承接", "任务": "确认表单字段、报价模板和24小时跟单负责人", "状态": "待跟进"})
            elif subtype == "CPC投放":
                tasks.append({"服务": subtype, "阶段": "投放检查", "任务": "确认页面、Pixel/GA4/UTM、预算和素材", "状态": "待跟进"})
            else:
                tasks.append({"服务": "营销", "阶段": "渠道确认", "任务": "确认适合AI矩阵号/CPS/CPL/CPC中的哪一种", "状态": "待跟进"})
    if not tasks:
        tasks.append({"服务": "Nurture", "阶段": "基础信息", "任务": "补齐客户品类、渠道、预算、销售记录和需求", "状态": "待跟进"})
    return tasks


def make_client_profile(text: str, scores: Dict[str, int], axes: Dict[str, Dict[str, Any]], service: Dict[str, Any], marketing_subtypes: List[str], compliance: str, evidence: str) -> Dict[str, str]:
    page_data = detect_page_data_foundation(text)
    features = detect_product_features(text)
    page_summary = " / ".join([f"{k}:{'Ready' if v else '未确认'}" for k, v in page_data.items()])
    feature_summary = " / ".join([k for k, v in features.items() if v]) or "未确认"
    return {
        "客户类型": detect_client_type(text),
        "主要痛点": "、".join(detect_pain_points(text)),
        "客单价/LTV": detect_aov_ltv(text),
        "页面与数据基础": page_summary,
        "产品特征": feature_summary,
        "Sourcing就绪度": axes["Sourcing"]["status"],
        "营销就绪度": axes["Marketing"]["status"],
        "建站就绪度": axes["Build"]["status"],
        "服务组合": "、".join(service["combo"]),
        "营销子类型": "、".join(marketing_subtypes) if marketing_subtypes else "不适用/待确认",
        "合规档": compliance,
        "证据置信度": evidence,
    }


def build_reason(compliance_reason: str, service_reason: str, value_reason: str, evidence_reason: str) -> str:
    return f"{service_reason} {value_reason} 证据判断：{evidence_reason} 合规判断：{compliance_reason}"


def build_export_row(client_code: str, profile: Dict[str, str], pain_points: List[str], service: Dict[str, Any], marketing_subtypes: List[str], compliance: str, value_tier: str, rhythm: str, evidence: str, reason: str, checklist_summary: str, status: str) -> Dict[str, str]:
    row = {
        "客户编号": client_code or f"未命名-{datetime.now().strftime('%Y%m%d%H%M')}",
        "ClientType": profile.get("客户类型", "待确认"),
        "PainPoint": "、".join(pain_points),
        "Sourcing就绪度": profile.get("Sourcing就绪度", ""),
        "营销就绪度": profile.get("营销就绪度", ""),
        "建站就绪度": profile.get("建站就绪度", ""),
        "服务组合": profile.get("服务组合", ""),
        "主方案": service.get("main", ""),
        "营销子类型": "、".join(marketing_subtypes) if marketing_subtypes else "",
        "合规档": compliance,
        "价值档": value_tier,
        "节奏": rhythm,
        "证据置信度": evidence,
        "SystemRoute": service.get("main", ""),
        "归因说明": reason,
        "AM阶段状态": checklist_summary,
        "Status": status,
    }
    return {field: row.get(field, "") for field in CONFIG["lark_fields"]}


def csv_bytes(row: Dict[str, str]) -> bytes:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CONFIG["lark_fields"])
    writer.writeheader()
    writer.writerow(row)
    return output.getvalue().encode("utf-8-sig")

# ============================================================
# Streamlit UI
# ============================================================

st.set_page_config(page_title="Client Profile & Route Recommender", page_icon="🧭", layout="wide")

st.title("🧭 Client Profile & Route Recommender")
st.caption("三轴就绪度 + 服务组合建议 + AM跟进Checklist｜面向电商卖家/品牌/分销/创作者客户")

with st.expander("适用范围说明｜请先看", expanded=True):
    st.info(
        "本工具主要适用于电商卖家、品牌方、分销商、创作者/KOL/KOC、独立站或平台卖家等客户画像分析。"
        "如果访谈内容与商品、销售渠道、流量、GMV、供应链、分销、达人推广等无关，系统结果可能不适合直接使用。"
    )

entry = st.radio(
    "请选择你现在要做什么：",
    ["1｜Analyze Interview：我有访谈/聊天记录", "2｜Quick Assessment：我没有完整记录，只想快速判断", "3｜Benchmark：查看评分口径"],
    horizontal=True,
)

COMPLIANCE_HELP = "Auto=系统自动判断；Green=常规可推进；Gray=需审批且默认只走CPL；Red=红线，不能进入付款/广告/sourcing流程。"


def render_analysis(text: str, client_code: str = "", source_label: str = "正式评估"):
    if not text.strip():
        st.warning("请先输入客户访谈内容或快速评估信息。")
        return

    if not has_any(text, CONFIG["keywords"]["ecommerce"]):
        st.warning("系统没有识别到明显的电商/分销业务信号，本次分析置信度较低。请确认该客户是否属于电商卖家、品牌方、创作者或分销相关客户；如果不是，请不要直接使用系统生成的话术。")

    compliance_override = st.session_state.get(f"compliance_override_{source_label}", "Auto")
    compliance, compliance_reason = detect_compliance(text, compliance_override)
    scores, score_reasons, axes = calculate_scores(text)
    evidence, evidence_reason = evidence_confidence(text, scores)
    service = determine_service_combo(text, axes, evidence, compliance, scores)
    marketing_subtypes, marketing_reasons = determine_marketing_subtypes(text, compliance, scores)
    value_tier, rhythm, value_reason = determine_value_and_priority(scores, axes, service, evidence)
    profile = make_client_profile(text, scores, axes, service, marketing_subtypes, compliance, evidence)
    reason = build_reason(compliance_reason, service["reason"], value_reason, evidence_reason)
    pains = detect_pain_points(text)
    signals = detect_signals(text)
    needed, not_app = missing_info(text, axes, service, marketing_subtypes)
    actions = next_actions_by_pain(text, service, marketing_subtypes)
    tasks = build_am_checklist(service, marketing_subtypes)

    st.subheader("客户画像 Client Profile")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("客户类型", profile["客户类型"])
    c2.metric("合规档", compliance)
    c3.metric("价值档", value_tier)
    c4.metric("节奏", rhythm)

    st.markdown("#### 三轴独立就绪度")
    a1, a2, a3 = st.columns(3)
    a1.metric("Sourcing轴", f"{axes['Sourcing']['status']}", f"{axes['Sourcing']['score']}/{axes['Sourcing']['max']}")
    a2.metric("Marketing轴", f"{axes['Marketing']['status']}", f"{axes['Marketing']['score']}/{axes['Marketing']['max']}")
    a3.metric("建站自助轴", f"{axes['Build']['status']}", f"{axes['Build']['score']}/{axes['Build']['max']}")

    if evidence == "低" and any(a["status"] == "Ready" for a in axes.values()):
        st.warning("存在高就绪但低置信的情况：请先补齐Missing Info后重跑，不要直接降级为Nurture。")

    st.markdown("#### 服务组合建议")
    st.success(f"服务组合：{profile['服务组合']}")
    st.write(f"**主方案：** {service['main']}")
    st.write(f"**辅助方案：** {service['aux']}")
    st.write(f"**营销子类型：** {profile['营销子类型']}")
    if marketing_reasons:
        st.caption("营销判断依据：" + "；".join(marketing_reasons))

    st.markdown("#### Human Final Review 前的归因说明")
    st.info(reason)

    with st.expander("查看Detected signals和评分依据", expanded=False):
        st.write("**Detected signals（只显示访谈中真实命中的信号）：**")
        st.write("、".join(signals) if signals else "暂未识别到足够明确的业务信号。")
        st.write("**分项评分：**")
        for key, score in scores.items():
            label = key
            st.write(f"- {label}: {score}｜{score_reasons[key]}")
        st.caption("Ready/待补证据/Not Ready按CONFIG中的每轴阈值判断；证据置信度与就绪度分开处理。")

    st.markdown("---")
    st.subheader("What should we do next?")
    st.caption("按客户pain point分别给内部动作和对客户说的动作。")
    for row in actions:
        with st.container(border=True):
            st.markdown(f"**Pain Point：{row['Pain Point']}**")
            col_i, col_c = st.columns(2)
            col_i.markdown("**内部动作**")
            col_i.write(row["内部动作"])
            col_c.markdown("**对客户说的动作**")
            col_c.write(row["对客户说的动作"])

    st.markdown("---")
    st.subheader("Missing Info 动态补问")
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**需补问**")
        if needed:
            for item in needed:
                st.write(f"- {item}")
        else:
            st.write("当前路线下没有明显必补项。")
    with m2:
        st.markdown("**对该客户暂不适用**")
        if not_app:
            for item in not_app:
                st.write(f"- {item}")
        else:
            st.write("暂无。")

    with st.expander("根据需补问生成的closing questions", expanded=True):
        if needed:
            for item in needed[:6]:
                st.write(f"- 为了帮你匹配更准确的资源，可以再确认一下：{item}吗？")
        else:
            st.write("信息基本够用，可以进入下一步人工确认。")

    st.markdown("---")
    st.subheader("AM跟进Checklist")
    st.caption("根据命中的服务动态生成，AM可更新阶段状态。")
    status_options = ["待跟进", "进行中", "已完成"]
    checklist_status = []
    for idx, task in enumerate(tasks):
        cols = st.columns([1.2, 1.2, 4, 1.2])
        cols[0].write(task["服务"])
        cols[1].write(task["阶段"])
        cols[2].write(task["任务"])
        status = cols[3].selectbox("状态", status_options, index=status_options.index(task["状态"]), key=f"task_status_{source_label}_{idx}", label_visibility="collapsed")
        checklist_status.append(f"{task['服务']}-{task['阶段']}:{status}")
    checklist_summary = "；".join(checklist_status)

    st.markdown("---")
    st.subheader("人工确认 / Override")
    agree = st.radio("你是否同意系统建议？", ["Agree", "Partially agree", "Disagree"], horizontal=True, key=f"agree_{source_label}")
    default_services = service["combo"]
    all_services = ["Sourcing", "建站自助", "营销", "精准补齐货源稳定性", "精准补齐营销", "精准补齐建站/素材", "补证据后重跑", "Nurture", "合规否决"]
    if agree == "Disagree":
        st.warning("你已选择不同意系统推荐，请重新选择最终服务组合，并填写原因。")
        default_final = []
    elif agree == "Partially agree":
        st.warning("你选择部分同意，请确认最终服务组合是否需要调整。导出以Human Final Route为准。")
        default_final = [s for s in default_services if s in all_services]
    else:
        default_final = [s for s in default_services if s in all_services]

    final_combo = st.multiselect("Human Final Route / 最终服务组合", all_services, default=default_final, key=f"final_combo_{source_label}")
    override_reason = st.text_area("人工调整原因（如无调整可写：同意系统建议）", value="同意系统建议" if agree == "Agree" else "", key=f"override_reason_{source_label}")
    export_status = "已确认" if agree == "Agree" else "人工调整"

    if agree == "Disagree" and not final_combo:
        st.error("选择Disagree后必须重新选择Human Final Route，否则不能导出。")
        can_export = False
    else:
        can_export = True

    st.markdown("#### CRM Note 可复制摘要")
    crm_note = (
        f"客户类型：{profile['客户类型']}。主要痛点：{profile['主要痛点']}。"
        f"三轴就绪度：Sourcing={axes['Sourcing']['status']}，营销={axes['Marketing']['status']}，建站={axes['Build']['status']}。"
        f"建议服务组合：{profile['服务组合']}；主方案：{service['main']}；营销子类型：{profile['营销子类型']}。"
        f"证据置信度：{evidence}。需补问：{'、'.join(needed) if needed else '暂无明显必补项'}。"
        f"人工确认：{agree}；最终路线：{'、'.join(final_combo) if final_combo else '未确认'}。"
    )
    st.text_area("CRM Note", value=crm_note, height=140)

    final_service_for_export = service.copy()
    if final_combo:
        final_service_for_export["combo"] = final_combo
        final_service_for_export["main"] = " + ".join(final_combo)
    export_row = build_export_row(
        client_code=client_code,
        profile=profile,
        pain_points=pains,
        service=final_service_for_export,
        marketing_subtypes=marketing_subtypes,
        compliance=compliance,
        value_tier=value_tier,
        rhythm=rhythm,
        evidence=evidence,
        reason=reason + (f" 人工说明：{override_reason}" if override_reason else ""),
        checklist_summary=checklist_summary,
        status=export_status,
    )

    if can_export:
        st.download_button(
            "下载CSV（可导入Lark多维表格）",
            data=csv_bytes(export_row),
            file_name=f"client_route_{client_code or datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
    else:
        st.button("下载CSV（需先完成Human Final Route）", disabled=True)


if entry.startswith("1"):
    st.header("1｜Analyze Interview")
    st.caption("已经有客户访谈、聊天记录或会议纪要时使用。系统会生成客户画像、三轴就绪度、服务组合、内部动作、客户follow-up和AM checklist。")
    client_code = st.text_input("客户编号", placeholder="例如：20260706-001")
    st.selectbox("Compliance Override", ["Auto", "Green normal", "Gray needs approval", "Red not allowed"], key="compliance_override_analyze", help=COMPLIANCE_HELP)
    st.caption("默认建议使用Auto；只有当你确认系统误判，或你掌握额外合规信息时，才需要手动调整。")
    text = st.text_area("粘贴客户访谈内容 / call notes / WhatsApp记录", height=260, placeholder="请粘贴客户访谈内容。内容越包含品类、销售渠道、GMV、预算、货源、页面基础和营销目标，判断越准确。")
    if st.button("开始分析", type="primary"):
        st.session_state["analysis_text"] = text
        st.session_state["analysis_client_code"] = client_code
    if st.session_state.get("analysis_text"):
        render_analysis(st.session_state["analysis_text"], st.session_state.get("analysis_client_code", ""), "analyze")

elif entry.startswith("2"):
    st.header("2｜Quick Assessment")
    st.caption("没有完整访谈内容时使用。用几个关键字段拼成结构化记录后进入同一套判断逻辑。")
    with st.form("quick_form"):
        client_code = st.text_input("客户编号", placeholder="例如：20260706-002")
        client_type = st.selectbox("客户初步类型", ["待确认", "现有卖家", "分销商", "创作者", "工厂B2B", "新手"])
        product = st.text_input("产品/品类", placeholder="例如：手机壳、家居香薰、服装、OEM包装")
        sales_channel = st.text_input("当前销售渠道", placeholder="例如：Shopify / TikTok Shop / Amazon / 线下 / 无")
        business_scale = st.text_input("GMV/订单/粉丝/私域", placeholder="例如：月GMV $8000；粉丝50k ER 3%；或未确认")
        budget = st.text_input("预算/付费意愿", placeholder="例如：预算$2000；愿意小额测试；只想免费")
        pain = st.multiselect("主要pain point", ["Sourcing", "Traffic / Ads", "Affiliate / Creator Sales", "Distributor / Reseller", "B2B Leads", "Store Setup", "Conversion", "Logistics", "Content / UGC", "Not clear"])
        data_foundation = st.multiselect("页面与数据基础", ["站点", "Pixel", "GA4", "表单", "WhatsApp", "归因"])
        product_features = st.multiselect("产品特征", ["强展示", "强解释", "可寄样", "可标准化", "B2B长决策"])
        materials = st.text_input("素材情况", placeholder="例如：产品图+视频齐全 / 部分素材 / 几乎没有")
        st.selectbox("Compliance Override", ["Auto", "Green normal", "Gray needs approval", "Red not allowed"], key="compliance_override_quick", help=COMPLIANCE_HELP)
        submitted = st.form_submit_button("生成快速评估", type="primary")

    if submitted:
        quick_text = f"客户类型：{client_type}\n产品品类：{product}\n当前销售渠道：{sales_channel}\n业务规模：{business_scale}\n预算付费意愿：{budget}\n主要pain point：{', '.join(pain)}\n页面与数据基础：{', '.join(data_foundation)}\n产品特征：{', '.join(product_features)}\n素材情况：{materials}"
        st.session_state["quick_text"] = quick_text
        st.session_state["quick_client_code"] = client_code
    if st.session_state.get("quick_text"):
        render_analysis(st.session_state["quick_text"], st.session_state.get("quick_client_code", ""), "quick")

else:
    st.header("3｜Benchmark：评分口径")
    st.caption("这是培训和复核用，不是日常主流程。")
    st.subheader("三轴结构")
    st.write("- Sourcing轴 = 货源稳定性")
    st.write("- Marketing轴 = 付费营销意愿 + 私域规模 + 原渠道销售表现")
    st.write("- 建站自助轴 = 建站电商基础 + 电子物料完备度")
    st.subheader("分项权重")
    for key, weight in CONFIG["weights"].items():
        st.write(f"- {key}: {weight}")
    st.subheader("评分选项")
    for key, opts in CONFIG["component_options"].items():
        with st.expander(key):
            for score, label in opts:
                st.write(f"{score}｜{label}")
    st.subheader("营销渠道")
    for k, v in CONFIG["marketing_subtypes"].items():
        st.write(f"- {k}：{v}")
    st.subheader("致谢")
    st.write("Handbook input：感谢 Frank 和 Jack 对 DHgate MyyBiz SP Follow-up Handbook 的输入。")
    st.write("Live Conversation Toolkit input：感谢 Ouna 对 Live Conversation & Interview Toolkit 的输入。")
