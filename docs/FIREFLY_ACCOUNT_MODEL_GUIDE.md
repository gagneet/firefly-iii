# Firefly III Account Model & Transaction Guide

## Understanding Firefly III's Double-Entry Bookkeeping System

Firefly III uses a **double-entry bookkeeping** system, which means every transaction has TWO sides: money moves FROM somewhere TO somewhere else. This guide explains how Firefly III tracks your money flow and why it uses different account types.

---

## Account Types in Firefly III

### 1. Asset Accounts (Your Real Accounts)

**What they are:** Your actual bank accounts, savings accounts, checking accounts that hold YOUR money.

**Examples:**
- CommBank Everyday Savings
- CommBank Everyday Offset
- ING Savings Maximiser
- ING Orange Everyday

**What shows up here:**
- Actual account balances
- All deposits (money coming in)
- All withdrawals (money going out)
- Transfers between your accounts

**In your case:** These are your Spend and Savings accounts where income arrives and from where you pay bills, credit cards, and loans.

---

### 2. Liability Accounts (Your Real Debts)

**What they are:** Money you OWE to others - credit cards, loans, mortgages.

**Examples:**
- AMEX Credit Card
- CommBank MasterCard
- CommBank Home Loan
- CommBank Personal Loan

**What shows up here:**
- How much you owe (debt balance)
- Purchases that increase your debt
- Payments that reduce your debt

**In your case:** Your credit cards and home loans. When you buy something on AMEX, the debt increases. When you pay from your savings account, the debt decreases.

---

### 3. Expense Accounts (Virtual - Where Money Goes)

**What they are:** VIRTUAL accounts representing stores, merchants, and places where you SPEND money. These are NOT real accounts - they're just labels to categorize spending.

**Examples:**
- Woolworths (supermarket)
- Coles (supermarket)
- Bunnings (hardware)
- Wilson Parking
- Netflix subscription

**Why they exist:**
- To answer: "How much did I spend at Woolworths this month?"
- To answer: "What's my total grocery spending across ALL my accounts?"
- To categorize expenses for budgeting and reporting

**How they're created:**
- Automatically created by Firefly when you make a withdrawal/expense
- You never see them in your bank - they exist only in Firefly
- With our new code: merchant names are normalized (e.g., "WOOLWORTHS 1234 BELCONNEN" becomes just "Woolworths")

**In your case:** Every purchase you make (on credit card or from savings) creates an expense categorized by merchant.

---

### 4. Revenue Accounts (Virtual - Where Money Comes From)

**What they are:** VIRTUAL accounts representing sources of INCOME. These are NOT real accounts - they're labels to track where money comes from.

**Examples:**
- Salary (your employer)
- Interest Income (from savings accounts)
- Loan Repayment (money coming back to you)
- Tax Refund

**Why they exist:**
- To answer: "How much salary did I receive this year?"
- To answer: "How much interest income did I earn?"
- To track income sources for reporting

**How they're created:**
- Automatically created by Firefly when you make a deposit
- You never see them in your bank - they exist only in Firefly
- With our new code: income sources are normalized (e.g., "Salary SAI GLOBAL PAYRO 006064" becomes just "Salary")

**In your case:** When salary hits your everyday account, it's tracked as coming from "Salary" revenue account.

---

## How Transactions Work - Real Examples

### Example 1: Buying Groceries with Credit Card

**What happens in real life:**
- You buy $150 of groceries at Woolworths
- Your AMEX credit card balance increases by $150 (you owe more)

**What Firefly III records:**

```
Transaction Type: Withdrawal (expense)
Date: 2025-10-08
Amount: $150.00
Description: WOOLWORTHS 1234 BELCONNEN AUS Card xx1234

FROM (Source):     AMEX Credit Card (liability account) → debt increases by $150
TO (Destination):  Woolworths (expense account - VIRTUAL) → tracks spending
```

**What you see:**
- **AMEX Account:** Shows -$150 transaction, balance increases to reflect more debt
- **Woolworths Expense Account:** Shows +$150, tracking total spent at Woolworths
- Your ACTUAL credit card shows the transaction

**Purpose:** You can now see your AMEX balance AND how much you've spent at Woolworths across all time.

---

### Example 2: Receiving Salary

**What happens in real life:**
- Your employer pays you $5,000
- Your CommBank Everyday Savings balance increases by $5,000

**What Firefly III records:**

```
Transaction Type: Deposit (income)
Date: 2025-10-08
Amount: $5,000.00
Description: Salary SAI GLOBAL PAYRO 006064

FROM (Source):     Salary (revenue account - VIRTUAL) → tracks income source
TO (Destination):  CommBank Everyday Savings (asset account) → receives money
```

