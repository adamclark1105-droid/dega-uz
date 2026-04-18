from bot import get_app

if __name__ == "__main__":
    app = get_app()
    print("Bot ishga tushdi...")
    app.run_polling()