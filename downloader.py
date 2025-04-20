import os
import re
import time
import shutil
from pytube import YouTube, Playlist
from pytube.exceptions import RegexMatchError, VideoUnavailable


import yt_dlp

def temizle_dosya_adi(dosya_adi):

    if not dosya_adi:
        return "video"
    return re.sub(r'[\\/*?:"<>|]', "", dosya_adi)

def on_progress_callback(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = bytes_downloaded / total_size * 100
    print(f"\rİndiriliyor... %{percentage:.1f} tamamlandı", end="")

def yt_dlp_progress_hook(d):
    if d['status'] == 'downloading':
        if 'total_bytes' in d and d['total_bytes'] > 0:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            print(f"\rİndiriliyor... %{percent:.1f} tamamlandı", end="")
        else:
            print(f"\rİndiriliyor... {d['downloaded_bytes']/1024/1024:.1f} MB", end="")
    elif d['status'] == 'finished':
        print("\nİndirme tamamlandı, işleniyor...", end="")
        
def temizle_eski_dosyalar(dizin, uzanti=None):
    """İndirme sonrası gereksiz dosyaları temizle"""
    try:
        for dosya in os.listdir(dizin):
            dosya_yolu = os.path.join(dizin, dosya)
            if os.path.isfile(dosya_yolu):
                dosya_adi, dosya_uzantisi = os.path.splitext(dosya)
                if uzanti and dosya_uzantisi != uzanti:
                    # Belirtilen uzantı dışındakileri sil
                    os.remove(dosya_yolu)
    except Exception as e:
        print(f"Temizleme sırasında hata: {e}")

def youtube_video_indir_ytdlp(video_url, format_tipi, kalite):
    try:
        # Çıktı klasörü için bilgi topla
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_adi = temizle_dosya_adi(info.get('title', 'video'))
        
        print(f"\nVideo hazırlanıyor: {video_adi}")
        
        # Video için klasör oluştur
        dizin = os.path.join(os.getcwd(), video_adi)
        if not os.path.exists(dizin):
            os.makedirs(dizin)
            
        # Format ve kalite seçenekleri
        if format_tipi == "1":  # MP3
            if kalite == "1":  # Düşük kalite
                format_opt = "worstaudio/worst"
                bitrate = "128K"
            elif kalite == "2":  # Orta kalite
                format_opt = "bestaudio[ext!=webm]"
                bitrate = "192K"
            else:  # Yüksek kalite
                format_opt = "bestaudio"
                bitrate = "320K"
                
            ydl_opts = {
                'format': format_opt,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }],
                'outtmpl': os.path.join(dizin, '%(title)s.%(ext)s'),
                'progress_hooks': [yt_dlp_progress_hook],
                'quiet': False,
                'no_warnings': True
            }
            
        else:  # MP4
            if kalite == "1":  # Düşük kalite
                # Birleşik tek bir MP4 dosyası olarak indir
                format_opt = "worst[ext=mp4]/worst"
            elif kalite == "2":  # Orta kalite
                format_opt = "best[height<=480][ext=mp4]/best[ext=mp4]/mp4"
            else:  # Yüksek kalite
                format_opt = "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"
                
            ydl_opts = {
                'format': format_opt,
                'outtmpl': os.path.join(dizin, '%(title)s.%(ext)s'),
                'progress_hooks': [yt_dlp_progress_hook],
                'quiet': False,
                'no_warnings': True,
                'merge_output_format': 'mp4',
                # Birleştirici seçenekleri
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]
            }
        
        # İndirme işlemi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        # İstenmeyen dosyaları temizle (örn: m4a)
        if format_tipi == "2":  # MP4 için
            temizle_eski_dosyalar(dizin, uzanti=".mp4")
            
        print(f"\nİndirme tamamlandı! Dosya dizini: {dizin}")
        return True
        
    except Exception as e:
        print(f"\nHata oluştu: {e}")
        return False

