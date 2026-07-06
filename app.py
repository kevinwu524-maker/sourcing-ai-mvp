import re
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Client Profile & Route Recommender V9", page_icon="🧭", layout="wide")

# -----------------------------
# Lightweight styling
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    .small-muted {color: #6b7280; font-size: 0.92rem;}
    .big-card {border: 1px solid #e5e7eb; border-radius: 14px; padding: 18px; background: #ffffff; margin-bottom: 12px;}
    .route-card {border: 1px solid #d1fae5; border-radius: 16px; padding: 18px; background: #ecfdf5; margin-bottom: 12px;}
    .warn-card {border: 1px solid #fde68a; border-radius: 16px; padding: 18px; background: #fffbeb; margin-bottom: 12px;}
    .danger-card {border: 1px solid #fecaca; border-radius: 16px; padding: 18px; background: #fef2f2; margin-bottom: 12px;}
    .metric-title {font-size: 0.85rem; color: #6b7280; margin-bottom: 4px;}
    .metric-value {font-size: 1.25rem; font-weight: 700; color: #111827;}
    .chip {display: inline-block; padding: 4px 10px; margin: 2px 4px 2px 0; border-radius: 999px; background: #f3f4f6; font-size: 0.86rem;}
    .copy-box {border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; background: #f9fafb; white-space: pre-wrap;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Knowledge base / sample cases
# -----------------------------
RED_KEYWORDS = [
    "毒品", "违禁药", "武器", "枪", "弹药", "烟草", "电子烟", "vape", "成人内容", "色情", "赌博", "博彩",
    "仿牌", "假货", "counterfeit", "大麻", "cbd", "thc", "加密理财", "金融服务", "危险化学品", "poison",
]
GRAY_KEYWORDS = [
    "保健品", "膳食补剂", "补剂", "减肥", "瘦身", "美容仪", "微整", "医疗器械", "成人向", "不露骨",
    "烟具配件", "博彩娱乐周边", "功效护肤", "祛痘", "美白", "抗衰", "丰胸", "medical", "health claim", "slimming", "whitening",
]

SAMPLE_CASES = {
    "Seller｜有销量，缺 sourcing + affiliate": {
        "expected": "Sourcing Support → MyyBiz CPS / Store",
        "note": "先验证供应链、目标价、MOQ 和样品；不要一开始只推 demo。",
        "text": """Client Name: HomeGlow Studio
Product Category: Home decor / LED mirror / room accessories
BD: Could you tell me what you're selling now and where you're selling it?
Client: We sell home decor items, mostly LED mirrors and small room accessories. We sell through Shopify and TikTok Shop. Shopify is doing around $8,000 to $12,000 monthly GMV. TikTok Shop is smaller, around 40 to 60 orders a month.
BD: What is the biggest challenge?
Client: Sourcing. Supplier price is not stable and quality is inconsistent. We want to test creator promotion but are not sure what commission rate makes sense.
BD: Existing product or custom?
Client: Mostly existing product, but we want custom packaging and our logo. Retail price is $59 to $79. Landed cost should be under $28. First order can be 300 units if sample is good.
BD: Paid ads or influencer campaigns?
Client: We spend $500 to $1,000 monthly on TikTok ads. We can offer 12% to 18% commission if margin works. We have product photos, videos, Shopify pages, and can share screenshots.
""",
    },
    "Creator｜强内容能力，无供应链": {
        "expected": "Co-Creation",
        "note": "先判断受众、内容风格、产品创意和 launch 能力，不要按普通 merchant 处理。",
        "text": """Client Name: Maya Lee
Product Category: Streetwear / lifestyle accessories
Client: I create streetwear and lifestyle content. I have 180,000 followers on TikTok and 62,000 on Instagram. Audience is women 18 to 28 in the U.S. My average TikTok video gets 20,000 to 50,000 views.
BD: Have you sold products before?
Client: Not my own product. I did affiliate links and brand deals. I sold around 240 units for a bag brand through TikTok Shop affiliate. I don't want to handle inventory or shipping.
BD: Product idea?
Client: A crossbody bag or phone charm line with my own color palette and packaging. I can create launch videos, livestreams, and styling content.
Client: I do not have budget for inventory, but I can commit content and promotion if product fits my audience. I care about design, packaging, and story.
""",
    },
    "Brand｜有产品，想要 KOL/KOC 种草": {
        "expected": "Myyshop / Product Seeding",
        "note": "核心是 UGC、review、unboxing 和种草；不要承诺大规模 GMV。",
        "text": """Client Name: PureSip Bottle
Product Category: Water bottle / outdoor lifestyle
Client: We sell reusable water bottles and outdoor drinkware. We have Shopify and Amazon. Amazon is around $15,000 monthly revenue.
Client: Traffic and awareness are the main challenges. Ads are getting expensive. We want UGC, reviews, unboxing videos, and micro influencers.
Client: We do not need sourcing now. We have inventory in the U.S. We can provide 100 to 150 samples over two months.
Client: First we want content exposure and product seeding. If creators perform well, we can set up affiliate commission, maybe 10%. We have product images, videos, reviews, and media kit.
""",
    },
    "Merchant｜想招代理/分销商": {
        "expected": "MyyBiz CPL / Distributor Lead Gen",
        "note": "关键词是 reseller/distributor/qualified lead，因此优先 CPL。",
        "text": """Client Name: FitPro Wholesale
Product Category: Fitness accessories / resistance bands
Client: We sell fitness accessories wholesale to local gyms and small retailers. We have a website but more like a catalog.
Client: We want more resellers and local distributors in California and Texas. Direct consumer sales are not priority. We need qualified leads, not just traffic.
Client: We have wholesale price list, MOQ by SKU, product photos, and shipping terms. Around 30 SKUs.
Client: We can test $1,000 if leads are relevant. Good leads are gym owners, fitness studios, sports stores, and small distributors with business email or store info.
""",
    },
    "Low readiness｜只有想法，缺产品/预算/渠道": {
        "expected": "Nurture / Self-service",
        "note": "不能因为客户感兴趣就推进。先教育，不进入 sourcing queue。",
        "text": """Client Name: New Starter
Product Category: Beauty / trending products
Client: I haven't started yet. I want to sell beauty products because I see people making money online.
Client: I don't have a product in mind. Maybe skincare, makeup tools, or something trending on TikTok.
Client: I might sell on TikTok or Instagram. I don't have a website. I have 500 followers on Instagram but don't post much.
Client: I prefer not to spend money first. I want to test for free if possible. No sales history or customer list. I just want something easy to make money.
""",
    },
    "Gray compliance｜功效护肤/减肥宣称": {
        "expected": "Compliance Review first; CPL only if approved",
        "note": "业务潜力可以中高，但合规优先，审批前不建议 CPC/CPS/Stripe。",
        "text": """Client Name: GlowFast Lab
Product Category: Skincare / body slimming cream
Client: We have a body slimming cream and whitening serum. The product page says it can reduce belly fat in 14 days and remove dark spots quickly. We want to run ads and find affiliates.
Client: Shopify and WhatsApp groups. Monthly revenue is around $6,000 from repeat customers.
BD: Certificates?
Client: Ingredient list from supplier, but no U.S. clinical test. We can edit claims if needed.
Client: We want CPC ads and affiliates, but can start with lead generation. Budget around $800 for testing.
""",
    },
}

ROUTE_DESCRIPTIONS = {
    "Sourcing Support": "客户主要痛点是找货、价格、MOQ、质量或定制。先验证供应链，不要先推完整营销方案。",
    "MyyBiz Store": "客户有产品/素材/电商基础，需要独立站、商品页、订单管理或收款闭环。",
    "MyyBiz CPC": "客户有产品和预算，主要缺流量。适合小预算广告测试，但要先确认素材和目标 CPA/ROAS。",
    "MyyBiz CPL": "客户想找代理、分销商、经销商或 B2B leads。适合 lead generation，而不是普通点击流量。",
    "MyyBiz CPS / Affiliate": "客户想让达人、affiliate 或分销员按销售拿佣金。必须确认佣金空间和样品能力。",
    "Co-Creation": "客户偏 creator，有内容/受众/创意，但不想承担库存和履约。适合共同开发产品。",
    "Myyshop / Product Seeding": "品牌/商家已有产品，希望通过 KOL/KOC 寄样、UGC、review、unboxing 增加曝光。",
    "Nurture / Self-service": "客户资源或信息不足，不适合深度投入。先教育、低频跟进，等明确行为信号。",
    "Compliance Review": "命中灰色/敏感风险。先审批，审批前不要承诺投放、收款或转化结果。",
    "Reject / Red Line": "红线类目，不推进任何渠道。",
}

# -----------------------------
# Helper functions
# -----------------------------
def norm(text):
    return (text or "").lower()


def contains_any(text, words):
    t = norm(text)
    return any(w.lower() in t for w in words)


def keyword_hit(text, keywords):
    t = norm(text)
    return [kw for kw in keywords if kw.lower() in t]


def extract_money_values(text):
    values = []
    if not text:
        return values
    patterns = [
        r"\$\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)(\s*[kKmM])?",
        r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)(\s*[kKmM])?\s*(?:usd|dollars|美金|美元)",
    ]
    for pat in patterns:
        for num, suffix in re.findall(pat, text):
            try:
                val = float(num.replace(",", ""))
                s = suffix.strip().lower()
                if s == "k":
                    val *= 1000
                elif s == "m":
                    val *= 1000000
                values.append(val)
            except Exception:
                pass
    return values


def extract_followers(text):
    t = text or ""
    values = []
    # very rough parser for "180,000 followers" or "50k followers"
    for m in re.findall(r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)(\s*[kKmM])?\s*(followers|粉丝)", t):
        num, suffix, _ = m
        try:
            val = float(num.replace(",", ""))
            s = suffix.strip().lower()
            if s == "k":
                val *= 1000
            elif s == "m":
                val *= 1000000
            values.append(int(val))
        except Exception:
            pass
    return values


def compliance_level(text, manual=None):
    manual = manual or "Auto"
    if manual.startswith("Red"):
        return "Red", ["manual red flag"]
    if manual.startswith("Gray"):
        return "Gray", ["manual gray flag"]
    red = keyword_hit(text, RED_KEYWORDS)
    gray = keyword_hit(text, GRAY_KEYWORDS)
    if red:
        return "Red", red
    if gray:
        return "Gray", gray
    return "Green", []


def detect_flags(text):
    t = norm(text)
    money = extract_money_values(text)
    followers = extract_followers(text)
    return {
        "money": money,
        "followers": followers,
        "creator": contains_any(t, ["creator", "influencer", "kol", "koc", "tiktok", "instagram", "youtube", "内容创作者", "达人", "网红", "粉丝"]),
        "strong_audience": contains_any(t, ["followers", "audience", "community", "email list", "customer list", "whatsapp group", "discord", "telegram", "粉丝", "社群", "客户名单"]) or (followers and max(followers) >= 10000),
        "merchant": contains_any(t, ["shopify", "amazon", "etsy", "tiktok shop", "store", "website", "brand", "merchant", "独立站", "商家", "店铺", "品牌"]),
        "has_sales": contains_any(t, ["gmv", "monthly revenue", "monthly sales", "orders", "sold", "sales", "月gmv", "月销售", "销量", "订单", "revenue"]),
        "has_proof": contains_any(t, ["screenshot", "store link", "shopify admin", "amazon seller", "后台", "截图", "店铺链接", "订单截图", "gmv截图"]),
        "has_product": contains_any(t, ["sku", "inventory", "stock", "already have product", "ready to list", "product images", "listing", "已有产品", "现货", "可以上架", "库存"]),
        "needs_sourcing": contains_any(t, ["sourcing", "source", "supplier", "factory", "1688", "alibaba", "找货", "寻源", "供应商", "工厂", "采购", "price not stable", "quality is inconsistent"]),
        "needs_traffic": contains_any(t, ["traffic", "exposure", "ads", "ad cost", "paid ads", "awareness", "流量", "曝光", "广告", "投放", "获客"]),
        "wants_affiliate": contains_any(t, ["affiliate", "commission", "creator promotion", "cps", "promoter", "佣金", "分销", "联盟", "带货", "达人"]),
        "wants_distributor": contains_any(t, ["reseller", "distributor", "agent", "wholesale", "dealer", "qualified leads", "代理", "分销商", "经销商", "批发"]),
        "wants_seeding": contains_any(t, ["seeding", "sample", "review", "unboxing", "ugc", "micro influencers", "寄样", "种草", "开箱", "测评"]),
        "has_budget": contains_any(t, ["budget", "ad spend", "marketing budget", "paid ads", "test $", "广告预算", "投放预算", "小额测试", "愿意投"]) or any(v >= 200 for v in money),
        "has_materials": contains_any(t, ["photo", "image", "video", "media kit", "product page", "listing", "素材", "图片", "视频", "卖点", "价格表"]),
        "has_moq_price": contains_any(t, ["moq", "target price", "retail price", "landed cost", "purchase price", "目标价", "采购价", "零售价", "毛利", "起订量"]),
        "custom": contains_any(t, ["custom", "logo", "packaging", "label", "material", "size", "定制", "包装", "材质", "尺寸", "颜色"]),
        "zero_resource": contains_any(t, ["no product", "no traffic", "no budget", "free if possible", "first time", "haven't started", "没有产品", "没有流量", "没有预算", "纯新手", "只想免费"]),
        "stripe_payment": contains_any(t, ["stripe", "payment", "paypal", "收款", "公司主体", "履约"]),
        "decision_maker": contains_any(t, ["owner", "founder", "ceo", "decision maker", "老板", "创始人", "本人决定", "我可以决定"]),
    }


def score_from_flags(flags):
    # Keep score in background. Employees see profile/actions first.
    product = 35
    if flags["needs_sourcing"]:
        product += 15
    if flags["has_moq_price"]:
        product += 18
    if flags["has_product"]:
        product += 12
    if flags["custom"]:
        product -= 4
    if flags["has_materials"]:
        product += 8
    if flags["zero_resource"]:
        product -= 25

    client = 30
    if flags["has_sales"]:
        client += 20
    if flags["has_budget"]:
        client += 16
    if flags["strong_audience"]:
        client += 14
    if flags["merchant"]:
        client += 10
    if flags["has_proof"]:
        client += 10
    if flags["zero_resource"]:
        client -= 30

    channel = 30
    if flags["wants_affiliate"]:
        channel += 18
    if flags["wants_distributor"]:
        channel += 18
    if flags["needs_traffic"]:
        channel += 10
    if flags["has_product"]:
        channel += 10
    if flags["has_materials"]:
        channel += 8
    if flags["zero_resource"]:
        channel -= 25

    product = max(0, min(100, product))
    client = max(0, min(100, client))
    channel = max(0, min(100, channel))
    raw = round(product * 0.35 + client * 0.35 + channel * 0.30, 1)
    return product, client, channel, raw


def evidence_level(flags):
    if flags["has_proof"]:
        return "High", 1.00
    if flags["has_sales"] or flags["has_budget"] or flags["money"] or flags["followers"]:
        return "Medium", 0.88
    return "Low", 0.75


def confidence_level(flags, missing_count):
    evidence, _ = evidence_level(flags)
    positives = sum(1 for k in ["has_sales", "has_budget", "has_product", "has_materials", "has_moq_price", "strong_audience", "wants_affiliate", "wants_distributor", "needs_sourcing"] if flags.get(k))
    if evidence == "High" and positives >= 5 and missing_count <= 3:
        return "High"
    if evidence in ["High", "Medium"] and positives >= 3 and missing_count <= 6:
        return "Medium"
    return "Low"


def priority_from_score(score, compliance):
    if compliance == "Red":
        return "Reject"
    if compliance == "Gray":
        return "Compliance Review"
    if score >= 82:
        return "A / Fast Track"
    if score >= 68:
        return "B / Good Fit"
    if score >= 52:
        return "C / Test & Validate"
    if score >= 38:
        return "D / Nurture"
    return "E / Not Ready"


def recommend_route(flags, compliance):
    if compliance == "Red":
        return "Reject / Red Line"
    if compliance == "Gray":
        return "Compliance Review"
    if flags["zero_resource"]:
        return "Nurture / Self-service"
    if flags["creator"] and flags["strong_audience"] and not flags["has_product"]:
        return "Co-Creation"
    if flags["wants_distributor"]:
        return "MyyBiz CPL"
    if flags["wants_seeding"] and flags["has_product"]:
        return "Myyshop / Product Seeding"
    if flags["needs_sourcing"]:
        if flags["wants_affiliate"]:
            return "Sourcing Support → MyyBiz CPS / Affiliate"
        return "Sourcing Support"
    if flags["wants_affiliate"]:
        return "MyyBiz CPS / Affiliate"
    if flags["needs_traffic"] and flags["has_budget"]:
        return "MyyBiz CPC"
    if flags["merchant"] and flags["has_product"]:
        return "MyyBiz Store"
    return "Nurture / Self-service"


def missing_info(text):
    checks = [
        ("主营品类 / 具体产品", ["category", "product", "品类", "产品", "sku"]),
        ("当前销售渠道", ["shopify", "amazon", "etsy", "tiktok shop", "website", "销售渠道", "平台", "独立站"]),
        ("GMV / 订单量 / 生意规模", ["gmv", "orders", "monthly sales", "revenue", "订单", "销量", "月销售"]),
        ("销售证明 / 店铺链接 / 截图", ["screenshot", "store link", "shopify admin", "截图", "店铺链接", "后台"]),
        ("目标采购价 / 零售价 / 毛利", ["target price", "retail price", "landed cost", "margin", "目标价", "采购价", "零售价", "毛利"]),
        ("MOQ / 首单预算", ["moq", "budget", "first order", "minimum order", "预算", "首单", "起订量"]),
        ("定制范围", ["custom", "logo", "packaging", "material", "size", "定制", "包装", "材质", "尺寸"]),
        ("流量来源 / 私域 / 达人资源", ["traffic", "followers", "community", "influencer", "流量", "粉丝", "社群", "达人"]),
        ("营销预算 / 广告经验", ["paid ads", "ad spend", "marketing budget", "广告", "投放", "预算"]),
        ("佣金比例 / Affiliate 结构", ["commission", "affiliate", "cps", "佣金", "分销", "联盟"]),
        ("收款 / Stripe / 履约", ["stripe", "payment", "fulfillment", "收款", "履约", "物流"]),
        ("最大痛点", ["challenge", "headache", "pain", "bottleneck", "难题", "痛点", "瓶颈"]),
    ]
    present = []
    missing = []
    for label, words in checks:
        if contains_any(text, words):
            present.append(label)
        else:
            missing.append(label)
    return present, missing


def infer_client_type(flags):
    if flags["creator"] and flags["strong_audience"] and not flags["has_product"]:
        return "Creator / Influencer"
    if flags["wants_distributor"]:
        return "Wholesale / Distributor-focused Merchant"
    if flags["wants_seeding"] and flags["has_product"]:
        return "Brand seeking KOL/KOC exposure"
    if flags["merchant"] and flags["has_sales"]:
        return "Existing Ecommerce Seller / Brand"
    if flags["zero_resource"]:
        return "Beginner / Low-readiness Lead"
    if flags["merchant"]:
        return "Merchant / Seller"
    return "Unknown / Needs more discovery"


def infer_business_stage(flags):
    if flags["zero_resource"]:
        return "Idea stage / Not ready"
    if flags["has_sales"] and flags["has_proof"]:
        return "Validated / Evidence-backed"
    if flags["has_sales"]:
        return "Growing / Sales claimed"
    if flags["has_product"]:
        return "Product-ready / Sales unclear"
    return "Early discovery"


def infer_pain_point(flags):
    pains = []
    if flags["needs_sourcing"]:
        pains.append("Sourcing / supplier stability")
    if flags["needs_traffic"]:
        pains.append("Traffic / awareness")
    if flags["wants_affiliate"]:
        pains.append("Affiliate / creator sales")
    if flags["wants_distributor"]:
        pains.append("Distributor / reseller acquisition")
    if flags["wants_seeding"]:
        pains.append("UGC / KOL seeding")
    if not pains:
        pains.append("Not clearly confirmed")
    return "; ".join(pains[:3])


def product_readiness(flags):
    if flags["has_product"] and flags["has_materials"]:
        return "High：已有产品和素材"
    if flags["has_product"]:
        return "Medium：有产品，但素材/详情需补"
    if flags["needs_sourcing"] and flags["has_moq_price"]:
        return "Medium：需求较清楚，需要 sourcing 验证"
    if flags["needs_sourcing"]:
        return "Low-Medium：需要找货，但参数不完整"
    return "Low / Unknown：产品方向未明确"


def marketing_readiness(flags):
    if flags["has_budget"] and (flags["wants_affiliate"] or flags["needs_traffic"] or flags["wants_seeding"]):
        return "High-Medium：有预算/意愿，可小测"
    if flags["strong_audience"]:
        return "Medium：有受众/私域，但转化方式需确认"
    if flags["wants_affiliate"]:
        return "Medium-Low：想做分销，但佣金/样品需确认"
    return "Low / Unknown"


def build_profile(text, flags, route, compliance):
    client_type = infer_client_type(flags)
    stage = infer_business_stage(flags)
    money = flags["money"]
    followers = flags["followers"]
    scale_parts = []
    if money:
        scale_parts.append("提到金额：" + ", ".join(["$%s" % int(v) for v in money[:4]]))
    if followers:
        scale_parts.append("粉丝量：" + ", ".join([str(v) for v in followers[:4]]))
    if flags["has_sales"] and not scale_parts:
        scale_parts.append("有销售/订单信号，但数字未确认")
    if not scale_parts:
        scale_parts.append("Not confirmed")

    return {
        "Client Type": client_type,
        "Business Stage": stage,
        "Compliance": compliance,
        "Main Pain Point": infer_pain_point(flags),
        "Product Readiness": product_readiness(flags),
        "Marketing Readiness": marketing_readiness(flags),
        "Business Scale": "; ".join(scale_parts),
        "Best Route": route,
        "Evidence": evidence_level(flags)[0],
    }


def build_next_steps(flags, route, compliance, evidence, missing):
    if compliance == "Red":
        internal = ["记录红线原因，不进入 sourcing / payment / advertising pipeline。", "如客户愿意，要求其更换合规类目后重新评估。"]
        client = "Thanks for sharing this. Based on our current policy, this category is not something we can support. If you have another product category, I’m happy to review that instead."
        do_not = ["不要讨论 Stripe、CPC、CPS 或具体采购执行。", "不要给出任何可推进的暗示。"]
        return internal, client, do_not
    if compliance == "Gray":
        internal = ["先收集合规材料：成分/证书/页面文案/广告宣称/产品图。", "审批前只做轻量沟通；如必须测试，优先 CPL。"]
        client = "Before we talk about traffic or sales channels, I’d like to confirm the compliance side first. Could you share the product page claims, ingredient/certification documents, and any ad copy you plan to use?"
        do_not = ["审批前不要承诺 CPC/CPS/Stripe。", "不要使用保证效果、治疗、减肥、美白等表达。"]
        return internal, client, do_not

    internal = []
    do_not = []

    if "Sourcing" in route:
        internal.extend(["先让 BD 补齐目标价、MOQ、定制范围和参考图。", "Sourcing 只做 2-3 个轻量款式/报价初筛，先不要深度开发。"])
        client = "Based on what you shared, I think the first step should be validating the sourcing side — especially target price, MOQ, customization, and sample expectations. Once we know the product can work, we can decide whether MyyBiz Store, CPS, or another route makes sense."
    elif "Co-Creation" in route:
        internal.extend(["先确认 creator 受众画像、内容表现、产品创意和可投入的 launch 内容。", "不要按普通 merchant 推建站；先判断是否能形成 hero product。"])
        client = "It sounds like your biggest value is your audience and creative direction. I’d suggest we first explore whether there’s a product idea that feels authentic to your personal brand, then we can discuss how DHgate can support product development, sampling, and launch."
    elif "CPL" in route:
        internal.extend(["确认目标 lead 画像：地区、行业、职位/店铺类型、表单字段。", "确认谁负责 24-48 小时内 follow up leads。"])
        client = "Since you’re mainly trying to find resellers or distributors, I think a lead-generation approach makes more sense than just driving traffic. Let’s define what a qualified lead looks like first, then we can test CPL."
    elif "CPS" in route or "Affiliate" in route:
        internal.extend(["先测算佣金空间：产品成本、履约成本、可给佣金比例。", "确认样品数量、creator profile 和 tracking link 设置。"])
        client = "Since you’re interested in affiliate or creator-driven sales, the next step is to confirm whether the margin can support commission and whether you can provide samples/content assets for a small test."
    elif "CPC" in route:
        internal.extend(["确认投放预算、目标 CPA/ROAS、素材和落地页准备度。", "预算或素材不清前，不启动投放。"])
        client = "If traffic is the main goal, we can look at a small CPC test, but I’d first want to confirm your test budget, product page, creative materials, and what result would count as success."
    elif "Myyshop" in route:
        internal.extend(["确认样品数量、目标 KOL/KOC 画像、内容交付形式和时间线。", "先做小批量 seeding，不承诺大规模销售。"])
        client = "It sounds like product seeding and creator content may be the right first step. Let’s define the creator profile, sample quantity, and what content outcome matters most — UGC, reviews, unboxing, or livestream."
    elif "Store" in route:
        internal.extend(["确认 SKU、产品素材、价格、库存、收款和履约准备。", "安排 5 分钟 MyyBiz Store demo，但只讲与客户痛点相关的部分。"])
        client = "Based on your current setup, MyyBiz may help as a lightweight store and order-management tool. Before a demo, I’d like to confirm your SKU list, product assets, pricing, and payment/fulfillment setup."
    else:
        internal.extend(["轻量 nurture：发自助教程/爆品清单/基础问卷。", "等客户有明确产品、预算、渠道或销售证明后再升级。"])
        client = "I think it may be better to start lighter for now. If you can share a clearer product direction, rough budget, or current selling channel, I can better decide which resources are actually useful for you."

    if evidence == "Low":
        internal.append("先要证据，不要直接给高优先级：店铺链接、截图、订单、素材或预算范围。")
        do_not.append("不要因为客户口述 GMV、粉丝或资源就直接判断为 A 类。")
    if "目标采购价 / 零售价 / 毛利" in missing or "MOQ / 首单预算" in missing:
        do_not.append("价格、MOQ 和预算不清前，不要让 sourcing 深度投入。")
    if "佣金比例 / Affiliate 结构" in missing and ("CPS" in route or "Affiliate" in route):
        do_not.append("佣金结构不清前，不要承诺 affiliate/CPS 效果。")
    if not do_not:
        do_not.append("不要一次性介绍所有产品线，只讲当前客户最相关的一条路径。")
    return internal, client, do_not


def closing_questions(route, missing):
    route_questions = []
    if "Sourcing" in route:
        route_questions = [
            "Could you send 1-2 reference links or images so our sourcing team can match the exact style?",
            "What target purchase price and first-order quantity would make this worth testing?",
            "Which requirements are must-have versus flexible — logo, packaging, material, size, or color?",
        ]
    elif "Co-Creation" in route:
        route_questions = [
            "What product idea feels most authentic to your audience and personal brand?",
            "Can you share your best-performing content examples and audience profile?",
            "How involved do you want to be in design, sampling review, and launch promotion?",
        ]
    elif "CPL" in route:
        route_questions = [
            "What does a qualified reseller/distributor look like for you?",
            "Which region or customer segment should we target first?",
            "Who on your side will follow up with leads within 24-48 hours?",
        ]
    elif "CPS" in route or "Affiliate" in route:
        route_questions = [
            "What commission range can your margin support after product and fulfillment cost?",
            "How many samples can you provide for the first creator/affiliate test?",
            "What creator profile fits your product best — platform, niche, audience, and content style?",
        ]
    elif "Myyshop" in route:
        route_questions = [
            "What content outcome matters most: UGC, review, unboxing, livestream, or conversion?",
            "How many samples can you provide for the first seeding batch?",
            "Which creator niche and platform are the best match for this product?",
        ]
    else:
        route_questions = [
            "What is the one product/category you want to test first?",
            "What channel are you currently using to reach customers?",
            "What rough budget or resource can you commit to the first small test?",
        ]

    missing_map = {
        "GMV / 订单量 / 生意规模": "Roughly, is this currently test orders or stable monthly volume?",
        "销售证明 / 店铺链接 / 截图": "If we move forward, could you share a store link or simple screenshot so our team can prioritize it?",
        "目标采购价 / 零售价 / 毛利": "Do you have a target purchase price and retail price range in mind?",
        "MOQ / 首单预算": "What first-order quantity or MOQ would feel comfortable for you?",
        "定制范围": "Are you looking for existing products, light customization, or full custom development?",
        "营销预算 / 广告经验": "Would you be open to a small paid test, or do you prefer a commission-based model first?",
        "收款 / Stripe / 履约": "Do you already have payment and fulfillment set up, or would you need support there?",
    }
    extra = [missing_map[m] for m in missing if m in missing_map]
    qs = []
    for q in route_questions + extra:
        if q not in qs:
            qs.append(q)
    return qs[:6]


def crm_note(profile, route, priority, confidence, internal, client_msg, missing, human_route=None, human_reason=None):
    final_route = human_route if human_route and human_route != "Use system recommendation" else route
    note = f"""Client Profile Summary
- Client Type: {profile['Client Type']}
- Business Stage: {profile['Business Stage']}
- Compliance: {profile['Compliance']}
- Current Scale: {profile['Business Scale']}
- Main Pain Point: {profile['Main Pain Point']}
- Product Readiness: {profile['Product Readiness']}
- Marketing Readiness: {profile['Marketing Readiness']}

Recommendation
- System Route: {route}
- Final Route: {final_route}
- Priority: {priority}
- Confidence: {confidence}

Internal Next Steps
"""
    for i, item in enumerate(internal, 1):
        note += f"{i}. {item}\n"
    note += "\nMissing Info\n"
    if missing:
        for i, item in enumerate(missing[:8], 1):
            note += f"{i}. {item}\n"
    else:
        note += "No major missing info detected.\n"
    note += "\nClient-facing Follow-up\n" + client_msg + "\n"
    if human_reason:
        note += "\nHuman Review Reason\n" + human_reason + "\n"
    return note


def analyze_text(text, manual_compliance="Auto"):
    compliance, hits = compliance_level(text, manual_compliance)
    flags = detect_flags(text)
    present, missing = missing_info(text)
    product_s, client_s, channel_s, raw = score_from_flags(flags)
    evidence, multiplier = evidence_level(flags)
    adjusted = round(raw * multiplier, 1)
    route = recommend_route(flags, compliance)
    priority = priority_from_score(adjusted, compliance)
    conf = confidence_level(flags, len(missing))
    profile = build_profile(text, flags, route, compliance)
    internal, client_msg, do_not = build_next_steps(flags, route, compliance, evidence, missing)
    qs = closing_questions(route, missing)
    return {
        "compliance": compliance,
        "compliance_hits": hits,
        "flags": flags,
        "present": present,
        "missing": missing,
        "scores": {"Product/Sourcing": product_s, "Client Value": client_s, "Channel Fit": channel_s, "Raw": raw, "Adjusted": adjusted},
        "evidence": evidence,
        "route": route,
        "priority": priority,
        "confidence": conf,
        "profile": profile,
        "internal": internal,
        "client_msg": client_msg,
        "do_not": do_not,
        "questions": qs,
    }


def render_profile(profile):
    cols = st.columns(3)
    items = list(profile.items())
    for idx, (k, v) in enumerate(items):
        with cols[idx % 3]:
            st.markdown(f"<div class='big-card'><div class='metric-title'>{k}</div><div class='metric-value'>{v}</div></div>", unsafe_allow_html=True)


def render_results(result, evaluator="", client_code=""):
    compliance = result["compliance"]
    card_class = "danger-card" if compliance == "Red" else "warn-card" if compliance == "Gray" else "route-card"
    st.markdown(
        f"""
        <div class='{card_class}'>
            <div class='metric-title'>Recommended Route</div>
            <div style='font-size:1.65rem;font-weight:800;'>{result['route']}</div>
            <div style='margin-top:8px;'>{ROUTE_DESCRIPTIONS.get(result['route'].split(' → ')[0], ROUTE_DESCRIPTIONS.get(result['route'], ''))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Priority", result["priority"])
    c2.metric("Confidence", result["confidence"])
    c3.metric("Evidence", result["evidence"])
    c4.metric("Adjusted Score", result["scores"]["Adjusted"])

    st.subheader("Client Profile 客户画像")
    render_profile(result["profile"])

    st.subheader("What should we do next?")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Internal Next Steps（内部动作）**")
        for item in result["internal"]:
            st.write("- " + item)
    with col2:
        st.markdown("**Do Not Do Yet（暂时不要做）**")
        for item in result["do_not"]:
            st.write("- " + item)

    st.markdown("**Client-facing Follow-up（可发客户）**")
    st.markdown(f"<div class='copy-box'>{result['client_msg']}</div>", unsafe_allow_html=True)

    with st.expander("Missing Info & Closing Questions（缺失信息 + 收尾确认问题）", expanded=True):
        st.markdown("**Missing Info**")
        if result["missing"]:
            for item in result["missing"][:10]:
                st.write("- " + item)
        else:
            st.write("No major missing info detected.")
        st.markdown("**2-minute closing questions**")
        for q in result["questions"]:
            st.write("- " + q)

    with st.expander("Scoring Details（评分细节，给 manager/复核用）", expanded=False):
        score_df = pd.DataFrame([
            {"Dimension": "Product / Sourcing", "Score": result["scores"]["Product/Sourcing"]},
            {"Dimension": "Client Value", "Score": result["scores"]["Client Value"]},
            {"Dimension": "Channel Fit", "Score": result["scores"]["Channel Fit"]},
            {"Dimension": "Raw Overall", "Score": result["scores"]["Raw"]},
            {"Dimension": "Adjusted Overall", "Score": result["scores"]["Adjusted"]},
        ])
        st.dataframe(score_df, use_container_width=True, hide_index=True)
        if result["compliance_hits"]:
            st.write("Compliance hits:", ", ".join(result["compliance_hits"]))
        st.write("Detected signals:")
        signal_tags = [k for k, v in result["flags"].items() if isinstance(v, bool) and v]
        st.markdown(" ".join([f"<span class='chip'>{s}</span>" for s in signal_tags]), unsafe_allow_html=True)

    st.subheader("Human Final Review")
    c1, c2 = st.columns(2)
    with c1:
        agree = st.radio("Do you agree with the system recommendation?", ["Agree", "Partially agree", "Disagree"], horizontal=True, key="agree_radio")
    with c2:
        final_route = st.selectbox(
            "Human Final Route",
            ["Use system recommendation", "Sourcing Support", "MyyBiz Store", "MyyBiz CPC", "MyyBiz CPL", "MyyBiz CPS / Affiliate", "Co-Creation", "Myyshop / Product Seeding", "Nurture / Self-service", "Compliance Review", "Reject / Red Line"],
            key="final_route",
        )
    human_reason = st.text_area("Reason for override / notes", placeholder="Example: System recommended CPS, but margin is not confirmed yet, so final route should be Sourcing Support first.", key="human_reason")

    note = crm_note(result["profile"], result["route"], result["priority"], result["confidence"], result["internal"], result["client_msg"], result["missing"], final_route, human_reason)
    st.subheader("Copy-ready CRM Note")
    st.text_area("Copy this into CRM / Slack / follow-up doc", value=note, height=360)

    export_row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "evaluator": evaluator,
        "client_code": client_code,
        "system_route": result["route"],
        "human_final_route": final_route,
        "agree": agree,
        "priority": result["priority"],
        "confidence": result["confidence"],
        "evidence": result["evidence"],
        "adjusted_score": result["scores"]["Adjusted"],
        "client_type": result["profile"]["Client Type"],
        "business_stage": result["profile"]["Business Stage"],
        "main_pain_point": result["profile"]["Main Pain Point"],
        "missing_info": "; ".join(result["missing"]),
        "human_reason": human_reason,
        "crm_note": note,
    }
    export_df = pd.DataFrame([export_row])
    st.download_button(
        "Download Result CSV",
        export_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="client_profile_result_v9.csv",
        mime="text/csv",
    )

# -----------------------------
# Sidebar / navigation
# -----------------------------
st.sidebar.title("🧭 Start Here")
mode = st.sidebar.radio(
    "你现在想做什么？",
    ["1｜Analyze Interview", "2｜Quick Assessment", "3｜Training Sample", "4｜Benchmark / Credits"],
)

st.sidebar.markdown("---")
st.sidebar.caption("V9 focuses on employee-friendly workflow: profile first, action second, score last.")

st.title("Client Profile & Route Recommender V9")
st.caption("自然访谈输入 → 自动生成客户画像 → 推荐路线 → 内部动作 → 客户 follow-up → 人工最终确认。")

# Shared metadata
with st.expander("Case Info（可选，用于导出和团队收集）", expanded=False):
    col_a, col_b, col_c = st.columns(3)
    evaluator = col_a.text_input("Evaluator Name", placeholder="Kevin / Frank / Jack / Ouna")
    client_code = col_b.text_input("Client Code", placeholder="20260706-001，不建议放真实全名")
    source_channel = col_c.selectbox("Source Channel", ["Unknown", "Interview", "WhatsApp", "Event", "Referral", "DHgate Buyer", "Email", "Other"])

if mode == "1｜Analyze Interview":
    st.header("1｜Analyze Interview / Call Notes")
    st.write("把 interview transcript、call notes 或 WhatsApp 聊天记录粘进来。员工不需要先理解评分，先看客户画像和下一步动作。")
    manual = st.selectbox("Compliance Override（可选）", ["Auto", "Green / normal", "Gray / needs approval", "Red / not allowed"])
    text = st.text_area("Paste Interview / Call Notes", height=300, placeholder="Paste interview notes here...")
    if st.button("Generate Client Profile", type="primary"):
        if not text.strip():
            st.warning("请先粘贴 interview / call notes。")
        else:
            result = analyze_text(text, manual)
            render_results(result, evaluator, client_code)

elif mode == "2｜Quick Assessment":
    st.header("2｜Quick Assessment / 2分钟快速评估")
    st.write("没有 transcript 的时候，用简单问题快速生成 profile。员工不需要看权重，只回答事实。")
    with st.form("quick_form"):
        q_client = st.selectbox("客户大概是哪类？", ["Existing ecommerce seller / brand", "Creator / influencer", "Wholesale / distributor-focused merchant", "Beginner / unknown", "Brand seeking KOL exposure"])
        q_product = st.text_input("产品/品类", placeholder="home decor, skincare, water bottle...")
        q_channel = st.multiselect("现在在哪些渠道卖/触达客户？", ["Shopify", "Amazon", "TikTok Shop", "Etsy", "Own website", "Offline", "WhatsApp/Community", "Instagram/TikTok content", "Not selling yet"])
        q_scale = st.selectbox("生意规模", ["Not confirmed", "No sales yet", "Test orders only", "Monthly GMV $1k-$5k", "Monthly GMV $5k-$20k", "Monthly GMV $20k+"])
        q_pain = st.multiselect("最大痛点", ["Sourcing", "Traffic / ads", "Affiliate / creator sales", "Distributor / reseller leads", "KOL/KOC seeding", "Store setup", "Conversion", "Logistics", "Not clear"])
        q_readiness = st.multiselect("已经准备好的东西", ["Product/SKU", "Inventory", "Product photos/videos", "Store link", "Sales screenshot", "Target price/MOQ", "Marketing budget", "Commission range", "Samples for creators", "None"])
        q_compliance = st.selectbox("合规判断", ["Auto", "Green / normal", "Gray / needs approval", "Red / not allowed"])
        submitted = st.form_submit_button("Generate Quick Profile")
    if submitted:
        synthetic = f"""
        Client type: {q_client}
        Product category: {q_product}
        Sales channels: {', '.join(q_channel)}
        Business scale: {q_scale}
        Pain points: {', '.join(q_pain)}
        Readiness: {', '.join(q_readiness)}
        """
        result = analyze_text(synthetic, q_compliance)
        render_results(result, evaluator, client_code)

elif mode == "3｜Training Sample":
    st.header("3｜Training Sample / 员工练习模式")
    st.write("先让员工自己判断路线，再看系统结果。这个模式适合 onboarding 和团队校准。")
    case_name = st.selectbox("Choose a sample case", list(SAMPLE_CASES.keys()))
    case = SAMPLE_CASES[case_name]
    st.markdown(f"**Training Note:** {case['note']}")
    with st.expander("View Sample Interview", expanded=True):
        st.text_area("Sample transcript", value=case["text"], height=260)
    guess = st.selectbox("你觉得这个客户最适合哪条路线？", ["Sourcing Support", "MyyBiz Store", "MyyBiz CPC", "MyyBiz CPL", "MyyBiz CPS / Affiliate", "Co-Creation", "Myyshop / Product Seeding", "Nurture / Self-service", "Compliance Review", "Reject / Red Line"])
    if st.button("Show System Analysis", type="primary"):
        st.info(f"Expected training route: {case['expected']}")
        result = analyze_text(case["text"], "Auto")
        render_results(result, evaluator, client_code)

else:
    st.header("4｜Benchmark / Credits")
    st.subheader("How employees should use this tool")
    st.write(
        """
        1. 先用 Interview Analyzer 生成客户画像，不要先纠结分数。  
        2. 看 Recommended Route、Priority、Confidence 和 Client-facing Follow-up。  
        3. 缺信息时，不要强推 demo 或 sourcing；用 Missing Info 里的问题补齐。  
        4. 最终路线必须由员工在 Human Final Review 里确认或 override。  
        5. 导出 CSV 后可以汇总到 Google Sheet，比较 system route 和 human route。
        """
    )
    st.subheader("Simple benchmark rules")
    benchmark = pd.DataFrame([
        {"Area": "Sales", "High": "月 GMV ≥ $20k 或订单 ≥300", "Medium": "$1k-$20k 或少量真实订单", "Low": "无销售/无计划"},
        {"Area": "Traffic", "High": "名单 ≥5k 或社媒 ≥50k 且互动好", "Medium": "名单 300-5k 或社媒 2k-50k", "Low": "无私域且不愿买流量"},
        {"Area": "Budget", "High": "月预算 ≥$2k 或稳定投放", "Medium": "$200-$2k 小测/接受 CPS", "Low": "只想免费/不分佣"},
        {"Area": "Sourcing", "High": "目标价/MOQ/图/规格/交期齐", "Medium": "缺 1-2 个参数", "Low": "只有泛品类想法"},
        {"Area": "Evidence", "High": "截图/订单/后台/店铺链接", "Medium": "口述 + 部分材料", "Low": "只有口述"},
    ])
    st.dataframe(benchmark, use_container_width=True, hide_index=True)
    st.subheader("Acknowledgements")
    st.markdown(
        """
        - **Handbook input:** Special thanks to **Frank** and **Jack** for their input on the DHgate MyyBiz SP Follow-up Handbook.  
        - **Live Conversation Toolkit input:** Special thanks to **Ouna** for her input on the Live Conversation & Interview Toolkit.
        """
    )
