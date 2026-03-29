"""Seed script — populates Weaviate with starter content for RAG & product catalog."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db.weaviate_client import init_weaviate_schema
from services.rag_service import add_financial_content, add_et_product

# Initialize schema
init_weaviate_schema()

# ── Financial Content ─────────────────────────────────────────────────────────
ARTICLES = [
    ("What is a SIP?", "A Systematic Investment Plan (SIP) allows you to invest a fixed amount in mutual funds at regular intervals. It leverages rupee cost averaging and compounding to build long-term wealth.", "mutual_funds", "sip,mutual_funds,investment"),
    ("Understanding Mutual Fund Risk Levels", "Equity mutual funds carry higher risk but offer potentially higher returns. Debt funds are lower risk. Balanced/Hybrid funds offer a middle ground. Your choice should depend on your risk tolerance and investment horizon.", "mutual_funds", "risk,mutual_funds,equity,debt"),
    ("How Term Insurance Works", "Term life insurance provides a death benefit to your nominees if you pass away during the policy term. It's the most affordable form of life insurance and is recommended for anyone with financial dependants.", "insurance", "term,life,insurance,protection"),
    ("Tax Saving with ELSS Funds", "Equity Linked Savings Schemes (ELSS) offer up to ₹1.5 lakh deduction under Section 80C. They have a 3-year lock-in and invest in equities, making them ideal for long-term tax-efficient wealth creation.", "tax_saving", "tax,elss,80c,section80c"),
    ("Fixed Deposits vs Debt Mutual Funds", "FDs offer guaranteed returns but are taxed at your income slab. Debt mutual funds offer better post-tax returns for those in the 30% tax bracket holding for 3+ years.", "fixed_income", "fd,fixed_deposit,debt,tax"),
    ("Getting Started with Stock Market Investing", "Investing in stocks requires understanding companies, sectors, and market cycles. Start with blue-chip stocks, diversify across sectors, and invest only what you can afford to lose.", "stocks", "stocks,equity,market,trading"),
    ("NPS: National Pension System Explained", "NPS is a government-backed pension scheme. It offers market-linked returns and tax benefits under Section 80C and 80CCD. Ideal for long-term retirement planning.", "retirement", "nps,pension,retirement,80ccd"),
    ("Digital Gold: A Modern Way to Invest in Gold", "Digital gold allows you to buy, sell, and store gold online. It tracks real gold prices without the hassle of physical storage or purity concerns.", "gold", "gold,digital_gold,investment,hedge"),
    ("Credit Score: Why It Matters", "Your credit score (CIBIL score) determines your eligibility for loans and credit cards. A score above 750 is considered excellent. Pay EMIs on time and keep credit utilization below 30%.", "credit", "credit,cibil,loan,credit_card"),
    ("Emergency Fund: Building Your Financial Safety Net", "An emergency fund should cover 6-12 months of expenses. Keep it in a liquid instrument like a savings account or liquid mutual fund. Never invest your emergency fund in volatile assets.", "basics", "emergency,savings,financial_planning,basics"),
]

for title, content, category, tags in ARTICLES:
    uid = add_financial_content(title, content, category, tags)
    print(f"✅ Added article: {title} → {uid}")

# ── ET Products ───────────────────────────────────────────────────────────────
PRODUCTS = [
    ("ET Money - SIP Investments", "mutual_funds", "Start SIP investments in top-rated mutual funds directly from the ET Money app. Zero commission, expert recommendations, and goal-based investing.", "young_professional,mid_career,student", "moderate", "https://www.etmoney.com"),
    ("ET Markets - Stock Portfolio Tracker", "stocks", "Track your stock portfolio, get real-time market analysis, expert picks, and personalized news on ET Markets.", "young_professional,mid_career,business_owner", "aggressive", "https://markets.economictimes.com"),
    ("ET Money Tax Saver ELSS", "tax_saving", "Save up to ₹46,800 in taxes annually with the best ELSS funds curated by ET Money experts.", "young_professional,mid_career", "moderate", "https://www.etmoney.com/tax-saving"),
    ("Term Life Insurance Plan", "insurance", "Get comprehensive life coverage starting at ₹500/month. Compare top insurers and buy 100% online.", "young_professional,mid_career,pre_retiree", "conservative", "https://www.etmoney.com/insurance"),
    ("Fixed Deposit - High Yield FD", "fixed_income", "Book FDs with up to 9% interest rate from partner banks. Safe, guaranteed returns.", "pre_retiree,retiree", "conservative", "https://economictimes.indiatimes.com"),
    ("Personal Loan - Quick Approval", "loans", "Get pre-approved personal loans up to ₹25 lakhs at competitive interest rates. 100% digital process.", "young_professional,mid_career,business_owner", "moderate", "https://economictimes.indiatimes.com/wealth/borrow"),
    ("Credit Card - ET Rewards Card", "credit_card", "Earn 5X rewards on ET Money investments, 2X on shopping. Zero annual fee for the first year.", "young_professional,mid_career", "moderate", "https://economictimes.indiatimes.com/wealth/spend"),
    ("ET Money - NPS (National Pension System)", "retirement", "Open your NPS account online. Get additional ₹50,000 deduction under 80CCD(1B) beyond the 80C limit.", "mid_career,pre_retiree", "conservative", "https://www.etmoney.com/nps"),
]

for name, category, description, target_persona, risk_level, url in PRODUCTS:
    uid = add_et_product(name, category, description, target_persona, risk_level, url)
    print(f"✅ Added product: {name} → {uid}")

print("\n🎉 Seed complete!")
