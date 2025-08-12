# Loyiha Nomi

Bu loyiha Telegram botlarini (userbot va control bot) va rejalashtiruvchini o'z ichiga oladi.

## Docker orqali ishga tushirish

Loyihani ishga tushirish uchun kompyuteringizda Docker o'rnatilgan bo'lishi kerak.

1.  **`.env` faylini sozlash:**
    `.env.example` faylidan nusxa oling va uni `.env` deb nomlang.

    ```bash
    cp .env.example .env
    ```

    Keyin `.env` faylini ochib, o'zingizning maxfiy ma'lumotlaringizni (API_ID, BOT_TOKEN va h.k.) kiriting.

2.  **Loyihani ishga tushirish:**
    Quyidagi komandani ishga tushiring. Bu barcha servislarni (control-bot, userbot, scheduler) quradi va ishga tushiradi.

    ```bash
    docker-compose up --build
    ```

Loyihani to'xtatish uchun `Ctrl + C` tugmalarini bosing. Orqa fonda ishlatish uchun `-d` flagidan foydalaning:

```bash
docker-compose up --build -d
```
