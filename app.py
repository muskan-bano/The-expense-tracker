def answer_finance_question(user_id, question):
    """Enhanced financial assistant with expanded question handling"""
    import re
    from difflib import get_close_matches
    from datetime import datetime, timedelta

    df = get_transactions(user_id)
    if df.empty:
        return "No data available yet. Add some income and expenses first."

    question = question.lower()
    
    # Expanded keywords and patterns
    keywords = {
        'expense': ['expense', 'spent', 'spending', 'cost'],
        'income': ['income', 'earn', 'earning', 'salary', 'received'],
        'saving': ['save', 'saving', 'savings'],
        'budget': ['budget', 'limit', 'allocation'],
        'trend': ['trend', 'pattern', 'history'],
        'category': ['category', 'type', 'group'],
        'time': ['month', 'year', 'week', 'today', 'yesterday'],
        'comparison': ['compare', 'difference', 'versus', 'vs'],
        'advice': ['should', 'recommend', 'suggestion', 'advice', 'help']
    }

    # Helper function to check if any keyword from a category is in the question
    def contains_keyword(category):
        return any(word in question for word in keywords[category])

    # Time-based filtering
    today = datetime.now()
    if 'today' in question:
        df = df[df['date'].dt.date == today.date()]
    elif 'yesterday' in question:
        df = df[df['date'].dt.date == (today - timedelta(days=1)).date()]
    elif 'this month' in question:
        df = df[df['date'].dt.month == today.month]
    elif 'this year' in question:
        df = df[df['date'].dt.year == today.year]

    # Handle different types of questions
    if contains_keyword('expense') and contains_keyword('category'):
        expense_df = df[df['type'] == 'expense']
        if expense_df.empty:
            return "No expense records found for the specified period."
        by_category = expense_df.groupby('category')['amount'].sum().sort_values(ascending=False)
        return f"Expense breakdown by category:\n" + "\n".join([f"- {cat}: Rs{amt:.2f}" for cat, amt in by_category.items()])

    if "average" in question and contains_keyword('expense'):
        expense_df = df[df['type'] == 'expense']
        if expense_df.empty:
            return "No expense records found for the specified period."
        avg = expense_df['amount'].mean()
        return f"Your average expense is Rs{avg:.2f}"

    if contains_keyword('trend'):
        monthly_data = df.groupby([df['date'].dt.strftime('%Y-%m'), 'type'])['amount'].sum().unstack()
        if monthly_data.empty:
            return "Not enough data to analyze trends."
        latest_month = monthly_data.index[-1]
        return f"In {latest_month}, you had:\nIncome: Rs{monthly_data.loc[latest_month, 'income']:.2f}\nExpenses: Rs{monthly_data.loc[latest_month, 'expense']:.2f}"

    if contains_keyword('advice'):
        total_income = df[df['type'] == 'income']['amount'].sum()
        total_expenses = df[df['type'] == 'expense']['amount'].sum()
        ratio = total_expenses / total_income if total_income > 0 else 0
        
        if ratio > 0.8:
            return "⚠️ Your expenses are quite high relative to income. Consider:\n- Reviewing non-essential expenses\n- Setting a stricter budget\n- Looking for additional income sources"
        elif ratio > 0.5:
            return "👍 Your spending is moderate. To improve:\n- Start an emergency fund\n- Consider investing spare money\n- Look for areas to reduce expenses"
        else:
            return "✨ Great job managing your finances! Consider:\n- Investing your savings\n- Setting long-term financial goals\n- Building an emergency fund"

    # Original keyword-based responses
    if re.search(r"save.*month", question):
        return "Try using the 50/30/20 rule: Allocate 20% of your income to savings. Reduce discretionary expenses."

    if "biggest expense" in question:
        expense_df = df[df['type'] == 'expense']
        if expense_df.empty:
            return "You have not recorded any expenses yet."
        top = expense_df.groupby('category')['amount'].sum().sort_values(ascending=False).head(1)
        return f"Your biggest expense is in category: {top.index[0]} (Rs{top.values[0]:.2f})"

    if contains_keyword('income'):
        total_income = df[df['type'] == 'income']['amount'].sum()
        return f"Your total income is Rs{total_income:.2f}"

    if "balance" in question or "left" in question:
        income = df[df['type'] == 'income']['amount'].sum()
        expense = df[df['type'] == 'expense']['amount'].sum()
        return f"Your balance is Rs{income - expense:.2f}"

    # If no specific pattern is matched, provide a help message
    return ("I can help you with:\n"
            "- Expense analysis by category\n"
            "- Income and balance information\n"
            "- Spending trends and patterns\n"
            "- Financial advice and recommendations\n"
            "- Budget tracking and suggestions\n"
            "Try asking specific questions about these topics!")