def youtube_playlist_indir_ytdlp(playlist_url, format_tipi, kalite):
    try:
        # Playlist bilgilerini al
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'extract_flat': True}) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            playlist_adi = temizle_dosya_adi(info.get('title', 'Playlist'))
            entries = info.get('entries', [])
        
        print(f"Playlist: {playlist_adi}")
        print(f"Toplam video sayısı: {len(entries)}")
        
        # Playlist için klasör oluştur
        dizin = os.path.join(os.getcwd(), playlist_adi)
        if not os.path.exists(dizin):
            os.makedirs(dizin)
            
        # Format ve kalite seçenekleri
        if format_tipi == "1":  # MP3
            if kalite == "1":  # Düşük kalite
                format_opt = "worstaudio/worst"
                bitrate = "128K"
            elif kalite == "2":  # Orta kalite
                format_opt = "bestaudio[ext!=webm]"
                bitrate = "192K"
            else:  # Yüksek kalite
                format_opt = "bestaudio"
                bitrate = "320K"
                
            ydl_opts = {
                'format': format_opt,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }],
                'outtmpl': os.path.join(dizin, '%(title)s.%(ext)s'),
                'progress_hooks': [yt_dlp_progress_hook],
                'quiet': False,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
        else:  # MP4
            if kalite == "1":  # Düşük kalite
                format_opt = "worst[ext=mp4]/worst"
            elif kalite == "2":  # Orta kalite
                format_opt = "best[height<=480][ext=mp4]/best[ext=mp4]/mp4"
            else:  # Yüksek kalite
                format_opt = "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"
                
            ydl_opts = {
                'format': format_opt,
                'outtmpl': os.path.join(dizin, '%(title)s.%(ext)s'),
                'progress_hooks': [yt_dlp_progress_hook],
                'quiet': False,
                'no_warnings': True,
                'ignoreerrors': True,
                'merge_output_format': 'mp4',
                # Birleştirici seçenekleri
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]
            }
        
        # İndirme işlemi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        
        # İstenmeyen dosyaları temizle (örn: m4a)
        if format_tipi == "2":  # MP4 için
            temizle_eski_dosyalar(dizin, uzanti=".mp4")
            
        print(f"\nPlaylist indirme tamamlandı! Klasör: {dizin}")
        return True
        
    except Exception as e:
        print(f"\nPlaylist indirme hatası: {e}")
        return False