**What you see:**
- **CommBank Everyday Savings:** Shows +$5,000 deposit, balance increases
- **Salary Revenue Account:** Shows -$5,000, tracking total salary received
- Your ACTUAL bank account shows the deposit

**Purpose:** You can see your bank balance AND total salary received this year for tax reporting.

---

### Example 3: Paying Credit Card from Savings

**What happens in real life:**
- You transfer $3,000 from savings to pay AMEX
- Savings decreases by $3,000
- AMEX debt decreases by $3,000

**What Firefly III records:**

```
Transaction Type: Transfer (between your own accounts)
Date: 2025-10-08
Amount: $3,000.00
Description: Credit Card Payment

FROM (Source):     CommBank Everyday Savings (asset account) → loses $3,000
TO (Destination):  AMEX Credit Card (liability account) → debt reduces by $3,000
```

**What you see:**
- **CommBank Everyday Savings:** Shows -$3,000 withdrawal
- **AMEX Account:** Shows +$3,000 payment, debt decreases
- **NO expense or revenue account** because money stayed within YOUR accounts

**Purpose:** Tracks money movement between your accounts without counting it as spending or income.

---

### Example 4: Loan Repayment Coming TO You

**What happens in real life:**
- Someone repays a loan they owed you: $714
- Your CommBank Everyday Offset receives $714

**What Firefly III records:**

```
Transaction Type: Deposit (income)
Date: 2025-01-03
Amount: $714.00
Description: Loan Repayment LN REPAY 695943637

FROM (Source):     Loan Repayment (revenue account - VIRTUAL) → tracks repayment
TO (Destination):  CommBank Everyday Offset (asset account) → receives money
```

**What you see:**
- **CommBank Everyday Offset:** Shows +$714 deposit
- **Loan Repayment Revenue Account:** Tracks total loan repayments received

---

## Transaction Types Summary

### Withdrawal (Expense)
- **Money leaves** your asset/liability accounts
- **Goes to** an expense account (merchant/store)
- **Examples:** Buying groceries, paying bills, fuel purchases

```
Asset/Liability → Expense Account
```

### Deposit (Income)
- **Money enters** your asset/liability accounts
- **Comes from** a revenue account (income source)
- **Examples:** Salary, interest, refunds, loan repayments to you

```
Revenue Account → Asset/Liability
```

### Transfer
- **Money moves** between YOUR OWN accounts
- **No expense/revenue** involved
- **Examples:** Moving savings between banks, paying credit cards, loan payments

```
Asset/Liability → Asset/Liability
```

---

## Why This System Is Powerful

### 1. Complete Financial Picture
You can see:
- Your actual bank/credit card balances (asset/liability accounts)
- Where you spent money (expense accounts)
- Where money came from (revenue accounts)

### 2. Cross-Account Analysis
Questions you can answer:
- "How much did I spend at Woolworths **across all my cards**?" → Check Woolworths expense account
- "What's my total grocery spending?" → Sum Woolworths + Coles + Aldi expense accounts
- "How much salary did I receive this year?" → Check Salary revenue account
- "Which credit card has the most debt?" → Compare liability accounts

### 3. Budgeting and Reports
- Set budgets per expense account (e.g., $800/month for groceries)
- Track spending by merchant over time
- Generate tax reports showing total income by source
- See spending trends and patterns

---

## How Our Import System Works

### What the PDF Upload Does

When you upload a bank statement PDF:

1. **Parses transactions** from the PDF
2. **Identifies your account** (e.g., AMEX Credit Card, CommBank Everyday)
3. **Normalizes merchant names** (e.g., "WOOLWORTHS 1234 BELCONNEN AUS" → "Woolworths")
4. **Creates transactions** in Firefly III
5. **Auto-creates expense/revenue accounts** as needed

### Merchant Name Normalization

**Before normalization (OLD - created 800+ accounts):**
- "WOOLWORTHS 1234 BELCONNEN AUS" → separate expense account
- "WOOLWORTHS 5678 GUNGAHLIN AUS Card xx1234" → another separate expense account
- "WOOLWORTHS 1234 BELCONNEN AUS Value Date: 01/01/2025" → yet another account

**After normalization (NEW - creates 1 account):**
- All variations → "Woolworths" expense account

This happens automatically for known merchants:
- Woolworths, Coles, Bunnings, IKEA, Target, Kmart
- McDonalds, KFC, Subway, Guzman Y Gomez
- Chemist Warehouse, Wilson Parking
- American Express (for AMEX payments)
- And many more...

For unknown merchants, the system extracts the first 2-3 words as the merchant name.

### Account Type Detection

The import system automatically detects account types:

**Asset Accounts (detected):**
- CommBank Everyday
- ING Savings
- ING Orange
- uBank accounts

**Liability Accounts (detected):**
- Credit cards: AMEX, MasterCard, Visa
- Home loans
- Personal loans

