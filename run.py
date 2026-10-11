from app import create_app

app = create_app()


# Bu dosya doğrudan çalıştırıldığında geliştirme sunucusunu başlat.
# DEBUG ayarı, config.py dosyasındaki ortama göre belirlenir.
if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])



