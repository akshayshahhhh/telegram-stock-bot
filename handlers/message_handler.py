# stock_bot_project/handlers/message_handler.py

import logging

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from services.stock_data import get_stock_data
from services.analysis_engine import analyze_stock
from services.structured_report import generate_structured_report

logger = logging.getLogger(__name__)

async def handle_stock_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Takes incoming text as a stock symbol,
    fetches data, runs analysis, and replies with the structured report.
    """
    symbol = update.message.text.strip().upper()
    try:
        # 1) Show “typing…” indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )

        # 2) Fetch OHLCV data
        data = get_stock_data(symbol)

        # 3) Properly check for missing/empty DataFrame
        if data is None or (hasattr(data, "empty") and data.empty):
            await update.message.reply_text(
                f"⚠️ No data found for symbol *{symbol}*",
                parse_mode="Markdown"
            )
            return

        # 4) Run your analysis engine
        analysis = analyze_stock(data)

        # 5) Generate the formatted report
        report = generate_structured_report(symbol, analysis)

        # 6) Send it back to the user
        await update.message.reply_text(
            report,
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.exception("Error in handle_stock_query")
        await update.message.reply_text(f"❌ Error: {e}")