**Expense/Revenue Accounts:**
- Created automatically based on transaction descriptions
- Normalized to avoid duplicates

---

## Your Money Flow Example

Let's trace money through your accounts:

### Month Start
```
CommBank Everyday Savings: $10,000
AMEX Credit Card: $-5,000 (you owe $5,000)
```

### Transaction 1: Salary Received
```
Deposit: $6,000
From: "Salary" (revenue - virtual)
To: CommBank Everyday Savings (asset)

Result:
  CommBank Everyday Savings: $16,000 (+$6,000)
  Salary Revenue Account: $6,000 total tracked
```

### Transaction 2: Groceries on AMEX
```
Withdrawal: $200
From: AMEX Credit Card (liability)
To: "Woolworths" (expense - virtual)

Result:
  AMEX Credit Card: $-5,200 (debt increased by $200)
  Woolworths Expense Account: $200 spent tracked
```

### Transaction 3: Pay AMEX from Savings
```
Transfer: $3,000
From: CommBank Everyday Savings (asset)
To: AMEX Credit Card (liability)

Result:
  CommBank Everyday Savings: $13,000 (-$3,000)
  AMEX Credit Card: $-2,200 (debt decreased by $3,000)
  No expense/revenue (internal transfer)
```

### Month End Balances
```
CommBank Everyday Savings: $13,000
AMEX Credit Card: $-2,200

Spending Tracked:
  Woolworths: $200

Income Tracked:
  Salary: $6,000
```

---

## Benefits of This System

### For You Personally

1. **Track spending across all accounts**
   - See total Woolworths spending even when using different cards
   - Identify where most money goes

2. **Budget management**
   - Set monthly limits per expense category
   - Get alerts when approaching limits

3. **Tax reporting**
   - Total income by source (salary, interest, etc.)
   - Business expense tracking if needed

4. **Financial insights**
   - Spending trends over time
   - Compare months/years
   - See which merchant gets most of your money

### What You DON'T Need to Do

- ❌ Manually create expense accounts (Woolworths, Coles, etc.)
- ❌ Manually create revenue accounts (Salary, Interest, etc.)
- ❌ Manually categorize transactions
- ❌ Update multiple accounts when money moves

Firefly III handles all this automatically based on your transactions!

---

## Common Questions

### Q: Do I need to create expense accounts before importing?
**A:** No! They're created automatically when you upload statements.

### Q: Why do I see money "leaving" and "entering" virtual accounts?
**A:** It's just double-entry bookkeeping. Every transaction needs two sides. The virtual accounts track categories, not real balances.

### Q: Can I rename expense accounts after import?
**A:** Yes! You can merge similar accounts (e.g., combine "Woolworths" and "Woolworths Online" into one).

### Q: What if the merchant normalization gets it wrong?
**A:** You can edit transactions to change the expense account, or we can add more patterns to the normalization code.

### Q: Do expense/revenue accounts affect my real account balances?
**A:** No! Only asset and liability accounts show real balances. Expense/revenue accounts are just for tracking and reporting.

### Q: Can I see all transactions for a specific merchant?
**A:** Yes! Click on the expense account (e.g., "Woolworths") to see every transaction, regardless of which card or account you used.

---

## Next Steps After Cleanup

1. **Run cleanup script** to delete all existing transactions and accounts
2. **Re-upload statements** with new normalized code
3. **Review expense accounts** - you should see ~50-100 merchants instead of 3800+
4. **Check reports** - see spending breakdown by merchant
5. **Set up budgets** (optional) - limit spending per category

The system will now properly track your money flow with meaningful categorization!

---

## Technical Notes (For Reference)

### Transaction Direction Logic

**For Asset Accounts (Savings, Checking):**
- Negative amount = Withdrawal (expense) → money goes TO expense account
- Positive amount = Deposit (income) → money comes FROM revenue account

**For Liability Accounts (Credit Cards, Loans):**
- Positive amount = Payment (withdrawal) → reduces debt, money goes OUT
- Negative amount = Purchase (deposit) → increases debt, money comes IN

This might seem backwards for liabilities, but it's correct:
- Paying $100 to AMEX = withdrawal (you're spending from AMEX to pay it off)
- Buying $50 at Woolworths on AMEX = deposit to AMEX (increasing the debt)

### Merchant Normalization Rules

The code applies these transformations:
1. Remove card numbers (xx1234)
2. Remove location codes (store numbers like 1234, 5678)
3. Remove country codes (AUS, AU)
4. Remove transaction metadata (Value Date, Tap and Pay, etc.)
5. Match against known merchant patterns
6. Extract first 2-3 words if unknown
7. Capitalize properly

---

**Last Updated:** 2025-10-08
**Version:** 1.0