def youtube_video_indir(video_url, format_tipi, kalite, deneme_sayisi=3):
    # Önce yt-dlp ile indirmeyi dene
    try:
        print("yt-dlp kütüphanesi kullanılıyor...")
        return youtube_video_indir_ytdlp(video_url, format_tipi, kalite)
    except Exception as e:
        print(f"yt-dlp hatası: {e}. Pytube ile denenecek...")
    
    # Eğer yt-dlp başarısız olursa pytube ile dene (eski kod)
    for deneme in range(deneme_sayisi):
        try:
            yt = YouTube(video_url, on_progress_callback=on_progress_callback)
            video_adi = temizle_dosya_adi(yt.title)
            
            print(f"\nVideo hazırlanıyor: {video_adi}")
            
            # Video için klasör oluştur
            dizin = os.path.join(os.getcwd(), video_adi)
            if not os.path.exists(dizin):
                os.makedirs(dizin)
            
            if format_tipi == "1":  # MP3
                video = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                if not video:
                    print("Bu video için ses akışı bulunamadı.")
                    return False
                    
                video_yolu = video.download(output_path=dizin)
                
                # MP3 uzantısına çevir
                mp3_dosya = os.path.splitext(video_yolu)[0] + '.mp3'
                os.rename(video_yolu, mp3_dosya)
                print(f"\nİndirme tamamlandı! Dosya şurada: {mp3_dosya}")
                
            else:  # MP4
                # Tüm kullanılabilir çözünürlükleri göster
                streams = yt.streams.filter(progressive=True).order_by('resolution')
                if not streams or len(streams) == 0:
                    print("Bu video için akış bulunamadı.")
                    return False
                
                if kalite == "1":  # Düşük kalite
                    video = streams.first()
                elif kalite == "2":  # Orta kalite
                    video = streams.all()[len(streams)//2] if len(streams) > 1 else streams.first()
                else:  # Yüksek kalite
                    video = streams.desc().first()
                
                video_yolu = video.download(output_path=dizin)
                print(f"\nİndirme tamamlandı! Dosya şurada: {video_yolu}")
                
            return True
        except (RegexMatchError, VideoUnavailable) as e:
            print(f"Video erişilebilir değil: {e}")
            return False
        except Exception as e:
            print(f"Hata oluştu ({deneme+1}/{deneme_sayisi}): {e}")
            if deneme < deneme_sayisi - 1:
                print(f"5 saniye bekleyip yeniden denenecek...")
                time.sleep(5)
            else:
                print("Maksimum deneme sayısına ulaşıldı.")
                return False
    return False

def youtube_playlist_indir(playlist_url, format_tipi, kalite):
    # Önce yt-dlp ile indirmeyi dene
    try:
        print("yt-dlp kütüphanesi kullanılıyor...")
        return youtube_playlist_indir_ytdlp(playlist_url, format_tipi, kalite)
    except Exception as e:
        print(f"yt-dlp hatası: {e}. Pytube ile denenecek...")
    
    # Eğer yt-dlp başarısız olursa pytube ile dene (eski kod)
    try:
        pl = Playlist(playlist_url)
        # YouTube sınırı nedeniyle başlık alamayabilir
        try:
            playlist_adi = temizle_dosya_adi(pl.title)
        except:
            # Başlık alınamazsa, URL'den bir ad oluştur
            playlist_adi = "Playlist_" + playlist_url.split("list=")[1]
        
        print(f"Playlist: {playlist_adi}")
        print(f"Toplam video sayısı: {len(pl.video_urls)}")
        
        # Playlist için klasör oluştur
        dizin = os.path.join(os.getcwd(), playlist_adi)
        if not os.path.exists(dizin):
            os.makedirs(dizin)
        
        basari_sayaci = 0
        hata_sayaci = 0
        
        for index, video_url in enumerate(pl.video_urls):
            print(f"\n[{index+1}/{len(pl.video_urls)}] Sıradaki video işleniyor...")
            try:
                # Her istek arasında kısa bekletme
                if index > 0:
                    time.sleep(2)
                    
                yt = YouTube(video_url, on_progress_callback=on_progress_callback)
                video_adi = temizle_dosya_adi(yt.title)
                print(f"İndiriliyor: {video_adi}")
                
                if format_tipi == "1":  # MP3
                    video = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                    if not video:
                        print("Bu video için ses akışı bulunamadı.")
                        hata_sayaci += 1
                        continue
                        
                    video_yolu = video.download(output_path=dizin)
                    
                    # MP3 uzantısına çevir
                    mp3_dosya = os.path.splitext(video_yolu)[0] + '.mp3'
                    os.rename(video_yolu, mp3_dosya)
                    
                else:  # MP4
                    streams = yt.streams.filter(progressive=True).order_by('resolution')
                    if not streams or len(streams) == 0:
                        print("Bu video için akış bulunamadı.")
                        hata_sayaci += 1
                        continue
                    
                    if kalite == "1":  # Düşük kalite
                        video = streams.first()
                    elif kalite == "2":  # Orta kalite
                        video = streams.all()[len(streams)//2] if len(streams) > 1 else streams.first()
                    else:  # Yüksek kalite
                        video = streams.desc().first()
                    
                    video.download(output_path=dizin)
                
                basari_sayaci += 1
                print(f"\nVideo başarıyla indirildi: {video_adi}")
                
            except (RegexMatchError, VideoUnavailable) as e:
                print(f"Video erişilebilir değil: {e}")
                hata_sayaci += 1
            except Exception as e:
                print(f"Video indirilemedi: {video_url} - Hata: {e}")
                hata_sayaci += 1
                # Hata durumunda bekletme
                time.sleep(5)
        
        print(f"\nPlaylist indirme tamamlandı!")
        print(f"Başarılı: {basari_sayaci} video")
        print(f"Başarısız: {hata_sayaci} video")
        print(f"Klasör: {dizin}")
        
        return True
    except Exception as e:
        print(f"Playlist indirme hatası: {e}")
        return False

def main():
    print("YouTube İndirici Programı")
    print("-------------------------")
    
    while True:
        print("\nNe indirmek istiyorsunuz?")
        print("1 - Youtube Tek Video")
        print("2 - Youtube Playlist")
        print("3 - Çıkış")
        
        secim = input("Seçiminizi yapın (1-3): ")
        
        if secim == "3":
            print("Programdan çıkılıyor...")
            break
        
        if secim not in ["1", "2"]:
            print("Geçersiz seçim! Lütfen tekrar deneyin.")
            continue
        
        # Format tipi seçimi
        print("\nHangi formatta indirmek istiyorsunuz?")
        print("1 - MP3 (Sadece ses)")
        print("2 - MP4 (Video)")
        
        format_tipi = input("Seçiminizi yapın (1-2): ")
        
        if format_tipi not in ["1", "2"]:
            print("Geçersiz format seçimi! Lütfen tekrar başlayın.")
            continue
        
        # Kalite seçimi
        if format_tipi == "1":  # MP3
            print("\nSes kalitesi seçin:")
            print("1 - Düşük Kalite")
            print("2 - Orta Kalite")
            print("3 - Yüksek Kalite")
        else:  # MP4
            print("\nVideo kalitesi seçin:")
            print("1 - Düşük Kalite")
            print("2 - Orta Kalite")
            print("3 - Yüksek Kalite")
        
        kalite = input("Seçiminizi yapın (1-3): ")
        
        if kalite not in ["1", "2", "3"]:
            print("Geçersiz kalite seçimi! Lütfen tekrar başlayın.")
            continue
        
        # URL alınması
        if secim == "1":  # Tek video
            url = input("\nYouTube video URL'sini girin: ")
            print("\nVideo indiriliyor, lütfen bekleyin...")
            youtube_video_indir(url, format_tipi, kalite)
        else:  # Playlist
            url = input("\nYouTube playlist URL'sini girin: ")
            print("\nPlaylist indiriliyor, lütfen bekleyin...")
            youtube_playlist_indir(url, format_tipi, kalite)

if __name__ == "__main__":
    main()
