# bot.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from services.stock_data import get_stock_data
from services.analysis_engine import analyze_stock
from services.structured_report import generate_structured_report

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your actual bot token
TELEGRAM_BOT_TOKEN = '7844949436:AAGuSSKfIaxojLMCcoWT2gigrq7ofv06zyQ'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    await update.message.reply_text(
        "👋 Welcome! Send me a valid stock symbol (e.g., TCS) and I'll provide a detailed technical analysis report."
    )

async def handle_stock_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages as stock symbol queries."""
    stock_name = update.message.text.strip().upper()
    logger.info("Received query for stock symbol: %s", stock_name)

    # Fetch OHLCV data for the requested stock
    data = get_stock_data(stock_name)
    # Properly check if DataFrame is empty or None
    if data is None or data.empty:
        await update.message.reply_text(
            f"❌ Error: Could not fetch data for symbol '{stock_name}'. Please verify the symbol and try again."
        )
        return

    # Analyze the fetched data (using data only)
    try:
        analysis = analyze_stock(data)
    except Exception as e:
        logger.error("Error analyzing %s: %s", stock_name, e)
        await update.message.reply_text(
            f"⚠️ Error analyzing '{stock_name}': {e}"
        )
        return

    # Generate the structured report
    report_text = generate_structured_report(stock_name, analysis)
    await update.message.reply_text(report_text)


def main() -> None:
    # Build and run the Telegram bot application
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stock_query))

    logger.info("✅ Bot is up and running...")
    app.run_polling()


if __name__ == '__main__':
    main()
