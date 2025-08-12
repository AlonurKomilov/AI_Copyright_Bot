# Loyihani Serverga Joylashtirish Qo'llanmasi

Ushbu qo'llanma loyihani noldan boshlab Ubuntu serveriga o'rnatish va ishga tushirish uchun to'liq, qadamma-qadam ko'rsatmalarni o'z ichiga oladi.

## 1. Serverni tayyorlash

Ushbu bo'limda biz serverni loyihani ishga tushirish uchun tayyorlaymiz.

### 1.1. Serverga ulanish

Avvalo, sizning serveringizga SSH orqali ulanishingiz kerak. Terminalda quyidagi komandani kiriting (`your_username` o'rniga o'z foydalanuvchi nomingizni va `your_server_ip` o'rniga server IP manzilini yozing):

```bash
ssh your_username@your_server_ip
```

### 1.2. Paketlarni yangilash

Serverga kirgandan so'ng, tizim paketlarini eng so'nggi versiyaga yangilash tavsiya etiladi.

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3. Docker va Docker Compose'ni o'rnatish

Loyihamiz Docker yordamida ishlaydi. Quyidagi komandalar Docker va Docker Compose'ni serverga o'rnatadi.

**Docker'ni o'rnatish:**

```bash
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce -y
```

**Docker Compose'ni o'rnatish:**

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

O'rnatish muvaffaqiyatli bo'lganini tekshirish uchun:

```bash
docker --version
docker-compose --version
```

## 2. Loyihani sozlash

Endi server tayyor, loyihani yuklab olamiz va sozlaymiz.

### 2.1. Loyihani yuklab olish

Loyihaning GitHub omboridan nusxasini serverga yuklab olamiz.

```bash
git clone https://github.com/your-repo-link/project-name.git
```
*Izoh: `https://github.com/your-repo-link/project-name.git` o'rniga o'zingizning loyiha havolangizni qo'ying.*

### 2.2. Loyiha papkasiga o'tish

Yuklab olingan papkaga o'tamiz.

```bash
cd project-name
```
*Izoh: `project-name` o'rniga loyiha papkangiz nomini yozing.*

### 2.3. `.env` faylini yaratish va sozlash

Loyihaning asosiy sozlamalari `.env` faylida saqlanadi. `.env.example` faylidan nusxa olib, yangi `.env` faylini yaratamiz.

```bash
cp .env.example .env
```

Endi `.env` faylini matn muharriri (masalan, `nano`) orqali ochib, kerakli o'zgaruvchilarni to'ldiramiz.

```bash
nano .env
```

Fayl ichida quyidagi kabi o'zgaruvchilarni o'zingizning ma'lumotlaringiz bilan almashtiring:
- `API_ID` va `API_HASH`: my.telegram.org saytidan olinadi.
- `BOT_TOKEN`: @BotFather orqali olingan bot tokeni.
- `ADMIN_ID`: Sizning Telegram ID raqamingiz.
- Boshqa kerakli o'zgaruvchilar...

O'zgarishlarni saqlash uchun `Ctrl + X`, keyin `Y` va `Enter` tugmalarini bosing.

## 3. Userbot sessiyasini yaratish

Userbotning to'g'ri ishlashi uchun unga `.session` fayli kerak. Bu faylni birinchi marta ishga tushirganda generatsiya qilishimiz kerak.

Quyidagi komandani ishga tushiring:

```bash
docker-compose run --rm userbot
```

Shundan so'ng terminalda sizdan telefon raqamingizni, keyin esa Telegram orqali kelgan tasdiqlash kodini kiritish so'raladi. Bularni kiritganingizdan so'ng, loyiha papkasida `userbot.session` nomli fayl paydo bo'ladi.

## 4. Dasturni ishga tushirish va boshqarish

Barcha sozlamalar tayyor. Endi dasturni ishga tushirishimiz mumkin.

### 4.1. Dasturni ishga tushirish

Dasturni fon rejimida (detached mode) ishga tushirish uchun quyidagi komandadan foydalaning. `--build` flugi o'zgarishlar bo'lsa, Docker obrazlarini qayta quradi.

```bash
docker-compose up -d --build
```

### 4.2. Dastur loglarini ko'rish

Dasturning ishlash jarayonini va loglarni kuzatish uchun:

```bash
docker-compose logs -f
```

Loglarni ko'rishdan chiqish uchun `Ctrl + C` tugmasini bosing.

### 4.3. Dasturni to'xtatish

Dasturni to'liq to'xtatish va konteynerlarni o'chirish uchun:

```bash
docker-compose down
```
