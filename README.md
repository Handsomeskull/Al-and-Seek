# Al-and-Seek
Ai learns to play hide and seek.


AI and Seek: Pekiştirmeli Öğrenme ile Saklambaç Simülasyonu

[Oyunun bir turundan ekran görüntüsü]

Bu proje, Q-learning algoritmasını kullanarak yapay zeka ajanlarının (bir ebe ve iki saklanan) zamanla akıllı stratejiler geliştirdiği bir saklambaç (hide-and-seek) simülasyonudur. Ajanlar, deneme-yanılma yoluyla çevrelerini ve diğer ajanların davranışlarını öğrenerek hayatta kalma ve hedef başarma şanslarını en üst düzeye çıkarmayı hedefler.

Simülasyon Nasıl Çalışır?

Simülasyon, ajanların karmaşık davranışlar sergilemesini sağlayan birkaç temel mekanizma üzerine kurulmuştur:

Oyun Ortamı: Ajanlar, rastgele oluşturulmuş duvarlarla dolu 16x16'lık bir grid dünyasında hareket eder. Bu duvarlar, hem ebe hem de saklananlar için stratejik siper ve engel görevi görür.

Öğrenme Algoritması (Q-Learning): Projenin kalbinde, model-free bir pekiştirmeli öğrenme tekniği olan Q-learning bulunur. Her ajan, belirli bir durumda hangi eylemin en iyi sonucu vereceğini tahmin etmesini sağlayan kendi Q-tablosunu (beynini) tutar.

Gelişmiş Ödül Sistemi (Reward Shaping): Ajanların öğrenmesini hızlandırmak için sadece büyük olaylar (yakalanma/yakalama) değil, aynı zamanda attıkları her küçük adım ödüllendirilir veya cezalandırılır:

Ebe (Seeker): Saklananlara görüş hattı açıkken yaklaştığında ödül, uzaklaştığında ceza alır.

Saklananlar (Hiders): Ebeden gerçek yol mesafesiyle uzaklaştığında ödül, yaklaştığında ceza alır. Duvar arkasına stratejik olarak saklandığında (ebe yakın ve görüş hattı kapalıyken) ekstra bonus kazanır.

Akıllı Algılama: Ajanların dünyayı daha doğru algılaması için gelişmiş algoritmalar kullanılır:

BFS (Genişlik Öncelikli Arama) Mesafesi: Ajanlar arasındaki mesafeyi, duvarları hesaba katarak en kısa gerçek yürüyüş yoluna göre hesaplar.

Bresenham Görüş Hattı (LOS): İki ajan arasında bir duvar olup olmadığını piksel hassasiyetinde kontrol ederek ödüllerin adil verilmesini sağlar.

Özellikler

Grafiksel Mod: Ajanların öğrenme sürecini ve geliştirdikleri stratejileri canlı olarak izleyin.

Headless Eğitim Modu: Görsel arayüz olmadan, işlemcinizin tüm çekirdeklerini paralel olarak kullanarak on binlerce turu saniyeler içinde simüle edin ve ajanlarınızı hızla eğitin.

Stratejik Yapay Zeka: Yeterince eğitildiğinde, ajanların sadece rastgele hareket etmek yerine duvarları siper olarak kullandığını, ebenin köşeye sıkıştırma taktikleri geliştirdiğini ve saklananların en güvenli kaçış yollarını bulduğunu gözlemleyin.

Nasıl Çalıştırılır?

Gereksinimleri Yükleyin:

pip install pygame numpy


Simülasyonu Başlatın:

python ai_and_seek.py


Mod Seçin: Program size Grafiksel Mod veya Hızlı Eğitim Modu seçeneklerini sunacaktır. Hızlı eğitim ile başlayıp ardından eğitilmiş ajanların performansını izlemeniz tavsiye edilir.

Gelecek Geliştirmeler ve Katkıda Bulunma

Bu proje, pekiştirmeli öğrenme dünyasına harika bir giriş noktasıdır ve birçok yönde geliştirilebilir. Katkıda bulunmak isterseniz, aşağıdaki fikirleri değerlendirebilirsiniz:

Daha Fazla Ajan: Ortama daha fazla ebe veya saklanan ekleyerek dinamikleri daha karmaşık hale getirme.

Farklı Algoritmalar: DQN (Deep Q-Networks) gibi daha gelişmiş öğrenme algoritmalarını entegre etme.

Dinamik Haritalar: Her turda değişen veya hareketli engeller içeren haritalar oluşturma.

Eğitimi Kaydetme/Yükleme: Ajanların öğrendiği Q-tablolarını (beyinlerini) bir dosyaya kaydedip daha sonra tekrar yükleyerek eğitime kaldığı yerden devam etme.

Kullanıcı Kontrolü: Bir ajanın kontrolünü kullanıcıya vererek eğitilmiş yapay zekaya karşı oynama imkanı.

Tüm katkı ve önerilere açığız! Bir "issue" açabilir veya "pull request" gönderebilirsiniz.

Teşekkürler

Bu projeyi incelediğiniz, kullandığınız veya katkıda bulunduğunuz için teşekkür ederiz. Umarız pekiştirmeli öğrenmenin temellerini anlamak için eğlenceli ve öğretici bir kaynak olur.
