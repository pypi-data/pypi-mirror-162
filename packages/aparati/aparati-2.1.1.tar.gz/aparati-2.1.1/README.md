[![Downloads](https://pepy.tech/badge/aparat-dl)](https://pepy.tech/project/aparat-dl) [![Downloads](https://pepy.tech/badge/aparat-dl/month)](https://pepy.tech/project/aparat-dl/month) [![Downloads](https://pepy.tech/badge/aparat-dl/week)](https://pepy.tech/project/aparat-dl/week)

## آپاراتی (aparati)

این برنامه آپاراتی (aparati) که گذشته به اسم aparat_dl شناخته میشد برنامه ای است برای دانلود از اپارت

نمای از برنامه رو درحال دانلود یک پلی لیست میبینید


![](Screenshot_20220807_223132.png)
<p>توضیحات نحوه ی کار با برنامه رو در این بخش
<a href="#here">
بخونید</a>
</p>

## نصب

برای نصب میتونید از دستور زیر استفاده کنید

```
pip3 install aparati
```

## اجرا

```
python -m aparati args link
```

را در shell سیستم خود وارد کنید (terminal , cmd, powershell)

<h2 dir = "auto" id="here"> این برنامه ۶ عمل برای شما انجام میده!</h2>

<p align="right">
دانلود کل پلی لیست  یا  رنج خاصی از پلی لیست(دانلود در پوشه ای هم نام پلی لیست) 
</br>
میتونید لینکاتون رو با معرفی یه فایل تکست به برنامه دانلود کنید 
</br>
وکلی کارای دیگه که تولیست زیر توضیح دادم 
<h2 align="right" >لیست دستورات</h2>
<p>

```
Options:
	-H : Helps you =)
	-R :list all available qualities
	        aparat_dl -R link
	-L : Download whole playlist
	        aparat_dl -L link
	-SL : Download videos by selection on a playlist
		aparat_dl  -SL startpoint endpoint link
	-F : grabs links from a txt file
		aprat_dl -F path/to/txt/file
	-LF: Downlaod playlist from a txt File
		aparat_dl -LF path/to/txt/file Note*:u can use -CR a long with it
       -CR : use with other flags first use -R to see the available resolutions
		aparat_dl -CR 1080p -F/-L/-SL/-LF


Notes:
	1.to download a single video use aparat dl link
	2.video /s will be downloaded as 720p by default !
	to change it use flag -R to choose
	the quality along with othe
```

<p align="right">
برای دیدن دستورات برنامه می‌تونید از کامند
</br>

```
aparat_dl  -H
```
